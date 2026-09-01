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


def test_legacy_mode_is_explicit():
    assert "legacy" in Py7zip.__init__.__code__.co_varnames
    assert ArchiveRunner is not None
