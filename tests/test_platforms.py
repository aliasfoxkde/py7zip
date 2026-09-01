"""Unit tests for the side-effect-free platform/catalog seam."""

from __future__ import annotations

import pytest

from py7zip.platforms import ArtifactCatalog, PlatformInfo, UnsupportedPlatformError


@pytest.mark.parametrize(
    ("system", "machine", "bits", "family", "architecture"),
    [
        ("Linux", "x86_64", 64, "pc", "x64"),
        ("Windows", "AMD64", 32, "pc", "x86"),
        ("Linux", "aarch64", 64, "arm", "x64"),
        ("Linux", "armv7l", 32, "arm", "x32"),
        ("Darwin", "arm64", 64, "arm", "x64"),
    ],
)
def test_detect_normalizes_published_host_facts(
    system, machine, bits, family, architecture
):
    info = PlatformInfo.detect(system=system, machine=machine, bits=bits)

    assert (info.system, info.family, info.architecture) == (
        system.lower() if system != "darwin" else "darwin",
        family,
        architecture,
    )


@pytest.mark.parametrize(
    ("system", "machine", "bits"),
    [
        ("SunOS", "x86_64", 64),
        ("Linux", "riscv64", 64),
        ("Linux", "x86_64", 128),
    ],
)
def test_detect_refuses_unknown_hosts(system, machine, bits):
    with pytest.raises(UnsupportedPlatformError):
        PlatformInfo.detect(system=system, machine=machine, bits=bits)


@pytest.mark.parametrize(
    ("system", "machine", "bits", "expected"),
    [
        ("Linux", "x86_64", 64, "bin/lin/pc/x64/7za"),
        ("Linux", "aarch64", 64, "bin/lin/arm/x64/7za"),
        ("Windows", "AMD64", 64, "bin/win/pc/x64/7za.exe"),
        ("Darwin", "arm64", 64, "bin/mac/any/7za"),
    ],
)
def test_catalog_resolves_nonempty_published_artifacts(
    system, machine, bits, expected
):
    spec = ArtifactCatalog.resolve(
        PlatformInfo.detect(system=system, machine=machine, bits=bits)
    )

    assert spec.relative_path == expected
    assert spec.executable_name in {"7za", "7za.exe"}


def test_catalog_refuses_an_unpublished_arm_windows_artifact():
    info = PlatformInfo.detect(system="Windows", machine="ARM64", bits=64)

    with pytest.raises(UnsupportedPlatformError, match="no published artifact"):
        ArtifactCatalog.resolve(info)
