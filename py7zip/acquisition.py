"""Explicit, checksum-verified acquisition of published 7-Zip artifacts."""

from __future__ import annotations

import hashlib
import os
import tempfile
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from urllib.request import urlopen

from .platforms import ArtifactCatalog, ArtifactSpec, PlatformInfo


class ArtifactAcquisitionError(RuntimeError):
    """Base error for binary acquisition and verification failures."""


class ArtifactIntegrityError(ArtifactAcquisitionError):
    """Raised when downloaded or cached bytes do not match the catalog."""


class ArtifactLockTimeout(ArtifactAcquisitionError):
    """Raised when another process holds the cache lock too long."""


class ArtifactManager:
    """Acquire catalog artifacts into a caller-selected cache directory.

    Construction is side-effect free.  ``ensure`` is the explicit operation
    that may read/write the cache and contact the configured source.
    """

    def __init__(
        self,
        cache_dir: str | os.PathLike[str],
        *,
        base_url: str = "https://github.com/aliasfoxkde/py7zip/raw/main",
        timeout: float = 30.0,
        lock_timeout: float = 30.0,
    ) -> None:
        if timeout <= 0 or lock_timeout <= 0:
            raise ValueError("timeouts must be positive")
        self.cache_dir = Path(cache_dir)
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.lock_timeout = lock_timeout

    def ensure(self, info: PlatformInfo) -> Path:
        """Return a verified cached artifact, downloading it when absent."""
        spec = ArtifactCatalog.resolve(info)
        destination = self.cache_dir / spec.executable_name
        self._validate_destination(destination)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        with self._lock(self.cache_dir / f".{spec.executable_name}.lock"):
            if destination.exists():
                self._verify(destination, spec)
                return destination
            self._download(spec, destination)
            return destination

    def _download(self, spec: ArtifactSpec, destination: Path) -> None:
        url = f"{self.base_url}/{spec.relative_path}"
        temporary_name: str | None = None
        try:
            with (
                urlopen(url, timeout=self.timeout) as response,
                tempfile.NamedTemporaryFile(
                    mode="wb", dir=self.cache_dir, prefix=".download-", delete=False
                ) as temporary,
            ):
                temporary_name = temporary.name
                total = 0
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > spec.size_bytes:
                        raise ArtifactIntegrityError(
                            f"artifact exceeds catalog size for {spec.relative_path}"
                        )
                    temporary.write(chunk)
            temporary_path = Path(temporary_name)
            self._verify(temporary_path, spec)
            os.chmod(temporary_path, 0o755)
            os.replace(temporary_path, destination)
        except ArtifactAcquisitionError:
            raise
        except OSError as exc:
            raise ArtifactAcquisitionError(f"failed to acquire {url}: {exc}") from exc
        finally:
            if temporary_name:
                Path(temporary_name).unlink(missing_ok=True)

    @staticmethod
    def _verify(path: Path, spec: ArtifactSpec) -> None:
        digest = hashlib.sha256()
        size = 0
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                size += len(chunk)
                digest.update(chunk)
        actual = digest.hexdigest()
        if size != spec.size_bytes or actual != spec.sha256:
            raise ArtifactIntegrityError(
                f"artifact integrity mismatch for {spec.relative_path}: "
                f"size={size} sha256={actual}"
            )

    def _validate_destination(self, destination: Path) -> None:
        root = self.cache_dir.resolve()
        resolved = destination.resolve()
        if resolved.parent != root:
            raise ArtifactAcquisitionError("artifact destination escapes cache directory")

    @contextmanager
    def _lock(self, lock_path: Path) -> Iterator[None]:
        deadline = time.monotonic() + self.lock_timeout
        while True:
            try:
                descriptor = os.open(
                    lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600
                )
                os.close(descriptor)
                break
            except FileExistsError:
                if time.monotonic() >= deadline:
                    raise ArtifactLockTimeout(f"timed out waiting for {lock_path}")
                time.sleep(0.05)
        try:
            yield
        finally:
            lock_path.unlink(missing_ok=True)
