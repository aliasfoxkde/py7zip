"""Characterisation of host detection as it exists today.

These tests pin the platform, architecture and binary-path behaviour of
``Py7zip.__init__`` before any redesign, including the combinations that
silently produce the wrong answer or the wrong exception type.  They are the
baseline the Phase 2 ``PlatformInfo`` redesign has to be measured against.
"""

from __future__ import annotations

import os

import pytest

import py7zip.py7zip as py7zip_module
from tests import fakes

#: (label, platform kwargs, sys_type, arch_type, sys_platform, extension)
#: The URL suffix keeps the doubled slash the current f-string produces.
RESOLVED_HOSTS = [
    (
        "linux x86-64",
        dict(system="Linux", machine="x86_64", architecture=("64bit", "ELF")),
        dict(
            sys_type="pc",
            arch_type="x64",
            sys_platform="lin",
            extension="",
            url_suffix="bin//lin/pc/x64/7za",
            binary_name="7za",
        ),
    ),
    (
        "linux armv7l 32-bit",
        dict(system="Linux", machine="armv7l", architecture=("32bit", "ELF")),
        dict(
            sys_type="arm",
            arch_type="x86",
            sys_platform="lin",
            extension="",
            url_suffix="bin//lin/arm/x86/7za",
            binary_name="7za",
        ),
    ),
    (
        "windows x86-64",
        dict(
            system="Windows",
            machine="AMD64",
            architecture=("64bit", "WindowsPE"),
        ),
        dict(
            sys_type="pc",
            arch_type="x64",
            sys_platform="win",
            extension=".exe",
            url_suffix="bin//win/pc/x64/7za.exe",
            binary_name="7za.exe",
        ),
    ),
    (
        "macos x86-64",
        dict(system="Darwin", machine="x86_64", architecture=("64bit", "")),
        dict(
            sys_type="pc",
            arch_type="x64",
            sys_platform="mac",
            extension="",
            url_suffix="bin//mac/pc/x64/7za",
            binary_name="7za",
        ),
    ),
    (
        "macos arm64",
        dict(system="Darwin", machine="arm64", architecture=("64bit", "")),
        dict(
            sys_type="arm",
            arch_type="x64",
            sys_platform="mac",
            extension="",
            url_suffix="bin//mac/arm/x64/7za",
            binary_name="7za",
        ),
    ),
]

#: Combinations the code cannot classify.  Each entry records the exception
#: the wrapper raises today so a later redesign that widens or narrows the
#: matrix does so deliberately rather than by accident.
REJECTED_HOSTS = [
    (
        "linux aarch64 is not matched because 'arm' is not a substring",
        dict(system="Linux", machine="aarch64", architecture=("64bit", "ELF")),
        NotImplementedError,
    ),
    (
        "linux i686 32-bit has a shipped binary but no classifier",
        dict(system="Linux", machine="i686", architecture=("32bit", "ELF")),
        NotImplementedError,
    ),
    (
        "windows arm64 machine name is matched case-sensitively",
        dict(
            system="Windows",
            machine="ARM64",
            architecture=("64bit", "WindowsPE"),
        ),
        NotImplementedError,
    ),
    (
        "linux riscv64 is unclassified",
        dict(system="Linux", machine="riscv64", architecture=("64bit", "ELF")),
        NotImplementedError,
    ),
    (
        "linux ppc64le is unclassified",
        dict(system="Linux", machine="ppc64le", architecture=("64bit", "ELF")),
        NotImplementedError,
    ),
]

#: An operating system outside the hard-coded list reaches the architecture
#: lookup first and dies on ``sys_platform`` with ``KeyError`` rather than the
#: ``NotImplementedError`` the wrapper documents for this case.
WRONG_EXCEPTION_HOSTS = [
    (
        "unsupported operating system raises KeyError, not NotImplementedError",
        dict(system="SunOS", machine="x86_64", architecture=("64bit", "ELF")),
        KeyError,
        "sunos",
    ),
    (
        "unrecognised pointer width raises KeyError",
        dict(system="Linux", machine="x86_64", architecture=("128bit", "ELF")),
        KeyError,
        "128bit",
    ),
]


@pytest.mark.parametrize(
    ("label", "kwargs", "expected"),
    RESOLVED_HOSTS,
    ids=[entry[0] for entry in RESOLVED_HOSTS],
)
def test_host_is_classified(label, kwargs, expected, make_wrapper):
    wrapper = make_wrapper(**kwargs)

    assert wrapper.sys_type == expected["sys_type"]
    assert wrapper.arch_type == expected["arch_type"]
    assert wrapper.sys_platform == expected["sys_platform"]
    assert wrapper.extension == expected["extension"]
    assert wrapper.url.endswith(expected["url_suffix"])
    assert os.path.basename(wrapper.binary_path) == expected["binary_name"]


@pytest.mark.parametrize(
    ("label", "kwargs", "exception"),
    REJECTED_HOSTS,
    ids=[entry[0] for entry in REJECTED_HOSTS],
)
def test_unclassified_machine_is_refused(label, kwargs, exception, make_wrapper):
    with pytest.raises(exception) as excinfo:
        make_wrapper(**kwargs)

    assert "No machine type could be detected" in str(excinfo.value)


@pytest.mark.parametrize(
    ("label", "kwargs", "exception", "missing_key"),
    WRONG_EXCEPTION_HOSTS,
    ids=[entry[0] for entry in WRONG_EXCEPTION_HOSTS],
)
def test_unsupported_host_surfaces_as_keyerror(label, kwargs, exception, missing_key, make_wrapper):
    with pytest.raises(exception) as excinfo:
        make_wrapper(**kwargs)

    assert excinfo.value.args[0] == missing_key


def test_supported_platform_list_is_hardcoded(make_wrapper):
    wrapper = make_wrapper()

    assert wrapper.supported == ["windows", "linux", "darwin"]


def test_platform_attribute_is_the_lowercased_system_name(make_wrapper):
    wrapper = make_wrapper(system="Linux")

    assert wrapper.platform == "linux"


def test_debug_info_records_the_supplied_host_facts(make_wrapper):
    wrapper = make_wrapper(system="Linux", machine="x86_64")

    assert wrapper.debug_info.system == "Linux"
    assert wrapper.debug_info.machine == "x86_64"


def test_binary_path_lives_beside_the_package_module(make_wrapper):
    wrapper = make_wrapper()

    expected = os.path.join(
        os.path.dirname(py7zip_module.__file__),
        "7za",
    )
    assert wrapper.binary_path == expected


def test_windows_binary_path_carries_the_executable_suffix(make_wrapper):
    wrapper = make_wrapper(
        system="Windows", machine="AMD64", architecture=("64bit", "WindowsPE")
    )

    assert wrapper.binary_path.endswith("7za.exe")


def test_get_binary_url_refuses_an_unsupported_platform(make_wrapper):
    wrapper = make_wrapper()
    wrapper.platform = "sunos"

    with pytest.raises(NotImplementedError) as excinfo:
        wrapper.get_binary_url()

    assert "Platform 'sunos' is not supported." in str(excinfo.value)


@pytest.mark.parametrize(
    "system",
    ["windows", "linux", "darwin"],
)
def test_get_binary_url_accepts_every_listed_platform(system, make_wrapper):
    wrapper = make_wrapper(system=system.capitalize())

    assert wrapper.get_binary_url() == wrapper.url


def test_construction_offline_reports_the_network_fallback_version(make_wrapper):
    """Constructing the wrapper offline yields the sentinel version.

    ``__init__`` calls the changelog HTTP probe and falls back to ``0.0.0``
    when it cannot reach the network, which is exactly the state every test
    in this suite runs in.
    """
    wrapper = make_wrapper()

    assert wrapper.__version__ == "0.0.0"
    assert wrapper._requests_fake.calls == [
        "https://raw.githubusercontent.com/aliasfoxkde/py7zip/main/docs/CHANGELOG.md"
    ]


def test_setup_is_invoked_during_construction(monkeypatch, make_wrapper):
    calls = []
    monkeypatch.setattr(
        py7zip_module.Py7zip,
        "setup",
        lambda self: calls.append(self.binary_path),
    )

    wrapper = make_wrapper(stub_setup=False)

    assert calls == [wrapper.binary_path]


def test_fake_platform_reports_its_configuration(monkeypatch):
    platform_fake = fakes.FakePlatform(
        monkeypatch, system="Darwin", machine="arm64", architecture=("64bit", "")
    )

    assert "Darwin" in repr(platform_fake)
    assert platform_fake.uname.machine == "arm64"
