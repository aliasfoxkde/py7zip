"""End-to-end archive operations against the repository's bundled 7-Zip.

These tests are the platform-qualification lane promised by AGENTS.md: they
run the real ``7za`` binary checked into ``bin/`` (no download), create and
extract real archives, and prove the backup-family semantics end to end.

The lane is host-gated: it runs only where the bundled artifact for the
detected platform exists and is executable.  Everything here stays offline;
the ``offline`` autouse fixture would fail any accidental network use.
"""

from __future__ import annotations

import time
import zipfile
from pathlib import Path

import pytest

from py7zip.py7zip import Py7zip
from py7zip.safe import ArchiveExecutionError, ArchiveResult, ArchiveTraversalError


def _write_tree(root: Path, files: dict[str, str]) -> None:
    for name, content in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def _read_tree(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): path.read_text(encoding="utf-8")
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


class TestCompressExtractRoundTrip:
    def test_compress_then_extract_reproduces_the_tree(self, safe, tmp_path):
        source = tmp_path / "src"
        _write_tree(source, {"a.txt": "alpha", "nested/b.txt": "beta"})

        result = safe.compress(source, tmp_path / "out.7z")
        assert isinstance(result, ArchiveResult)
        assert result.success
        assert (tmp_path / "out.7z").is_file()

        destination = tmp_path / "restored"
        safe.decompress(tmp_path / "out.7z", destination)
        # compressing a directory stores the directory itself
        assert _read_tree(destination / source.name) == _read_tree(source)

    def test_compat_api_roundtrip_and_verbose_message(
        self, bundled_binary, tmp_path, capsys
    ):
        wrapper = Py7zip(verbose=True, binary_path=bundled_binary, cache_dir=tmp_path)
        source = tmp_path / "src"
        _write_tree(source, {"only.txt": "payload"})

        wrapper.compress(source, tmp_path / "c.7z")
        assert "Backup created" in capsys.readouterr().out

        wrapper.decompress(tmp_path / "c.7z", tmp_path / "out")
        assert "Extracted archive" in capsys.readouterr().out
        # compressing a directory stores the directory itself
        assert (tmp_path / "out" / "src" / "only.txt").read_text(
            encoding="utf-8"
        ) == "payload"

    def test_compat_api_rejects_string_options(self, bundled_binary, tmp_path):
        wrapper = Py7zip(binary_path=bundled_binary, cache_dir=tmp_path)
        with pytest.raises(TypeError, match="sequence"):
            wrapper.compress(tmp_path, tmp_path / "x.7z", options="-y")

    def test_extraction_refuses_archive_members_escaping_the_root(
        self, bundled_binary, tmp_path
    ):
        """A real archive with a ``../`` member is refused before extraction."""
        trap = tmp_path / "trap.zip"
        with zipfile.ZipFile(trap, "w") as archive:
            archive.writestr("../pwned.txt", "escape attempt")

        wrapper = Py7zip(binary_path=bundled_binary, cache_dir=tmp_path)
        outside = tmp_path / "outside"
        outside.mkdir()

        with pytest.raises(ArchiveTraversalError, match="pwned"):
            wrapper.decompress(trap, outside)
        assert not (outside.parent / "pwned.txt").exists()
        assert list(outside.iterdir()) == []

    def test_extracting_a_missing_archive_raises_a_typed_error(
        self, bundled_binary, tmp_path
    ):
        wrapper = Py7zip(binary_path=bundled_binary, cache_dir=tmp_path)
        with pytest.raises(ArchiveExecutionError, match="could not list"):
            wrapper.decompress(tmp_path / "missing.7z", tmp_path / "out")


class TestBackupModes:
    def test_full_creates_a_fresh_complete_archive(self, safe, tmp_path):
        source = tmp_path / "src"
        _write_tree(source, {"a.txt": "v1"})

        safe.full(source, tmp_path / "full.7z")
        assert (tmp_path / "full.7z").is_file()

    def test_incremental_updates_newest_and_keeps_deletions(self, safe, tmp_path):
        source = tmp_path / "src"
        _write_tree(source, {"a.txt": "v1", "b.txt": "keep"})

        archive = tmp_path / "inc.7z"
        safe.incremental(source, archive)

        _write_tree(source, {"a.txt": "v2-changed", "new.txt": "added"})
        (source / "b.txt").unlink()
        time.sleep(1.2)  # ensure the modified file is strictly newer
        safe.incremental(source, archive)

        restored = tmp_path / "restored"
        safe.decompress(archive, restored)
        assert _read_tree(restored / source.name) == {
            "a.txt": "v2-changed",
            "b.txt": "keep",  # deletions are retained by design
            "new.txt": "added",
        }

    def test_differential_capture_and_restore_procedure(self, safe, tmp_path):
        source = tmp_path / "src"
        _write_tree(source, {"a.txt": "v1", "b.txt": "doomed"})

        base = tmp_path / "base.7z"
        safe.full(source, base)
        baseline_hash = base.read_bytes()

        time.sleep(1.2)
        _write_tree(source, {"a.txt": "v2-changed", "new.txt": "added"})
        (source / "b.txt").unlink()

        safe.differential(source, base)

        diff = tmp_path / "base.diff.7z"
        assert diff.is_file()
        assert base.read_bytes() == baseline_hash  # the base is never touched

        restore = tmp_path / "restore"
        safe.decompress(base, restore, options=("-y",))
        # overlaying the diff over the base needs overwrite enabled
        safe.decompress(diff, restore, options=("-y",))
        assert _read_tree(restore / source.name) == _read_tree(source)

    def test_differential_honors_an_explicit_diff_path(self, safe, tmp_path):
        source = tmp_path / "src"
        _write_tree(source, {"a.txt": "v1"})
        base = tmp_path / "base.7z"
        safe.full(source, base)

        custom = tmp_path / "custom-name.7z"
        safe.differential(source, base, diff_path=custom)
        assert custom.is_file()

    def test_differential_refuses_non_7z_diff_targets(self, safe, tmp_path):
        source = tmp_path / "src"
        _write_tree(source, {"a.txt": "v1"})
        base = tmp_path / "base.7z"
        safe.full(source, base)

        with pytest.raises(ValueError, match=r"\.7z"):
            safe.differential(source, base, diff_path=tmp_path / "diff.zip")

    def test_snapshot_writes_a_timestamped_archive_and_keeps_the_original(
        self, safe, tmp_path
    ):
        source = tmp_path / "src"
        _write_tree(source, {"a.txt": "point-in-time"})

        result = safe.snapshot(
            source, tmp_path / "snap/site.7z", timestamp="20260928T220000"
        )

        stamped = tmp_path / "snap" / "site.20260928T220000.7z"
        assert stamped.is_file()
        assert result.command[2] == str(stamped)
        assert not (tmp_path / "snap" / "site.7z").exists()

        restored = tmp_path / "restored"
        safe.decompress(stamped, restored)
        assert _read_tree(restored / source.name) == {"a.txt": "point-in-time"}

    def test_compat_backup_family_uses_the_same_runtime(self, bundled_binary, tmp_path):
        wrapper = Py7zip(binary_path=bundled_binary, cache_dir=tmp_path)
        source = tmp_path / "src"
        _write_tree(source, {"a.txt": "v1"})

        wrapper.full(source, tmp_path / "f.7z")
        wrapper.incremental(source, tmp_path / "f.7z")
        wrapper.snapshot(source, tmp_path / "s/site.7z", timestamp="20260928T220100")
        wrapper.differential(source, tmp_path / "f.7z")

        assert (tmp_path / "f.7z").is_file()
        assert (tmp_path / "s" / "site.20260928T220100.7z").is_file()
        assert (tmp_path / "f.diff.7z").is_file()
