"""Deterministic host classification and bundled-artifact catalog.

This module deliberately has no network, filesystem, or subprocess side
effects.  It is the seam used by the later binary manager to choose an
artifact before it performs any acquisition.
"""

from __future__ import annotations

from dataclasses import dataclass
import platform as host_platform
import struct


class UnsupportedPlatformError(RuntimeError):
    """Raised when no published py7zip artifact matches the host."""


@dataclass(frozen=True, slots=True)
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
    ) -> "PlatformInfo":
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


@dataclass(frozen=True, slots=True)
class ArtifactSpec:
    """Published repository-relative binary artifact metadata."""

    relative_path: str
    executable_name: str


class ArtifactCatalog:
    """Resolve normalized hosts only to non-empty published artifacts."""

    _ARTIFACTS = {
        ("linux", "pc", "x64"): ArtifactSpec("bin/lin/pc/x64/7za", "7za"),
        ("linux", "pc", "x86"): ArtifactSpec("bin/lin/pc/x86/7za", "7za"),
        ("linux", "arm", "x64"): ArtifactSpec("bin/lin/arm/x64/7za", "7za"),
        ("linux", "arm", "x32"): ArtifactSpec("bin/lin/arm/x32/7za", "7za"),
        ("windows", "pc", "x64"): ArtifactSpec("bin/win/pc/x64/7za.exe", "7za.exe"),
        ("windows", "pc", "x86"): ArtifactSpec("bin/win/pc/x86/7za.exe", "7za.exe"),
        # The repository contains one non-empty universal macOS artifact.
        ("darwin", "pc", "x64"): ArtifactSpec("bin/mac/any/7za", "7za"),
        ("darwin", "pc", "x86"): ArtifactSpec("bin/mac/any/7za", "7za"),
        ("darwin", "arm", "x64"): ArtifactSpec("bin/mac/any/7za", "7za"),
    }

    @classmethod
    def resolve(cls, info: PlatformInfo) -> ArtifactSpec:
        """Return the published artifact or raise a typed refusal."""
        try:
            return cls._ARTIFACTS[(info.system, info.family, info.architecture)]
        except KeyError as exc:
            raise UnsupportedPlatformError(
                f"no published artifact for {info.system}/{info.family}/{info.architecture}"
            ) from exc

