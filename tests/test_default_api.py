"""Tests for the safe-by-default public wrapper."""

from __future__ import annotations

import socket

import pytest

from py7zip.py7zip import Py7zip
from py7zip.safe import ArchiveRunner


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


def test_get_binary_url_raises_on_safe_runtime(tmp_path):
    """The safe runtime exposes acquisition, not download URLs.

    Per the F2 finding in the platform-architecture audit, the safe
    runtime previously returned a fabricated cache-relative path that
    did not correspond to any real download. Acquisition is now
    explicit via ``ensure_binary()``; this method raises a typed
    error pointing callers at the correct API.
    """
    wrapper = Py7zip(cache_dir=tmp_path)

    with pytest.raises(NotImplementedError, match="ensure_binary"):
        wrapper.get_binary_url()


def test_legacy_mode_is_explicit():
    assert "legacy" in Py7zip.__init__.__code__.co_varnames
    assert ArchiveRunner is not None
