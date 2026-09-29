"""Characterisation of binary acquisition as it exists today.

``setup()`` runs from ``__init__`` and calls ``download_binary()`` whenever
the expected file is missing from the package directory.  The download is
unauthenticated, unverified and unbounded: whatever bytes come back are
written straight to disk and marked executable.

The offline boundary used here is a real ``file://`` transfer through
``urllib.request``, so file creation and permission behaviour is observed
against an actual transport rather than a stub.  Network-style failures are
exercised through the ``urllib`` seam.  ``py7zip.__file__`` is redirected for
every test in this module so nothing is ever written into the source tree.
"""

from __future__ import annotations

import stat
import urllib.error

import py7zip.py7zip as py7zip_module
from tests.fakes import FakeUrllibRequest

import pytest

FAKE_BINARY = b"#!/bin/sh\nprintf 'characterization 7za\\n'\n"


@pytest.fixture
def staged_package_dir(tmp_path, monkeypatch):
    """Point the wrapper at a throwaway package directory."""
    package_dir = tmp_path / "site-packages" / "py7zip"
    package_dir.mkdir(parents=True)
    monkeypatch.setattr(
        py7zip_module, "__file__", str(package_dir / "py7zip.py")
    )
    return package_dir


def test_setup_skips_the_download_when_the_binary_already_exists(
    make_wrapper, staged_package_dir, monkeypatch
):
    calls = []
    monkeypatch.setattr(
        py7zip_module.Py7zip,
        "download_binary",
        lambda self: calls.append(self.binary_path),
    )

    make_wrapper(binary_present=True)

    assert calls == []
    assert not (staged_package_dir / "7za").exists()


def test_setup_downloads_when_the_binary_is_absent(
    make_wrapper, staged_package_dir, monkeypatch
):
    """A missing binary is fetched as a side effect of construction."""
    transport = FakeUrllibRequest(payload=FAKE_BINARY).install(monkeypatch)

    wrapper = make_wrapper(binary_present=False)

    installed = staged_package_dir / "7za"
    assert transport.opened == [wrapper.url]
    assert installed.read_bytes() == FAKE_BINARY


def test_setup_downloads_the_windows_suffix_on_windows(
    make_wrapper, staged_package_dir, monkeypatch
):
    transport = FakeUrllibRequest(payload=FAKE_BINARY).install(monkeypatch)

    wrapper = make_wrapper(
        binary_present=False,
        system="Windows",
        machine="AMD64",
        architecture=("64bit", "WindowsPE"),
    )

    installed = staged_package_dir / "7za.exe"
    assert transport.opened == [wrapper.url]
    assert installed.exists()
    assert installed.name == "7za.exe"


def test_download_binary_writes_and_marks_executable(
    make_wrapper, staged_package_dir, tmp_path
):
    wrapper = make_wrapper()
    source = tmp_path / "upstream-7za"
    source.write_bytes(FAKE_BINARY)
    wrapper.binary_path = str(staged_package_dir / "7za")
    wrapper.url = source.as_uri()

    wrapper.download_binary()

    installed = staged_package_dir / "7za"
    assert installed.read_bytes() == FAKE_BINARY
    assert stat.S_IMODE(installed.stat().st_mode) == 0o755


def test_download_binary_creates_missing_parent_directories(
    make_wrapper, tmp_path
):
    wrapper = make_wrapper()
    source = tmp_path / "upstream-7za"
    source.write_bytes(FAKE_BINARY)
    nested = tmp_path / "a" / "b" / "c" / "7za"
    wrapper.binary_path = str(nested)
    wrapper.url = source.as_uri()

    assert not nested.parent.exists()

    wrapper.download_binary()

    assert nested.read_bytes() == FAKE_BINARY


def test_download_binary_writes_whatever_it_receives_unbounded(
    make_wrapper, staged_package_dir, tmp_path
):
    """There is no size cap and no content check; a payload is stored as-is."""
    wrapper = make_wrapper()
    payload = b"\x00" * 8192
    source = tmp_path / "upstream-7za"
    source.write_bytes(payload)
    wrapper.binary_path = str(staged_package_dir / "7za")
    wrapper.url = source.as_uri()

    wrapper.download_binary()

    assert (staged_package_dir / "7za").read_bytes() == payload


def test_download_binary_does_not_verify_what_it_wrote(
    make_wrapper, staged_package_dir, tmp_path
):
    """Garbage is accepted and made executable without any integrity check."""
    wrapper = make_wrapper()
    source = tmp_path / "upstream-7za"
    source.write_bytes(b"definitely not an executable")
    wrapper.binary_path = str(staged_package_dir / "7za")
    wrapper.url = source.as_uri()

    wrapper.download_binary()

    installed = staged_package_dir / "7za"
    assert installed.read_bytes() == b"definitely not an executable"
    assert stat.S_IMODE(installed.stat().st_mode) == 0o755


def test_setup_swallows_a_download_failure_and_prints_it(
    make_wrapper, staged_package_dir, monkeypatch, capsys
):
    """A failed download is printed and construction still succeeds."""
    FakeUrllibRequest(
        payload=urllib.error.URLError("characterization outage")
    ).install(monkeypatch)

    wrapper = make_wrapper(binary_present=False)

    assert wrapper is not None
    assert not (staged_package_dir / "7za").exists()
    assert "characterization outage" in capsys.readouterr().out


def test_setup_does_nothing_when_the_binary_is_present(
    make_wrapper, staged_package_dir, capsys
):
    wrapper = make_wrapper(binary_present=True)

    wrapper.setup()

    assert capsys.readouterr().out == ""
    assert not (staged_package_dir / "7za").exists()
