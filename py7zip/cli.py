"""Command-line access to the safe py7zip runtime.

Every subcommand drives :class:`~py7zip.safe.SafePy7zip` — the
argument-list runtime with checksum-verified binary acquisition and
zip-slip validation — and maps its outcomes onto shell exit codes:

* ``0`` success
* ``1`` archive execution or binary acquisition failed
* ``2`` usage error (also argparse's own code)
* ``3`` the operation exceeded ``--timeout``
* ``4`` extraction refused unsafe archive members (zip-slip guard)
* ``5`` the host platform has no catalog artifact

The same operations are available programmatically through
``python -m py7zip`` and the installed ``py7zip`` script.  Switches meant for
7-Zip itself follow a ``--`` terminator and reach the binary untouched.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from . import __version__
from .acquisition import ArtifactAcquisitionError
from .platforms import UnsupportedPlatformError
from .safe import (
    ArchiveExecutionError,
    ArchiveTimeoutError,
    ArchiveTraversalError,
    SafePy7zip,
    differential_name,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser; one subcommand per runtime operation."""
    parser = argparse.ArgumentParser(
        prog="py7zip",
        description="Create, inspect, and extract 7-Zip archives.",
        epilog="Exit codes: 0 success, 1 execution failure, 2 usage, "
        "3 timeout, 4 unsafe archive members, 5 unsupported platform. "
        "7-Zip switches are passed verbatim after a -- terminator "
        "(e.g. extract arc.7z out -- -y).",
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.set_defaults(option=())
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--binary-path",
        type=Path,
        default=None,
        help="use this 7-Zip executable instead of acquiring one",
    )
    common.add_argument(
        "--cache-dir",
        type=Path,
        default=None,
        help="cache directory for the acquired binary (default ~/.cache/py7zip)",
    )
    common.add_argument(
        "--timeout",
        type=float,
        default=300.0,
        help="seconds before an archive operation is killed (default 300)",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    def add(name: str, help_text: str) -> argparse.ArgumentParser:
        command = subcommands.add_parser(name, parents=[common], help=help_text)
        command.set_defaults(func=_dispatch_command)
        return command

    add("download", "acquire and verify the 7-Zip binary for this host")
    for name, help_text in (
        ("compress", "create ARCHIVE from SOURCE"),
        ("full", "like compress, but unattended-overwrite safe"),
        ("incremental", "update ARCHIVE in place (deletions retained)"),
    ):
        command = add(name, help_text)
        command.add_argument("source")
        command.add_argument("archive")
    extract = add("extract", "extract ARCHIVE into DESTINATION (zip-slip guarded)")
    extract.add_argument("archive")
    extract.add_argument("destination")
    listing = add("list", "print the member paths stored in ARCHIVE")
    listing.add_argument("archive")
    differential = add("differential", "write changes since BASE to a diff archive")
    differential.add_argument("source")
    differential.add_argument("base", help="the existing base archive")
    differential.add_argument(
        "--diff-path",
        type=Path,
        default=None,
        help="diff archive path (default <base-stem>.diff.7z)",
    )
    snapshot = add("snapshot", "create a timestamped archive of SOURCE")
    snapshot.add_argument("source")
    snapshot.add_argument("archive")
    snapshot.add_argument(
        "--timestamp",
        default=None,
        help="override the YYYYmmddTHHMMSS name stamp (for deterministic runs)",
    )
    return parser


def _runtime(args: argparse.Namespace) -> SafePy7zip:
    return SafePy7zip(
        cache_dir=args.cache_dir,
        binary_path=args.binary_path,
        timeout=args.timeout,
    )


def _created_archive(result) -> Path:
    """Recover the archive path from a compress/update invocation.

    The runtime places the destination archive immediately after the
    7-Zip command letter, an ordering pinned by ``ArchiveRunner.run``.
    """
    return Path(result.command[2])


def _dispatch_command(args: argparse.Namespace) -> int:
    """Run the parsed subcommand and print its one-line human outcome."""
    runtime = _runtime(args)
    options = tuple(args.option)
    command = args.command
    if command == "download":
        print(runtime.ensure_binary())
    elif command == "compress":
        runtime.compress(args.source, args.archive, options)
        print(f"created {args.archive}")
    elif command == "full":
        runtime.full(args.source, args.archive, options)
        print(f"created {args.archive}")
    elif command == "incremental":
        runtime.incremental(args.source, args.archive, options)
        print(f"updated {args.archive}")
    elif command == "extract":
        runtime.decompress(args.archive, args.destination, options)
        print(f"extracted {args.archive} into {args.destination}")
    elif command == "list":
        for entry in runtime.list_entries(args.archive):
            print(entry)
    elif command == "differential":
        diff = (
            args.diff_path
            if args.diff_path is not None
            else differential_name(args.base)
        )
        runtime.differential(args.source, args.base, diff_path=diff, options=options)
        print(f"wrote {diff}")
    else:  # snapshot
        result = runtime.snapshot(
            args.source, args.archive, options, timestamp=args.timestamp
        )
        # The stamped name is decided inside the runtime; recover it from
        # the executed command instead of recomputing a second wall-clock.
        print(f"created {_created_archive(result)}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Parse ``argv`` (default: ``sys.argv``) and return the exit code.

    ``--`` ends py7zip's own parsing; everything after it is handed to 7-Zip
    verbatim.  Every 7-Zip switch starts with ``-`` (``-y``, ``-mx=9``), so
    they cannot follow a value-taking flag — the verbatim tail is the same
    convention 7-Zip itself documents for stopping switch parsing.
    """
    raw = list(sys.argv[1:] if argv is None else argv)
    if "--" in raw:
        split = raw.index("--")
        raw, passthrough = raw[:split], tuple(raw[split + 1 :])
    else:
        passthrough = ()
    args = build_parser().parse_args(raw)
    args.option = passthrough
    try:
        return args.func(args)
    except ArchiveTimeoutError as error:
        print(f"py7zip: timed out: {error}", file=sys.stderr)
        return 3
    except ArchiveTraversalError as error:
        print(f"py7zip: refused unsafe archive members: {error}", file=sys.stderr)
        return 4
    except UnsupportedPlatformError as error:
        print(f"py7zip: unsupported platform: {error}", file=sys.stderr)
        return 5
    except (ArchiveExecutionError, ArtifactAcquisitionError) as error:
        print(f"py7zip: {error}", file=sys.stderr)
        return 1
    except ValueError as error:
        # Definition-level misuse, e.g. a differential on a non-.7z base.
        print(f"py7zip: {error}", file=sys.stderr)
        return 2
