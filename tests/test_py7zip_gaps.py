"""Branch coverage for the compatibility API's mode-specific paths.

Each test pins one deliberate behaviour of ``Py7zip`` that the
characterization and e2e suites only touch indirectly.
"""

from __future__ import annotations

import runpy
import subprocess
import warnings
from datetime import datetime
from pathlib import Path

import pytest

import py7zip.py7zip as py7zip_module
import py7zip.safe as safe_module
from py7zip.platforms import ArtifactCatalog
from py7zip.py7zip import Py7zip
from py7zip.safe import ArchiveExecutionError
from tests.fakes import make_response


def test_safe_get_version_reads_installed_metadata(tmp_path, monkeypatch):
    monkeypatch.setattr(py7zip_module, "package_version", lambda _name: "9.9.9")

    wrapper = Py7zip(cache_dir=tmp_path)

    assert wrapper.__version__ == "9.9.9"
    assert wrapper.get_version() == "9.9.9"


def test_legacy_version_probe_without_match_prints_when_verbose(make_wrapper, capsys):
    def no_version(_url):
        return make_response("# Changelog\n\n- nothing parseable here\n")

    wrapper = make_wrapper(requests_responder=no_version)
    assert wrapper.get_version(verbose=True) == "0.0.0"
    assert "Failed to retrieve the latest version" in capsys.readouterr().out


def test_safe_setup_is_an_explicit_noop(tmp_path):
    preset = tmp_path / "7za"
    preset.write_bytes(b"MZ")
    wrapper = Py7zip(binary_path=preset, cache_dir=tmp_path)

    wrapper.setup()  # must not touch the network or the filesystem
    assert list(tmp_path.iterdir()) == [preset]


def test_safe_download_binary_resolves_the_preset_path(tmp_path):
    preset = tmp_path / "7za"
    preset.write_bytes(b"MZ")
    wrapper = Py7zip(binary_path=preset, cache_dir=tmp_path / "cache")

    assert wrapper.download_binary() == preset
    assert wrapper.binary_path == preset


def test_safe_binary_url_points_at_the_cache_location(tmp_path):
    preset = tmp_path / "7za"
    preset.write_bytes(b"MZ")
    wrapper = Py7zip(binary_path=preset, cache_dir=tmp_path / "cache")

    expected_spec = ArtifactCatalog.resolve(wrapper.platform_info)
    assert wrapper.get_binary_url() == (
        f"{tmp_path / 'cache'}/{expected_spec.relative_path}"
    )


def test_safe_wrapper_debug_prints_binary_stdout(tmp_path, monkeypatch, capsys):
    def run_with_output(command, **_kwargs):
        return subprocess.CompletedProcess(command, 0, stdout="7-Zip banner", stderr="")

    monkeypatch.setattr(safe_module.subprocess, "run", run_with_output)
    preset = tmp_path / "7za"
    preset.write_bytes(b"MZ")
    wrapper = Py7zip(debug=True, binary_path=preset, cache_dir=tmp_path)

    wrapper.wrapper("src.7z", "out")
    assert "7-Zip banner" in capsys.readouterr().out


def test_safe_wrapper_verbose_reports_failures(tmp_path, monkeypatch, capsys):
    """A failed extract (not a failed listing) prints the error message."""

    def listing_ok_then_extract_fails(command, **_kwargs):
        if command[1] == "l":
            stdout = "Path = src/a.txt\n"
            return subprocess.CompletedProcess(command, 0, stdout=stdout, stderr="")
        return subprocess.CompletedProcess(command, 2, stdout="", stderr="bad")

    monkeypatch.setattr(safe_module.subprocess, "run", listing_ok_then_extract_fails)
    preset = tmp_path / "7za"
    preset.write_bytes(b"MZ")
    wrapper = Py7zip(verbose=True, binary_path=preset, cache_dir=tmp_path)

    result = wrapper.wrapper("src.7z", "out")
    assert result.success is False
    assert "Failed to extract archive" in capsys.readouterr().out


def test_normalize_options_maps_only_the_empty_default():
    assert Py7zip._normalize_options("") == ()
    assert Py7zip._normalize_options(None) == ()
    assert Py7zip._normalize_options(("-y", "-mx=9")) == ("-y", "-mx=9")
    opaque = "-y"
    assert Py7zip._normalize_options(opaque) is opaque


def test_legacy_backup_methods_require_7za_on_path(make_wrapper, monkeypatch):
    monkeypatch.setattr(py7zip_module.shutil, "which", lambda _name: None)

    wrapper = make_wrapper()
    with pytest.raises(ArchiveExecutionError, match="not found on PATH"):
        wrapper.full("src", "dst")
    with pytest.raises(ArchiveExecutionError, match="not found on PATH"):
        wrapper.snapshot("src", "dst")


def test_dunder_main_prints_import_guidance(capsys):
    """Executing the module as a script prints guidance, nothing else."""
    with warnings.catch_warnings():
        # runpy warns that the module is already imported via the package;
        # the guidance print itself is what this test pins.
        warnings.simplefilter("ignore", RuntimeWarning)
        runpy.run_module("py7zip.py7zip", run_name="__main__")

    assert "intended to be imported" in capsys.readouterr().out


def test_snapshot_defaults_to_the_live_timestamp(safe, tmp_path):
    """Without an explicit stamp the archive name carries the current time."""
    source = tmp_path / "src"
    (source / "nested").mkdir(parents=True)
    (source / "nested" / "a.txt").write_text("live", encoding="utf-8")

    result = safe.snapshot(source, tmp_path / "snap/live.7z")

    stamped = Path(result.command[2])
    assert stamped.is_file()
    today = datetime.now().strftime("%Y%m%dT")  # noqa: DTZ005 - mirrors runtime
    assert stamped.name.startswith(f"live.{today}")
