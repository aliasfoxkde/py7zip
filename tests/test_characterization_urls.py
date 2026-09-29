"""Characterisation of the binary URL and version-probe URLs as they exist today.

The wrapper builds both URLs by string interpolation against a mutable
``main`` branch.  These tests pin the exact strings so the Phase 2 catalog
redesign can prove that every URL it emits differs deliberately.
"""

from __future__ import annotations

import pytest

BASE_BINARY_URL = "https://github.com/aliasfoxkde/py7zip/raw/main/bin/"
RAW_USERCONTENT = "https://raw.githubusercontent.com"
CHANGELOG_URL = (
    "https://raw.githubusercontent.com/aliasfoxkde/py7zip/main/docs/CHANGELOG.md"
)


def test_base_binary_url_points_at_the_mutable_main_branch(make_wrapper):
    wrapper = make_wrapper()

    assert wrapper.base_bin_url == BASE_BINARY_URL
    assert "/raw/main/" in wrapper.base_bin_url


def test_raw_usercontent_host_is_recorded(make_wrapper):
    wrapper = make_wrapper()

    assert wrapper.raw_usercontent == RAW_USERCONTENT


def test_app_identity_is_hardcoded(make_wrapper):
    wrapper = make_wrapper()

    assert wrapper.username == "aliasfoxkde"
    assert wrapper.app_name == "py7zip"


def test_binary_url_contains_a_doubled_path_separator(make_wrapper):
    """The base URL ends in ``/`` and the template adds another."""
    wrapper = make_wrapper()

    assert wrapper.url == f"{BASE_BINARY_URL}/lin/pc/x64/7za"
    assert "//" in wrapper.url


@pytest.mark.parametrize(
    ("system", "machine", "architecture", "expected_url"),
    [
        (
            "Linux",
            "x86_64",
            ("64bit", "ELF"),
            f"{BASE_BINARY_URL}/lin/pc/x64/7za",
        ),
        (
            "Linux",
            "armv7l",
            ("32bit", "ELF"),
            f"{BASE_BINARY_URL}/lin/arm/x86/7za",
        ),
        (
            "Windows",
            "AMD64",
            ("64bit", "WindowsPE"),
            f"{BASE_BINARY_URL}/win/pc/x64/7za.exe",
        ),
        (
            "Darwin",
            "arm64",
            ("64bit", ""),
            f"{BASE_BINARY_URL}/mac/arm/x64/7za",
        ),
        (
            "Darwin",
            "x86_64",
            ("64bit", ""),
            f"{BASE_BINARY_URL}/mac/pc/x64/7za",
        ),
    ],
    ids=[
        "linux-x86-64",
        "linux-armv7l",
        "windows-x86-64",
        "macos-arm64",
        "macos-x86-64",
    ],
)
def test_binary_url_per_platform(
    system, machine, architecture, expected_url, make_wrapper
):
    wrapper = make_wrapper(
        system=system, machine=machine, architecture=architecture
    )

    assert wrapper.get_binary_url() == expected_url
    assert wrapper.url == expected_url


def test_version_probe_targets_the_changelog_on_main(make_wrapper):
    wrapper = make_wrapper()

    assert wrapper.raw_usercontent in CHANGELOG_URL
    assert wrapper._requests_fake.calls == [CHANGELOG_URL]
