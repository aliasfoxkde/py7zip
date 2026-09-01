"""Tests for the explicit safe runtime API."""

from __future__ import annotations

import subprocess

import pytest

import py7zip.safe as safe_module
from py7zip.safe import (
    ArchiveExecutionError,
    ArchiveRunner,
    ArchiveTimeoutError,
    SafePy7zip,
)


class Completed:
    returncode = 7
    stdout = "out"
    stderr = "err"


def test_runner_passes_an_argument_vector_without_shell(monkeypatch, tmp_path):
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return Completed()

    monkeypatch.setattr(safe_module.subprocess, "run", fake_run)
    result = ArchiveRunner(tmp_path / "7za", timeout=12).decompress if False else None
    result = ArchiveRunner(tmp_path / "7za", timeout=12).run(
        "decompress", "source;touch", "out dir", ["-y", "m0=on;touch"]
    )

    assert result.returncode == 7
    command, kwargs = calls[0]
    assert command == (
        str(tmp_path / "7za"),
        "x",
        "source;touch",
        "-oout dir",
        "-y",
        "m0=on;touch",
    )
    assert kwargs == {
        "capture_output": True,
        "text": True,
        "shell": False,
        "check": False,
        "timeout": 12,
    }


def test_runner_rejects_opaque_option_strings(tmp_path):
    with pytest.raises(TypeError, match="sequence"):
        ArchiveRunner(tmp_path / "7za").run("compress", "src", "dst", "-y")


def test_runner_wraps_missing_binary(tmp_path):
    with pytest.raises(ArchiveExecutionError, match="not found"):
        ArchiveRunner(tmp_path / "missing").run("compress", "src", "dst")


def test_runner_wraps_timeout(monkeypatch, tmp_path):
    def timeout(*_args, **_kwargs):
        raise subprocess.TimeoutExpired("7za", 1)

    monkeypatch.setattr(safe_module.subprocess, "run", timeout)

    with pytest.raises(ArchiveTimeoutError, match="exceeded"):
        ArchiveRunner(tmp_path / "7za", timeout=1).run("compress", "src", "dst")


def test_safe_construction_does_not_acquire_or_execute(tmp_path, monkeypatch):
    monkeypatch.setattr(safe_module.PlatformInfo, "detect", lambda: "detected")
    safe = SafePy7zip(cache_dir=tmp_path)

    assert safe.binary_path is None
    assert list(tmp_path.iterdir()) == []
