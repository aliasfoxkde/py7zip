"""Shared fixtures for the offline py7zip characterization suite.

Every test here must pass on a machine with no network access and no 7-Zip
binary installed.  Rather than trusting that, the fixtures below enforce it:

``offline`` (autouse)
    Turns address resolution and socket connection into hard failures, so a
    regression that reintroduces a network call fails loudly instead of
    quietly depending on connectivity.

``clean_cwd``
    Restores the process working directory after each test, because the
    wrapper's ``cd`` helper mutates global interpreter state.

``package_tree_snapshot``
    Records the files under the installed ``py7zip`` package directory so
    tests can prove that importing or constructing the wrapper did not write
    a binary or any other artifact next to the source.
"""

from __future__ import annotations

import os
import socket
from pathlib import Path

import pytest

import py7zip.py7zip as py7zip_module
from tests import fakes

PACKAGE_DIR = Path(py7zip_module.__file__).resolve().parent
REPO_ROOT = PACKAGE_DIR.parent


def _deny_network(*_args, **_kwargs):
    raise AssertionError(
        "network access attempted during an offline test run; the py7zip "
        "suite must not resolve addresses or open sockets"
    )


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    """Fail any test that resolves a name or opens a network connection."""
    monkeypatch.setattr(socket, "create_connection", _deny_network)
    monkeypatch.setattr(socket, "getaddrinfo", _deny_network)
    monkeypatch.setattr(socket, "gethostbyname", _deny_network)
    monkeypatch.setattr(socket, "gethostbyaddr", _deny_network)
    monkeypatch.setattr(socket.socket, "connect", _deny_network)
    monkeypatch.setattr(socket.socket, "connect_ex", _deny_network)
    yield


@pytest.fixture
def clean_cwd(monkeypatch, tmp_path):
    """Run a test inside ``tmp_path`` and restore the real cwd afterwards."""
    original = Path.cwd()
    monkeypatch.chdir(tmp_path)
    yield tmp_path
    os.chdir(original)


@pytest.fixture
def package_tree_snapshot():
    """Return a callable that reports non-cache files added to the package."""
    before = _package_files()
    seen = []

    def added():
        return sorted(_package_files() - before)

    seen.append(added)
    yield added
    for path in added():
        path.unlink()


def _package_files():
    return {
        path
        for path in PACKAGE_DIR.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }


@pytest.fixture
def make_wrapper(monkeypatch):
    """Build a ``Py7zip`` against fake host data with side effects switched off.

    The filesystem seam answers "binary already present" by default, so the
    real ``setup()`` runs and skips the download, and the ``requests`` seam is
    replaced with a fake that fails the connection.  Tests that need the other
    behaviour opt in explicitly.
    """

    def factory(
        system="Linux",
        machine="x86_64",
        architecture=("64bit", "ELF"),
        binary_present=True,
        stub_setup=False,
        requests_responder=None,
    ):
        fakes.FakePlatform(
            monkeypatch,
            system=system,
            machine=machine,
            architecture=architecture,
        )
        if binary_present:
            fakes.FakeFileSystem(exists=True).install(monkeypatch)
        if stub_setup:
            monkeypatch.setattr(py7zip_module.Py7zip, "setup", lambda self: None)
        requests_fake = fakes.FakeRequests(responder=requests_responder).install(
            monkeypatch
        )
        wrapper = py7zip_module.Py7zip(legacy=True)
        wrapper._requests_fake = requests_fake
        return wrapper

    return factory
