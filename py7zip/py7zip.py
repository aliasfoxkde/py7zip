from __future__ import annotations

import os
import platform
import re
import subprocess
import urllib.request
from collections.abc import Sequence
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as package_version
from pathlib import Path

import requests

from .platforms import PlatformInfo
from .safe import ArchiveResult, SafePy7zip


class Py7zip:
    """An unofficial, cross-platform, lightweight, and easy-to-use wrapper
    for 7zip command-line binaries (7za) in Python."""

    # The safe runtime stores a verified Path (or None before acquisition);
    # the legacy runtime stores the historical in-package path as a str.
    binary_path: str | Path | None
    platform_info: PlatformInfo
    _safe: SafePy7zip

    def __init__(
        self,
        verbose: bool = False,
        debug: bool = False,
        *,
        legacy: bool = False,
        cache_dir: str | os.PathLike[str] | None = None,
        binary_path: str | os.PathLike[str] | None = None,
        timeout: float = 300.0,
    ) -> None:
        """Initializes the class and variables."""
        self.verbose = verbose
        self.debug = debug
        self.legacy = legacy
        if not legacy:
            self._safe = SafePy7zip(
                cache_dir=cache_dir, binary_path=binary_path, timeout=timeout
            )
            self.platform_info = self._safe.platform_info
            self.binary_path = self._safe.binary_path
            self.__version__ = self._metadata_version()
            return

        self.platform = platform.system().lower()
        self.supported = ["windows", "linux", "darwin"]
        self.architecture = platform.architecture()[0]
        self.username = "aliasfoxkde"
        self.app_name = "py7zip"
        self.base_bin_url = (
            f"https://github.com/{self.username}/{self.app_name}/raw/main/bin/"
        )
        self.raw_usercontent = "https://raw.githubusercontent.com"
        self.debug_info = platform.uname()

        # Move platform check to dedicated function
        if platform.machine() in ["AMD64", "x86_64"]:
            self.sys_type = "pc"
        elif "arm" in platform.machine():
            self.sys_type = "arm"
        else:
            raise NotImplementedError("No machine type could be detected. Exiting.")

        self.arch_type = {
            "32bit": "x86",
            "64bit": "x64",
            "arm64": "x64",
            "arm32": "x86",
        }[self.architecture]
        self.sys_platform = {"windows": "win", "linux": "lin", "darwin": "mac"}[
            self.platform
        ]
        self.extension = {"windows": ".exe", "linux": "", "darwin": ""}[self.platform]
        self.url = f"{self.base_bin_url}/{self.sys_platform}/{self.sys_type}/{self.arch_type}/7za{self.extension}"
        self.binary_path = os.path.join(
            os.path.dirname(__file__), f"7za{self.extension}"
        )
        self.__version__ = self.get_version()
        self.setup()

    @staticmethod
    def _metadata_version() -> str:
        try:
            return package_version("py7zip")
        except PackageNotFoundError:
            return "0.7.3"

    def get_version(self, verbose: bool = False) -> str:
        """Construct the URL to fetch CHANGELOG.md and find the version number."""
        if not self.legacy:
            return self._metadata_version()
        changelog_url = f"{self.raw_usercontent}/{self.username}/{self.app_name}/main/docs/CHANGELOG.md"

        try:
            # Fetch the content of the CHANGELOG.md file from the URL
            response = requests.get(changelog_url)
            response.raise_for_status()  # Raise an error for bad responses
            changelog_content = response.text

            # Search for the version in the content
            version_match = re.search(
                r"^-\s*(\d+\.\d+\.\d+)", changelog_content, re.MULTILINE
            )

            if version_match:
                version = version_match.group(1)
                if verbose:
                    print(f"Latest version found in CHANGELOG.md: {version}")
            else:
                version = "0.0.0"
                if verbose:
                    print("Failed to retrieve the latest version from CHANGELOG.md")
        except requests.RequestException as e:
            version = "0.0.0"
            if verbose:
                print(f"Error fetching CHANGELOG.md: {e}")

        return version

    def setup(self) -> None:
        """Checks the system for prerequisites and performs the required steps."""
        if not self.legacy:
            return
        # Only the legacy branch reaches here, and legacy __init__ always
        # assigns binary_path a str.
        binary_path = self.binary_path
        assert binary_path is not None
        try:
            if not os.path.exists(binary_path):
                self.download_binary()
        except (OSError, requests.RequestException) as err:
            print(err)

    @staticmethod
    def cd(directory_path: str | os.PathLike[str]) -> None:
        os.chdir(directory_path)

    def download_binary(self) -> Path | None:
        """Dynamically downloads the binary required for the given platform."""
        if not self.legacy:
            self.binary_path = self._safe.ensure_binary()
            return self.binary_path
        # Only the legacy branch reaches here, and legacy __init__ always
        # assigns binary_path a str.
        binary_path = self.binary_path
        assert binary_path is not None
        binary_url = self.get_binary_url()
        binary_dir = os.path.dirname(binary_path)
        os.makedirs(binary_dir, exist_ok=True)

        with (
            urllib.request.urlopen(binary_url) as response,
            open(binary_path, "wb") as out_file,
        ):
            out_file.write(response.read())
            os.chmod(binary_path, 0o755)
        return None

    def get_binary_url(self) -> str:
        """Return the source location for the platform's 7-Zip binary.

        On the safe runtime (default), binary acquisition is explicit:
        callers must invoke :meth:`download_binary` (or supply a
        pre-verified ``binary_path``) before using the wrapper. This
        method raises :class:`NotImplementedError` rather than returning
        a fabricated cache-relative path, because the safe runtime does
        not construct download URLs at construction time.

        On the legacy runtime (``legacy=True``), returns the URL where
        the historical in-package binary would have been served from,
        or raises :class:`NotImplementedError` for unsupported host
        platforms.
        """
        if not self.legacy:
            raise NotImplementedError(
                "get_binary_url() is not supported on the safe runtime; "
                "call download_binary() to acquire a verified binary into "
                "the cache directory, or supply a pre-verified "
                "binary_path=... to the constructor."
            )
        if self.platform not in self.supported:
            raise NotImplementedError(f"Platform '{self.platform}' is not supported.")
        return self.url

    def wrapper(
        self,
        src: str | os.PathLike[str],
        dst: str | os.PathLike[str],
        options: str | Sequence[str] = "",
        method: str = "decompress",
    ) -> ArchiveResult | None:
        """Method used to extract an archive.

        ``options`` means different things on the two runtimes:

        * Safe runtime (default): only a sequence of individual arguments
          (e.g. ``["-y", "-mx=9"]``) is accepted, each forwarded as a single
          argument to an argv runner.  A non-empty string raises
          :class:`TypeError` (audit decision D5 / OVH-16: shell text is
          rejected, never silently tokenized).  The documented default
          ``""`` forwards no arguments.
        * Legacy runtime: a string is appended verbatim to the shell
          command, preserving the historical behaviour; a sequence is
          forwarded element by element as an argument vector with
          ``shell=False``, so no element is re-interpreted by a shell.
        """
        if not self.legacy:
            operation = "compress" if method == "compress" else "decompress"
            safe_options = () if options == "" else options
            result = self._safe.run(operation, src, dst, safe_options)
            if self.debug and result.stdout:
                print(result.stdout)
            return result
        command: str | tuple[str, ...]
        shell = isinstance(options, str)
        if method == "compress":
            if shell:
                command = f'"7za{self.extension}" a "{dst}" "{src}" {options}'
            else:
                command = (
                    f"7za{self.extension}",
                    "a",
                    os.fspath(dst),
                    os.fspath(src),
                    *tuple(options),
                )
            success_msg = f"Backup created from '{src}' to '{dst}'."
            error_msg = f"Failed to extract archive from '{src}' to '{dst}'."
        else:  # "decompress" method as default
            if shell:
                command = f'"7za{self.extension}" x "{src}" -o"{dst}" {options}'
            else:
                command = (
                    f"7za{self.extension}",
                    "x",
                    os.fspath(src),
                    f"-o{os.fspath(dst)}",
                    *tuple(options),
                )
            success_msg = f"Extracted archive from '{src}' to '{dst}'"
            error_msg = f"Failed to create backup from '{src}' to '{dst}'."

        try:
            completed = subprocess.run(
                command, capture_output=True, text=True, shell=shell, check=True
            )
            if self.debug:
                print(completed.stdout)
            if self.verbose:
                print(success_msg)
        except subprocess.CalledProcessError as e:
            if self.debug:
                print(f"Error: {e.stderr}.")
            if self.verbose:
                print(error_msg)
        return None

    def decompress(
        self,
        src: str | os.PathLike[str],
        dst: str | os.PathLike[str],
        options: str | Sequence[str] = "",
    ) -> ArchiveResult | None:
        """Method used to extract an archive."""
        return self.wrapper(src, dst, options=options, method="decompress")

    def extract(
        self,
        src: str | os.PathLike[str],
        dst: str | os.PathLike[str],
        options: str | Sequence[str] = "",
    ) -> ArchiveResult | None:
        """Alias used for 'decompress' method."""
        return self.wrapper(src, dst, options=options, method="decompress")

    def compress(
        self,
        src: str | os.PathLike[str],
        dst: str | os.PathLike[str],
        options: str | Sequence[str] = "",
    ) -> ArchiveResult | None:
        """Method used to backup files, folders, or directories to an archive."""
        return self.wrapper(src, dst, options=options, method="compress")

    def archive(
        self,
        src: str | os.PathLike[str],
        dst: str | os.PathLike[str],
        options: str | Sequence[str] = "",
    ) -> ArchiveResult | None:
        """Alias used for compress method."""
        return self.wrapper(src, dst, options=options, method="compress")

    def backup(
        self,
        src: str | os.PathLike[str],
        dst: str | os.PathLike[str],
        options: str | Sequence[str] = "",
    ) -> ArchiveResult | None:
        """Alias used for compress method."""
        return self.wrapper(src, dst, options=options, method="compress")

    def full(
        self,
        src: str | os.PathLike[str],
        dst: str | os.PathLike[str],
        options: str | Sequence[str] = "",
    ) -> None:
        return

    def incremental(
        self,
        src: str | os.PathLike[str],
        dst: str | os.PathLike[str],
        options: str | Sequence[str] = "",
    ) -> None:
        return

    def differential(
        self,
        src: str | os.PathLike[str],
        dst: str | os.PathLike[str],
        options: str | Sequence[str] = "",
    ) -> None:
        return

    def snapshot(
        self,
        src: str | os.PathLike[str],
        dst: str | os.PathLike[str],
        options: str | Sequence[str] = "",
    ) -> None:
        """Streamlines the process for creating a snapshot."""
        return


if __name__ == "__main__":
    print("This module is intended to be imported, not run directly!")
