"""Side-effect-free construction and safe argv-based archive execution."""

from __future__ import annotations

import os
import subprocess
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath, PureWindowsPath

from .acquisition import ArtifactManager
from .platforms import PlatformInfo


class ArchiveExecutionError(RuntimeError):
    """Base error for failures to start or control 7-Zip."""


class ArchiveTimeoutError(ArchiveExecutionError):
    """Raised when 7-Zip exceeds the configured execution timeout."""


class ArchiveTraversalError(ArchiveExecutionError):
    """Raised when an archive member would escape its extraction root."""


def snapshot_name(destination: str | os.PathLike[str], stamp: str) -> Path:
    """Return the archive path a snapshot of ``destination`` writes to.

    The stamp is inserted into the name's stem, so ``backups/site.7z``
    becomes ``backups/site.<stamp>.7z``.  ``SafePy7zip.snapshot`` and the
    command-line interface share this helper so both always agree on the
    produced name.
    """
    target = Path(destination)
    return target.with_name(f"{target.stem}.{stamp}.7z")


def differential_name(destination: str | os.PathLike[str]) -> Path:
    """Return the diff archive path ``SafePy7zip.differential`` writes to.

    The diff is a sibling of the base archive with the ``.diff.7z``
    suffix; sharing the helper keeps the runtime and the command-line
    interface consistent about where a differential lands.
    """
    return Path(os.fspath(destination)).with_suffix(".diff.7z")


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
        """Run an archive operation without invoking a shell.

        ``compress`` builds ``a <destination> <source>``; ``decompress``
        builds ``x <source> -o<destination>``; ``update`` builds
        ``u <archive> <source>``.  In every case the destination comes
        before the source on the command line.
        """
        if operation not in {"compress", "decompress", "update"}:
            raise ValueError("operation must be 'compress', 'decompress' or 'update'")
        if isinstance(options, (str, bytes)):
            raise TypeError("options must be a sequence of individual arguments")

        source_text = os.fspath(source)
        destination_text = os.fspath(destination)
        option_args = tuple(os.fspath(option) for option in options)
        if operation == "compress":
            command = (
                str(self.binary_path),
                "a",
                destination_text,
                source_text,
                *option_args,
            )
        elif operation == "update":
            command = (
                str(self.binary_path),
                "u",
                destination_text,
                source_text,
                *option_args,
            )
        else:
            command = (
                str(self.binary_path),
                "x",
                source_text,
                f"-o{destination_text}",
                *option_args,
            )
        if any("\x00" in argument for argument in command):
            raise ValueError("archive arguments cannot contain NUL bytes")

        return self._invoke(command)

    def list_entries(self, archive: str | os.PathLike[str]) -> tuple[str, ...]:
        """List archive member paths using 7-Zip's machine-readable output."""
        archive_text = os.fspath(archive)
        result = self._invoke((str(self.binary_path), "l", "-slt", "-ba", archive_text))
        if not result.success:
            raise ArchiveExecutionError(
                f"7-Zip could not list archive {archive_text}: {result.stderr.strip()}"
            )
        return tuple(
            line.removeprefix("Path = ").strip()
            for line in result.stdout.splitlines()
            if line.startswith("Path = ") and line.removeprefix("Path = ").strip()
        )

    def _invoke(self, command: tuple[str, ...]) -> ArchiveResult:
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


def validate_archive_members(
    members: Sequence[str], destination: str | os.PathLike[str]
) -> None:
    """Reject absolute or traversal members before extraction begins."""
    root = Path(destination).resolve()
    for member in members:
        normalized = member.replace("\\", "/")
        posix_member = PurePosixPath(normalized)
        windows_member = PureWindowsPath(normalized)
        if (
            not normalized
            or posix_member.is_absolute()
            or windows_member.is_absolute()
            or windows_member.drive
        ):
            raise ArchiveTraversalError(f"unsafe archive member: {member!r}")
        candidate = (root / Path(*posix_member.parts)).resolve()
        try:
            candidate.relative_to(root)
        except ValueError as exc:
            raise ArchiveTraversalError(f"unsafe archive member: {member!r}") from exc


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
        runner = ArchiveRunner(self.ensure_binary(), timeout=self.timeout)
        validate_archive_members(runner.list_entries(source), destination)
        return runner.run("decompress", source, destination, options)

    def list_entries(self, archive: str | os.PathLike[str]) -> tuple[str, ...]:
        """Return the member paths stored in ``archive``."""
        return ArchiveRunner(self.ensure_binary(), timeout=self.timeout).list_entries(
            archive
        )

    def full(
        self,
        source: str | os.PathLike[str],
        destination: str | os.PathLike[str],
        options: Sequence[str] = (),
    ) -> ArchiveResult:
        """Create a complete archive of ``source`` at ``destination``.

        Every file currently on disk is stored; nothing is inherited from a
        previous archive.  ``-y`` is prepended so an unattended run never
        blocks on an overwrite prompt; caller options follow it.
        """
        return self.run("compress", source, destination, ("-y", *options))

    def incremental(
        self,
        source: str | os.PathLike[str],
        destination: str | os.PathLike[str],
        options: Sequence[str] = (),
    ) -> ArchiveResult:
        """Update ``destination`` in place with 7-Zip's default ``u`` semantics.

        The newest copy of each file wins, files absent from the source keep
        their archived copies, and a missing archive is created.  Note this
        retains deleted files by design; use ``snapshot`` for a fresh full
        copy or ``differential`` to record deletions.
        """
        return self.run("update", source, destination, ("-y", *options))

    def differential(
        self,
        source: str | os.PathLike[str],
        destination: str | os.PathLike[str],
        diff_path: str | os.PathLike[str] | None = None,
        options: Sequence[str] = (),
    ) -> ArchiveResult:
        """Write everything that differs from the base archive to a diff.

        ``destination`` is the existing base archive and is left untouched.
        The diff archive receives new files, files whose disk copy is newer
        or otherwise diverges, and anti (tombstone) entries for deletions.
        Restoring means extracting the base archive and then the diff over
        it with overwrite enabled, e.g. ``decompress(diff, target,
        options=("-y",))``.  The diff must be 7z format because anti entries
        are a 7z feature; ``diff_path`` defaults to a sibling of the base
        named ``<base-stem>.diff.7z``.
        """
        diff = (
            Path(diff_path) if diff_path is not None else differential_name(destination)
        )
        if diff.suffix.lower() != ".7z":
            raise ValueError("differential archives must use the .7z format")
        update_switch = f"-up0q3r2x2y2z0w2!{os.fspath(diff)}"
        return self.run(
            "update", source, destination, ("-y", "-u-", update_switch, *options)
        )

    def snapshot(
        self,
        source: str | os.PathLike[str],
        destination: str | os.PathLike[str],
        options: Sequence[str] = (),
        *,
        timestamp: str | None = None,
    ) -> ArchiveResult:
        """Create a timestamped full archive and leave any original intact.

        ``destination`` is the archive path; its name stem gains a
        ``YYYYmmddTHHMMSS`` component, so ``backups/site.7z`` becomes
        ``backups/site.20260928T221500.7z``.  ``timestamp`` overrides the
        stamp for deterministic runs.
        """
        if timestamp is not None:
            stamp = timestamp
        else:
            # Naive local time is deliberate: the stamp names a wall-clock
            # snapshot on the machine taking the backup, not an instant.
            stamp = datetime.now().strftime("%Y%m%dT%H%M%S")  # noqa: DTZ005
        stamped = snapshot_name(destination, stamp)
        return self.run("compress", source, stamped, ("-y", *options))
