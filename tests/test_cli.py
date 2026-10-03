"""Offline behaviour and exit-code contract of the command-line interface.

Happy paths run the bundled 7-Zip for this host (no download, no shell);
failure paths inject typed errors so every exit code is pinned without
manufacturing real faults.
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

import pytest

import py7zip.cli as cli_module
from py7zip.acquisition import ArtifactIntegrityError
from py7zip.cli import main
from py7zip.platforms import UnsupportedPlatformError
from py7zip.safe import (
    ArchiveExecutionError,
    ArchiveTimeoutError,
    ArchiveTraversalError,
)


def _write_tree(root: Path) -> None:
    (root / "src" / "nested").mkdir(parents=True)
    (root / "src" / "a.txt").write_text("cli", encoding="utf-8")
    (root / "src" / "nested" / "b.txt").write_text("tree", encoding="utf-8")


class TestParserSurface:
    def test_help_names_every_subcommand(self, capsys):
        with pytest.raises(SystemExit) as exit_code:
            main(["--help"])
        assert exit_code.value.code == 0
        help_text = capsys.readouterr().out
        for command in (
            "download",
            "compress",
            "full",
            "incremental",
            "extract",
            "list",
            "differential",
            "snapshot",
        ):
            assert command in help_text

    def test_version_flag_prints_a_release_version(self, capsys):
        with pytest.raises(SystemExit) as exit_code:
            main(["--version"])
        assert exit_code.value.code == 0
        assert capsys.readouterr().out.count(".") == 2

    def test_missing_subcommand_is_a_usage_error(self, capsys):
        with pytest.raises(SystemExit) as exit_code:
            main([])
        assert exit_code.value.code == 2
        assert "command" in capsys.readouterr().err


class TestHappyPaths:
    def test_download_reports_the_resolved_binary(
        self, bundled_binary, tmp_path, capsys
    ):
        assert main(["download", "--binary-path", str(bundled_binary)]) == 0
        assert str(bundled_binary) in capsys.readouterr().out

    def test_compress_list_extract_roundtrip(self, bundled_binary, tmp_path, capsys):
        _write_tree(tmp_path)
        base = ["--binary-path", str(bundled_binary)]
        archive = tmp_path / "arc.7z"

        assert main(["compress", *base, str(tmp_path / "src"), str(archive)]) == 0
        assert f"created {archive}" in capsys.readouterr().out

        main(["list", *base, str(archive)])
        listing = capsys.readouterr().out
        assert "src/a.txt" in listing
        assert "src/nested/b.txt" in listing

        out = tmp_path / "out"
        assert main(["extract", *base, str(archive), str(out)]) == 0
        assert (out / "src" / "nested" / "b.txt").read_text(encoding="utf-8") == "tree"

    def test_full_and_incremental_drive_their_runtime_operations(
        self, bundled_binary, tmp_path, capsys
    ):
        _write_tree(tmp_path)
        base = ["--binary-path", str(bundled_binary)]
        archive = tmp_path / "inc.7z"

        assert main(["full", *base, str(tmp_path / "src"), str(archive)]) == 0
        assert f"created {archive}" in capsys.readouterr().out
        assert main(["incremental", *base, str(tmp_path / "src"), str(archive)]) == 0
        assert f"updated {archive}" in capsys.readouterr().out
        assert archive.is_file()

    def test_differential_defaults_to_a_sibling_diff(
        self, bundled_binary, tmp_path, capsys
    ):
        _write_tree(tmp_path)
        base = ["--binary-path", str(bundled_binary)]
        archive = tmp_path / "base.7z"
        main(["compress", *base, str(tmp_path / "src"), str(archive)])
        capsys.readouterr()

        assert main(["differential", *base, str(tmp_path / "src"), str(archive)]) == 0
        diff = tmp_path / "base.diff.7z"
        assert f"wrote {diff}" in capsys.readouterr().out
        assert diff.is_file()

    def test_differential_honours_an_explicit_diff_path(
        self, bundled_binary, tmp_path, capsys
    ):
        _write_tree(tmp_path)
        base = ["--binary-path", str(bundled_binary)]
        archive = tmp_path / "base.7z"
        main(["compress", *base, str(tmp_path / "src"), str(archive)])
        capsys.readouterr()

        diff = tmp_path / "elsewhere" / "named.7z"
        assert (
            main(
                [
                    "differential",
                    *base,
                    str(tmp_path / "src"),
                    str(archive),
                    "--diff-path",
                    str(diff),
                ]
            )
            == 0
        )
        assert diff.is_file()

    def test_snapshot_with_fixed_timestamp_writes_the_pinned_name(
        self, bundled_binary, tmp_path, capsys
    ):
        _write_tree(tmp_path)
        target = tmp_path / "snap.7z"
        assert (
            main(
                [
                    "snapshot",
                    "--binary-path",
                    str(bundled_binary),
                    "--timestamp",
                    "20261002T120000",
                    str(tmp_path / "src"),
                    str(target),
                ]
            )
            == 0
        )
        stamped = tmp_path / "snap.20261002T120000.7z"
        assert f"created {stamped}" in capsys.readouterr().out
        assert stamped.is_file()

    def test_snapshot_without_timestamp_reports_the_live_stamped_name(
        self, bundled_binary, tmp_path, capsys
    ):
        _write_tree(tmp_path)
        target = tmp_path / "live.7z"
        assert (
            main(
                [
                    "snapshot",
                    "--binary-path",
                    str(bundled_binary),
                    str(tmp_path / "src"),
                    str(target),
                ]
            )
            == 0
        )
        created = capsys.readouterr().out.removeprefix("created ").strip()
        assert Path(created).is_file()
        assert created != str(target)  # the stamp is part of the name


class TestExitCodeContract:
    def test_execution_failure_exits_1(self, monkeypatch, capsys):
        def fail(self, *_args, **_kwargs):
            raise ArchiveExecutionError("7-Zip exploded")

        monkeypatch.setattr(cli_module.SafePy7zip, "compress", fail)
        assert main(["compress", "src", "dest.7z"]) == 1
        assert "7-Zip exploded" in capsys.readouterr().err

    def test_acquisition_failure_exits_1(self, monkeypatch, capsys):
        class FailingRuntime:
            def __init__(self, **_kwargs):
                pass

            def ensure_binary(self):
                raise ArtifactIntegrityError("digest mismatch")

        monkeypatch.setattr(cli_module, "SafePy7zip", FailingRuntime)
        assert main(["download"]) == 1
        assert "digest mismatch" in capsys.readouterr().err

    def test_timeout_exits_3(self, monkeypatch, capsys):
        def slow(self, *_args, **_kwargs):
            raise ArchiveTimeoutError("killed after 300s")

        monkeypatch.setattr(cli_module.SafePy7zip, "compress", slow)
        assert main(["compress", "src", "dest.7z"]) == 3
        assert "timed out" in capsys.readouterr().err

    def test_zip_slip_refusal_exits_4(self, monkeypatch, capsys):
        def unsafe(self, *_args, **_kwargs):
            raise ArchiveTraversalError("member escapes the root")

        monkeypatch.setattr(cli_module.SafePy7zip, "decompress", unsafe)
        assert main(["extract", "evil.7z", "out"]) == 4
        assert "unsafe archive members" in capsys.readouterr().err

    def test_unsupported_platform_exits_5(self, monkeypatch, capsys):
        class RefusingRuntime:
            def __init__(self, **_kwargs):
                pass

            def ensure_binary(self):
                raise UnsupportedPlatformError("no artifact for this host")

        monkeypatch.setattr(cli_module, "SafePy7zip", RefusingRuntime)
        assert main(["download"]) == 5
        assert "unsupported platform" in capsys.readouterr().err

    def test_non_7z_diff_target_is_a_usage_error(
        self, bundled_binary, tmp_path, capsys
    ):
        _write_tree(tmp_path)
        base = ["--binary-path", str(bundled_binary)]
        archive = tmp_path / "base.7z"
        main(["compress", *base, str(tmp_path / "src"), str(archive)])
        capsys.readouterr()

        assert (
            main(
                [
                    "differential",
                    *base,
                    str(tmp_path / "src"),
                    str(archive),
                    "--diff-path",
                    str(tmp_path / "bad.zip"),
                ]
            )
            == 2
        )
        assert ".7z" in capsys.readouterr().err


class TestVerbatimSwitches:
    """Switches after ``--`` reach 7-Zip untouched.

    Every 7-Zip switch starts with ``-``, so they cannot follow a
    value-taking flag; the verbatim tail is the contract instead.
    """

    def test_switches_after_the_terminator_reach_the_runtime(self, monkeypatch):
        seen = {}

        class CapturingRuntime:
            def __init__(self, **_kwargs):
                pass

            def decompress(self, archive, destination, options=()):
                seen["call"] = (archive, destination, tuple(options))

        monkeypatch.setattr(cli_module, "SafePy7zip", CapturingRuntime)
        assert main(["extract", "arc.7z", "out", "--", "-y", "-mmt=4"]) == 0
        assert seen["call"] == ("arc.7z", "out", ("-y", "-mmt=4"))

    def test_overwrite_extract_repeats_without_a_prompt(
        self, bundled_binary, tmp_path, capsys
    ):
        """The documented two-step differential restore: extract twice into
        the same tree with ``-y``, which 7-Zip only accepts after ``--``."""
        _write_tree(tmp_path)
        base = ["--binary-path", str(bundled_binary)]
        archive = tmp_path / "base.7z"
        assert main(["compress", *base, str(tmp_path / "src"), str(archive)]) == 0
        capsys.readouterr()
        out = tmp_path / "out"

        assert main(["extract", *base, str(archive), str(out), "--", "-y"]) == 0
        assert main(["extract", *base, str(archive), str(out), "--", "-y"]) == 0
        assert (out / "src" / "a.txt").read_text(encoding="utf-8") == "cli"

    def test_the_first_terminator_ends_py7zip_parsing(self, monkeypatch):
        seen = {}

        class CapturingRuntime:
            def __init__(self, **_kwargs):
                pass

            def compress(self, source, destination, options=()):
                seen["options"] = tuple(options)

        monkeypatch.setattr(cli_module, "SafePy7zip", CapturingRuntime)
        assert main(["compress", "src", "arc.7z", "--", "-y", "--", "-mx=9"]) == 0
        assert seen["options"] == ("-y", "--", "-mx=9")


def test_python_dash_m_entrypoint_runs_the_cli(monkeypatch, capsys):
    """``python -m py7zip`` dispatches into the same parser."""
    monkeypatch.setattr(sys, "argv", ["py7zip", "--version"])
    with pytest.raises(SystemExit) as exit_code:
        runpy.run_module("py7zip", run_name="__main__")
    assert exit_code.value.code == 0
    assert capsys.readouterr().out.count(".") == 2
