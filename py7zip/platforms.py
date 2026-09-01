"""Deterministic host classification and bundled-artifact catalog.

This module deliberately has no network, filesystem, or subprocess side
effects.  It is the seam used by the later binary manager to choose an
artifact before it performs any acquisition.
"""

from __future__ import annotations

import platform as host_platform
import struct
from dataclasses import dataclass
from typing import ClassVar


class UnsupportedPlatformError(RuntimeError):
    """Raised when no published py7zip artifact matches the host."""


@dataclass(frozen=True)
class PlatformInfo:
    """Normalized platform identity used by the artifact catalog."""

    system: str
    machine: str
    bits: int
    family: str
    architecture: str

    @classmethod
    def detect(
        cls,
        *,
        system: str | None = None,
        machine: str | None = None,
        bits: int | None = None,
    ) -> PlatformInfo:
        """Detect and normalize the current host without touching I/O."""
        raw_system = (system or host_platform.system()).strip().lower()
        raw_machine = (machine or host_platform.machine()).strip().lower()
        pointer_bits = bits if bits is not None else struct.calcsize("P") * 8

        systems = {"linux": "linux", "windows": "windows", "darwin": "darwin"}
        normalized_system = systems.get(raw_system)
        if normalized_system is None:
            raise UnsupportedPlatformError(
                f"unsupported operating system: {system or raw_system}"
            )
        if pointer_bits not in (32, 64):
            raise UnsupportedPlatformError(f"unsupported pointer width: {pointer_bits}")

        pc_machines = {"amd64", "x86_64", "i386", "i686", "x86"}
        arm_machines = {
            "aarch64",
            "arm64",
            "armv8",
            "armv8l",
            "armv7l",
            "armv7",
            "arm",
        }
        if raw_machine in pc_machines:
            family = "pc"
        elif raw_machine in arm_machines:
            family = "arm"
        else:
            raise UnsupportedPlatformError(f"unsupported machine: {machine or raw_machine}")

        # The repository uses x64/x86 for PC artifacts and x64/x32 for ARM
        # artifacts.  The latter reflects the upstream binary layout, not a
        # claim that every ARM host is 32-bit.
        if family == "pc":
            architecture = "x64" if pointer_bits == 64 else "x86"
        elif pointer_bits == 64:
            architecture = "x64"
        else:
            architecture = "x32"

        return cls(normalized_system, raw_machine, pointer_bits, family, architecture)


@dataclass(frozen=True)
class ArtifactSpec:
    """Published repository-relative binary artifact metadata."""

    relative_path: str
    executable_name: str
    sha256: str
    size_bytes: int


class ArtifactCatalog:
    """Resolve normalized hosts only to non-empty published artifacts."""

    _ARTIFACTS: ClassVar[dict[tuple[str, str, str], ArtifactSpec]] = {
        ("linux", "pc", "x64"): ArtifactSpec("bin/lin/pc/x64/7za", "7za", "12ef12519899ecda8ba59940d7f25a3f4818c97693538d49e894e6b783fb3081", 2837048),
        ("linux", "pc", "x86"): ArtifactSpec("bin/lin/pc/x86/7za", "7za", "ca0950c6d4b6e4ed2c7d0d1759b2beb68aecaf95ed31d9e5c1ae9faa914c37b9", 3139200),
        ("linux", "arm", "x64"): ArtifactSpec("bin/lin/arm/x64/7za", "7za", "271f123d64fb339f3011388005ff781958e4c17b9eb781e4d7a7b38712808a41", 2428216),
        ("linux", "arm", "x32"): ArtifactSpec("bin/lin/arm/x32/7za", "7za", "1414d731e764b969c22dae77d3948c6f0d1fca7b33eb7a16d016038e4e8ea753", 1519768),
        ("windows", "pc", "x64"): ArtifactSpec("bin/win/pc/x64/7za.exe", "7za.exe", "827f88db392fbb679ca0dcf0818f32e74b59242061d0e6bc05bac9c672bbde51", 1314816),
        ("windows", "pc", "x86"): ArtifactSpec("bin/win/pc/x86/7za.exe", "7za.exe", "4721caf434de02b9aeb80b930702bbca75a1d54a5308c3445ec0db0778cfe693", 841216),
        # The repository contains one non-empty universal macOS artifact.
        ("darwin", "pc", "x64"): ArtifactSpec("bin/mac/any/7za", "7za", "c76d80526586c039e11d9d2ea8fe02324798c5082711178304b5060565859742", 5792768),
        ("darwin", "pc", "x86"): ArtifactSpec("bin/mac/any/7za", "7za", "c76d80526586c039e11d9d2ea8fe02324798c5082711178304b5060565859742", 5792768),
        ("darwin", "arm", "x64"): ArtifactSpec("bin/mac/any/7za", "7za", "c76d80526586c039e11d9d2ea8fe02324798c5082711178304b5060565859742", 5792768),
    }

    @classmethod
    def specs(cls) -> tuple[ArtifactSpec, ...]:
        """Return each distinct published artifact exactly once."""
        return tuple(dict.fromkeys(cls._ARTIFACTS.values()))

    @classmethod
    def resolve(cls, info: PlatformInfo) -> ArtifactSpec:
        """Return the published artifact or raise a typed refusal."""
        try:
            return cls._ARTIFACTS[(info.system, info.family, info.architecture)]
        except KeyError as exc:
            raise UnsupportedPlatformError(
                f"no published artifact for {info.system}/{info.family}/{info.architecture}"
            ) from exc
