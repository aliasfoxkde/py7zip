"""Side-effect-free construction and safe argv-based archive execution."""

from __future__ import annotations

import os
import subprocess
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from .acquisition import ArtifactManager
from .platforms import PlatformInfo


class ArchiveExecutionError(RuntimeError):
    """Base error for failures to start or control 7-Zip."""


class ArchiveTimeoutError(ArchiveExecutionError):
    """Raised when 7-Zip exceeds the configured execution timeout."""


@dataclass(frozen=True)
class ArchiveResult:
    """Complete result of one 7-Zip invocation."""

    command: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str

    @property
    def success(self) -> bool:
        return self.returncode == 0


class ArchiveRunner:
    """Run 7-Zip with an argument vector and bounded execution time."""

    def __init__(self, binary_path: str | os.PathLike[str], *, timeout: float = 300.0):
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        self.binary_path = Path(binary_path)
        self.timeout = timeout

    def run(
        self,
        operation: str,
        source: str | os.PathLike[str],
        destination: str | os.PathLike[str],
        options: Sequence[str] = (),
    ) -> ArchiveResult:
        """Run an archive operation without invoking a shell."""
        if operation not in {"compress", "decompress"}:
            raise ValueError("operation must be 'compress' or 'decompress'")
        if isinstance(options, (str, bytes)):
            raise TypeError("options must be a sequence of individual arguments")

        source_text = os.fspath(source)
        destination_text = os.fspath(destination)
        option_args = tuple(os.fspath(option) for option in options)
        command = (
            (str(self.binary_path), "a", destination_text, source_text, *option_args)
            if operation == "compress"
            else (
                str(self.binary_path),
                "x",
                source_text,
                f"-o{destination_text}",
                *option_args,
            )
        )
        if any("\x00" in argument for argument in command):
            raise ValueError("archive arguments cannot contain NUL bytes")

        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                shell=False,
                check=False,
                timeout=self.timeout,
            )
        except FileNotFoundError as exc:
            raise ArchiveExecutionError(
                f"7-Zip binary not found: {self.binary_path}"
            ) from exc
        except subprocess.TimeoutExpired as exc:
            raise ArchiveTimeoutError(
                f"7-Zip exceeded {self.timeout:g}s timeout"
            ) from exc
        except OSError as exc:
            raise ArchiveExecutionError(f"failed to start 7-Zip: {exc}") from exc

        return ArchiveResult(
            command=command,
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )


class SafePy7zip:
    """Explicit production API combining acquisition and safe execution.

    Construction performs platform detection only.  It never downloads a
    binary or starts a process.  Call ``ensure_binary`` explicitly before the
    first operation, or provide a verified binary path for an offline run.
    """

    def __init__(
        self,
        *,
        cache_dir: str | os.PathLike[str] | None = None,
        binary_path: str | os.PathLike[str] | None = None,
        timeout: float = 300.0,
    ) -> None:
        self.platform_info = PlatformInfo.detect()
        self.cache_dir = (
            Path(cache_dir)
            if cache_dir is not None
            else Path.home() / ".cache" / "py7zip"
        )
        self.binary_path = Path(binary_path) if binary_path is not None else None
        self.timeout = timeout

    def ensure_binary(self) -> Path:
        """Acquire and verify the host artifact explicitly."""
        if self.binary_path is None:
            self.binary_path = ArtifactManager(
                self.cache_dir, timeout=min(self.timeout, 30.0)
            ).ensure(self.platform_info)
        return self.binary_path

    def run(
        self,
        operation: str,
        source: str | os.PathLike[str],
        destination: str | os.PathLike[str],
        options: Sequence[str] = (),
    ) -> ArchiveResult:
        """Execute an operation after explicit binary resolution."""
        return ArchiveRunner(self.ensure_binary(), timeout=self.timeout).run(
            operation, source, destination, options
        )

    def compress(
        self,
        source: str | os.PathLike[str],
        destination: str | os.PathLike[str],
        options: Sequence[str] = (),
    ) -> ArchiveResult:
        return self.run("compress", source, destination, options)

    def decompress(
        self,
        source: str | os.PathLike[str],
        destination: str | os.PathLike[str],
        options: Sequence[str] = (),
    ) -> ArchiveResult:
        return self.run("decompress", source, destination, options)
