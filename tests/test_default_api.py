"""Tests for the safe-by-default public wrapper."""

from __future__ import annotations

import socket

import pytest

import py7zip.safe as safe_module
from py7zip.py7zip import Py7zip
from py7zip.safe import ArchiveResult, ArchiveRunner, ArchiveTraversalError


class RecordingSafe:
    """Stand-in for ``SafePy7zip`` that records the operation it is handed.

    Only the operation-level entry points the safe wrapper dispatches to
    are defined: a regression back to a direct ``SafePy7zip.run`` dispatch
    fails loudly here instead of silently bypassing member validation.
    """

    def __init__(self):
        self.calls = []

    def _record(self, operation, source, destination, options=()):
        self.calls.append((operation, source, destination, tuple(options)))
        return ArchiveResult(command=(), returncode=0, stdout="", stderr="")

    def compress(self, source, destination, options=()):
        return self._record("compress", source, destination, options)

    def decompress(self, source, destination, options=()):
        return self._record("decompress", source, destination, options)


def traversal_listing(member):
    """Build the ``l -slt -ba`` output a 7-Zip listing would print."""
    return f"Path = {member}\n"


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


@pytest.mark.parametrize(
    "member",
    [
        "../evil.txt",
        "a/../../evil.txt",
        "/abs/evil.txt",
        "C:/evil.txt",
    ],
)
def test_default_wrapper_rejects_traversal_members_before_extraction(
    tmp_path, monkeypatch, member
):
    """The public safe wrapper extracts only through member validation.

    Regression: ``Py7zip.wrapper`` dispatched the safe runtime through
    ``SafePy7zip.run``, bypassing the ``SafePy7zip.decompress`` guard, so
    the public ``decompress``/``extract`` entry points could write a
    member outside the destination root.  The wrapper must route
    decompression through the validating path: the archive is listed, a
    traversal member raises ``ArchiveTraversalError``, and no extraction
    command is ever started.
    """
    commands = []

    def fake_run(command, **kwargs):
        commands.append(tuple(command))
        return safe_module.subprocess.CompletedProcess(
            command, 0, stdout=traversal_listing(member), stderr=""
        )

    monkeypatch.setattr(safe_module.subprocess, "run", fake_run)
    wrapper = Py7zip(binary_path=tmp_path / "7za")

    with pytest.raises(ArchiveTraversalError, match="unsafe archive member"):
        wrapper.extract("archive.7z", tmp_path / "out")

    assert commands == [(str(tmp_path / "7za"), "l", "-slt", "-ba", "archive.7z")]


def test_default_wrapper_extracts_after_members_validate(tmp_path, monkeypatch):
    """A clean member list proceeds to the plain ``x`` extraction argv."""
    commands = []

    def fake_run(command, **kwargs):
        commands.append(tuple(command))
        return safe_module.subprocess.CompletedProcess(
            command, 0, stdout=traversal_listing("data/file.txt"), stderr=""
        )

    monkeypatch.setattr(safe_module.subprocess, "run", fake_run)
    wrapper = Py7zip(binary_path=tmp_path / "7za")

    result = wrapper.decompress("archive.7z", tmp_path / "out")

    assert result is not None
    assert result.success
    assert commands == [
        (str(tmp_path / "7za"), "l", "-slt", "-ba", "archive.7z"),
        (str(tmp_path / "7za"), "x", "archive.7z", f"-o{tmp_path / 'out'}"),
    ]


def test_default_wrapper_compress_never_lists_or_validates_members(
    tmp_path, monkeypatch
):
    """Compression packs local paths directly — no archive listing runs.

    Member validation is a decompression-side property; the compress
    command must stay the plain ``a`` invocation with the caller's argv.
    """
    commands = []

    def fake_run(command, **kwargs):
        commands.append(tuple(command))
        return safe_module.subprocess.CompletedProcess(
            command, 0, stdout="", stderr=""
        )

    monkeypatch.setattr(safe_module.subprocess, "run", fake_run)
    wrapper = Py7zip(binary_path=tmp_path / "7za")

    result = wrapper.compress("src dir", "dst.7z", options=["-y"])

    assert result is not None
    assert result.success
    assert commands == [(str(tmp_path / "7za"), "a", "dst.7z", "src dir", "-y")]


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
