"""py7zip: a safe, cross-platform Python wrapper for 7-Zip's 7za binary.

Importing this package performs no network access, downloads nothing, and
starts no process.  Acquiring a binary and running 7-Zip are explicit
operations (``Py7zip``/``SafePy7zip`` methods).
"""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _package_version

from .acquisition import (
    ArtifactAcquisitionError,
    ArtifactIntegrityError,
    ArtifactLockTimeoutError,
    ArtifactManager,
)
from .platforms import (
    ArtifactCatalog,
    ArtifactSpec,
    PlatformInfo,
    UnsupportedPlatformError,
)
from .py7zip import Py7zip
from .safe import (
    ArchiveExecutionError,
    ArchiveResult,
    ArchiveRunner,
    ArchiveTimeoutError,
    ArchiveTraversalError,
    SafePy7zip,
    differential_name,
    snapshot_name,
    validate_archive_members,
)

try:
    __version__ = _package_version("py7zip")
except PackageNotFoundError:  # running from a source checkout
    __version__ = "0.9.0"

__all__ = [
    "ArchiveExecutionError",
    "ArchiveResult",
    "ArchiveRunner",
    "ArchiveTimeoutError",
    "ArchiveTraversalError",
    "ArtifactAcquisitionError",
    "ArtifactCatalog",
    "ArtifactIntegrityError",
    "ArtifactLockTimeoutError",
    "ArtifactManager",
    "ArtifactSpec",
    "PlatformInfo",
    "Py7zip",
    "SafePy7zip",
    "UnsupportedPlatformError",
    "differential_name",
    "snapshot_name",
    "validate_archive_members",
]
