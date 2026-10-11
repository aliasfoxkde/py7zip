"""Tests for the safe-by-default public wrapper."""

from __future__ import annotations

import socket

import pytest

from py7zip.py7zip import Py7zip
from py7zip.safe import ArchiveResult, ArchiveRunner


class RecordingSafe:
    """Stand-in for ``SafePy7zip`` that records the operation it is handed."""

    def __init__(self):
        self.calls = []

    def run(self, operation, source, destination, options=()):
        self.calls.append((operation, source, destination, tuple(options)))
        return ArchiveResult(command=(), returncode=0, stdout="", stderr="")


def test_default_constructor_is_offline_and_does_not_download(monkeypatch, tmp_path):
    def fail_network(*_args, **_kwargs):
        raise AssertionError("default construction attempted network access")

    monkeypatch.setattr(socket, "getaddrinfo", fail_network)
    wrapper = Py7zip(cache_dir=tmp_path)

    assert wrapper.legacy is False
    assert wrapper.binary_path is None
    assert wrapper.__version__ == "0.7.3"
    assert list(tmp_path.iterdir()) == []


def test_default_aliases_require_individual_option_arguments(tmp_path):
    wrapper = Py7zip(binary_path=tmp_path / "missing")

    with pytest.raises(TypeError, match="sequence"):
        wrapper.compress("source", "destination", options="-y")


def test_default_runtime_accepts_individual_option_arguments(tmp_path, monkeypatch):
    """The sequence form reaches the safe runtime element by element."""
    wrapper = Py7zip(cache_dir=tmp_path)
    recording = RecordingSafe()
    monkeypatch.setattr(wrapper, "_safe", recording)

    result = wrapper.compress("src", "dst.7z", options=["-y", "-mx=9"])

    assert recording.calls == [("compress", "src", "dst.7z", ("-y", "-mx=9"))]
    assert result is not None
    assert result.success


def test_default_runtime_shell_text_never_reaches_parsing_or_execution(
    tmp_path, monkeypatch
):
    """A non-empty options string raises TypeError before anything runs.

    Audit decision D5 / OVH-16 keeps ``TypeError`` for string options on the
    safe path: there is no ``shlex.split`` bridge, so the documented failure
    for shell text is ``TypeError`` — never ``shlex``'s undocumented failure
    modes, i.e. the silent POSIX-mode corruption of unquoted Windows
    backslashes (``"-oC:\\Temp"`` would lose its separator) or the
    ``ValueError`` raised on an unbalanced quote.
    """
    monkeypatch.setattr(
        ArchiveRunner,
        "_invoke",
        lambda self, command: pytest.fail("a subprocess was started", pytrace=False),
    )
    wrapper = Py7zip(binary_path=tmp_path / "missing")

    with pytest.raises(TypeError, match="sequence"):
        wrapper.decompress("src.7z", "out", options="-oC:\\Temp")
    with pytest.raises(TypeError, match="sequence"):
        wrapper.decompress("src.7z", "out", options="-p'unbalanced")


def test_default_runtime_empty_string_options_are_empty_arguments(
    tmp_path, monkeypatch
):
    """The documented ``options = ""`` default forwards no arguments."""
    wrapper = Py7zip(cache_dir=tmp_path)
    recording = RecordingSafe()
    monkeypatch.setattr(wrapper, "_safe", recording)

    wrapper.extract("src.7z", "out")

    assert recording.calls == [("decompress", "src.7z", "out", ())]


def test_get_binary_url_raises_on_safe_runtime(tmp_path):
    """The safe runtime exposes acquisition, not download URLs.

    Per the F2 finding in the platform-architecture audit, the safe
    runtime previously returned a fabricated cache-relative path that
    did not correspond to any real download. Acquisition is now
    explicit via the public ``download_binary()`` entry point; this
    method raises a typed error pointing callers at that API rather
    than the internal ``SafePy7zip.ensure_binary()``.
    """
    wrapper = Py7zip(cache_dir=tmp_path)

    with pytest.raises(NotImplementedError) as excinfo:
        wrapper.get_binary_url()

    message = str(excinfo.value)
    assert "download_binary()" in message
    assert "ensure_binary" not in message


def test_legacy_mode_is_explicit():
    assert "legacy" in Py7zip.__init__.__code__.co_varnames
    assert ArchiveRunner is not None
