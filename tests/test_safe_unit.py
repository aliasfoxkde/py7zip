"""Unit coverage for the argv runtime, member validation and backup modes.

These tests never execute a process: the subprocess seam inside
``py7zip.safe`` is replaced with a recording fake, mirroring how the
characterization suite pins the legacy wrapper.
"""

from __future__ import annotations

import subprocess

import pytest

import py7zip.safe as safe_module
from py7zip.safe import (
    ArchiveExecutionError,
    ArchiveResult,
    ArchiveRunner,
    ArchiveTimeoutError,
    ArchiveTraversalError,
    SafePy7zip,
    validate_archive_members,
)


@pytest.fixture
def recording_run(monkeypatch):
    """Replace ``subprocess.run`` inside the safe runtime; return the log."""
    calls: list[tuple[tuple[str, ...], dict]] = []

    def run(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0, stdout="out", stderr="err")

    monkeypatch.setattr(safe_module.subprocess, "run", run)
    return calls


class TestArchiveRunnerGuards:
    def test_non_positive_timeout_is_rejected(self, tmp_path):
        with pytest.raises(ValueError, match="timeout"):
            ArchiveRunner(tmp_path / "7za", timeout=0)

    def test_unknown_operation_is_rejected(self, tmp_path):
        runner = ArchiveRunner(tmp_path / "7za")
        with pytest.raises(ValueError, match="operation"):
            runner.run("benchmark", "src", "dst")

    @pytest.mark.parametrize("argument", ["src", "dst", "options"])
    def test_nul_bytes_are_rejected_everywhere(self, tmp_path, recording_run, argument):
        runner = ArchiveRunner(tmp_path / "7za")
        values = {
            "src": ("bad\x00src", "dst", ()),
            "dst": ("src", "bad\x00dst", ()),
            "options": ("src", "dst", ("-y\x00",)),
        }
        with pytest.raises(ValueError, match="NUL"):
            runner.run("compress", *values[argument])
        assert recording_run == []

    def test_bytes_options_are_rejected(self, tmp_path):
        runner = ArchiveRunner(tmp_path / "7za")
        with pytest.raises(TypeError, match="sequence"):
            runner.run("compress", "src", "dst", b"-y")


class TestDifferentialDiffReplacement:
    """A pre-existing diff is replaced, never refused.

    7za rejects the switch-named archive when it exists (errno 17), so a
    re-run against the same base must clear the derived file first.
    """

    def test_existing_diff_is_removed_before_the_update(self, tmp_path, recording_run):
        preset = tmp_path / "7za"
        preset.write_bytes(b"MZ")
        stale = tmp_path / "base.diff.7z"
        stale.write_bytes(b"stale diff")

        manager = SafePy7zip(binary_path=preset)
        manager.differential("src", tmp_path / "base.7z")

        assert not stale.exists()
        assert recording_run[0][0][1:3] == ("u", str(tmp_path / "base.7z"))
        assert "-up0q3r2x2y2z0w2!" + str(stale) in recording_run[0][0]

    def test_absent_diff_leaves_the_disk_alone(self, tmp_path, recording_run):
        preset = tmp_path / "7za"
        preset.write_bytes(b"MZ")

        manager = SafePy7zip(binary_path=preset)
        manager.differential("src", tmp_path / "base.7z")

        assert len(recording_run) == 1  # the update ran; no pre-pass side trip


class TestListEntries:
    def test_members_are_parsed_from_technical_listing(self, tmp_path, monkeypatch):
        def run_with_listing(command, **_kwargs):
            stdout = "Path = archive.7z\nPath = \nPath = docs/readme.md\nSize = 12\n"
            return subprocess.CompletedProcess(command, 0, stdout=stdout, stderr="")

        monkeypatch.setattr(safe_module.subprocess, "run", run_with_listing)
        runner = ArchiveRunner(tmp_path / "7za")

        assert runner.list_entries("archive.7z") == ("archive.7z", "docs/readme.md")


def test_list_entries_raises_on_listing_failure(tmp_path, monkeypatch):
    def failing_run(command, **_kwargs):
        return subprocess.CompletedProcess(command, 2, stdout="", stderr="no such")

    monkeypatch.setattr(safe_module.subprocess, "run", failing_run)
    runner = ArchiveRunner(tmp_path / "7za")

    with pytest.raises(ArchiveExecutionError, match="could not list"):
        runner.list_entries("archive.7z")


def test_os_errors_become_typed_execution_errors(tmp_path, monkeypatch):
    def os_error_run(_command, **_kwargs):
        raise OSError(13, "permission denied")

    monkeypatch.setattr(safe_module.subprocess, "run", os_error_run)
    runner = ArchiveRunner(tmp_path / "7za")

    with pytest.raises(ArchiveExecutionError, match="failed to start"):
        runner.run("compress", "src", "dst")


def test_timeout_expiry_becomes_a_typed_timeout(tmp_path, monkeypatch):
    def timeout_run(_command, **_kwargs):
        raise subprocess.TimeoutExpired(cmd="7za", timeout=0.5)

    monkeypatch.setattr(safe_module.subprocess, "run", timeout_run)
    runner = ArchiveRunner(tmp_path / "7za", timeout=0.5)

    with pytest.raises(ArchiveTimeoutError, match="timeout"):
        runner.run("compress", "src", "dst")


class TestSafePy7zipExplicitBinary:
    def test_preset_binary_path_is_returned_without_acquisition(self, tmp_path):
        preset = tmp_path / "7za"
        preset.write_bytes(b"MZ")
        manager = SafePy7zip(binary_path=preset)

        assert manager.ensure_binary() == preset
        assert manager.binary_path == preset


class TestBackupModeConstruction:
    """The argv each backup mode builds, pinned at the runner boundary."""

    @pytest.fixture
    def runner(self, tmp_path, recording_run):
        return ArchiveRunner(tmp_path / "7za"), recording_run

    def test_full_builds_add_with_assume_yes(self, runner):
        archive_runner, calls = runner
        result = archive_runner.run("compress", "src", "dst.7z", ("-y", "-mx=9"))

        assert result.success
        assert calls[0][0] == (
            str(archive_runner.binary_path),
            "a",
            "dst.7z",
            "src",
            "-y",
            "-mx=9",
        )

    def test_incremental_builds_update(self, runner):
        archive_runner, calls = runner
        archive_runner.run("update", "src", "dst.7z", ("-y",))

        assert calls[0][0][1:4] == ("u", "dst.7z", "src")

    def test_decompress_builds_output_switch(self, runner):
        archive_runner, calls = runner
        archive_runner.run("decompress", "src.7z", "outdir")

        assert calls[0][0] == (
            str(archive_runner.binary_path),
            "x",
            "src.7z",
            "-ooutdir",
        )


def test_safe_compress_and_decompress_convenience(tmp_path, monkeypatch):
    preset = tmp_path / "7za"
    preset.write_bytes(b"MZ")
    safe = SafePy7zip(binary_path=preset, cache_dir=tmp_path / "cache")

    calls: list[tuple] = []

    def run(command, **_kwargs):
        calls.append(command)
        if command[1] == "l":
            stdout = "Path = a.txt\n"
            return subprocess.CompletedProcess(command, 0, stdout=stdout, stderr="")
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(safe_module.subprocess, "run", run)

    compress_result = safe.compress("src", "dst.7z", ("-y",))
    assert compress_result.command[1:4] == ("a", "dst.7z", "src")

    decompress_result = safe.decompress("src.7z", "out")
    assert decompress_result.command[1:4] == ("x", "src.7z", "-oout")


class TestValidationMatrix:
    @pytest.mark.parametrize(
        "member",
        [
            "/etc/passwd",
            "C:\\Windows\\evil",
            "\\\\server\\share\\evil",
            "../outside",
            "docs/../../outside",
            "a\\..\\..\\outside",
            "",
        ],
    )
    def test_rejects_unsafe_members(self, member, tmp_path):
        with pytest.raises(ArchiveTraversalError, match="unsafe archive member"):
            validate_archive_members([member], tmp_path)

    def test_accepts_deeply_nested_relative_members(self, tmp_path):
        validate_archive_members(["docs/subdir/readme.md", "images/logo.png"], tmp_path)


def test_archive_result_success_reflects_returncode():
    ok = ArchiveResult(
        command=("7za", "a", "d", "s"), returncode=0, stdout="", stderr=""
    )
    failed = ArchiveResult(
        command=("7za", "a", "d", "s"), returncode=2, stdout="", stderr="boom"
    )
    assert ok.success
    assert not failed.success


def test_ensure_binary_acquires_through_the_artifact_manager(tmp_path, monkeypatch):
    """Without a preset path, ensure_binary delegates to acquisition."""
    resolved = tmp_path / "cache" / "7za"
    constructed: dict = {}

    class StubManager:
        def __init__(self, cache_dir, timeout):
            constructed["cache_dir"] = cache_dir
            constructed["timeout"] = timeout

        def ensure(self, info):
            constructed["info"] = info
            return resolved

    monkeypatch.setattr(safe_module, "ArtifactManager", StubManager)
    manager = SafePy7zip(cache_dir=tmp_path / "cache", timeout=90.0)

    assert manager.ensure_binary() == resolved
    assert constructed["cache_dir"] == tmp_path / "cache"
    assert constructed["timeout"] == 30.0  # capped at the acquisition bound
    assert constructed["info"] is manager.platform_info
    assert manager.binary_path == resolved  # cached on the instance
