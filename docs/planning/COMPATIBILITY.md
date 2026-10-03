# py7zip compatibility policy

This document states the public contract of `py7zip` as it stands at the
Phase 0 baseline, the contract the revamp is moving to, and the migration map
between them. It is written before the contract changes so that each break is
a recorded decision rather than an accident of refactoring.

The behaviour described in "current contract" is not asserted from reading
the source; every line is pinned by a test in `tests/`.

**Note:** the sections below describe the Phase 0 baseline as it was. Changes
that have since shipped are recorded under "Recorded contract changes" at the
end of this file; those supersede the corresponding baseline rows.

## Current contract (Phase 0 baseline)

### Construction

| Aspect | Behaviour today |
|--------|-----------------|
| Signature | `Py7zip(verbose=False, debug=False)` |
| Side effects | Detects the host, probes `raw.githubusercontent.com` for the version, then downloads a 7za binary into the package directory if it is absent. All three happen inside `__init__`. |
| Failure mode for download errors | Printed and swallowed. Construction succeeds even when the binary could not be fetched. |
| Unsupported machine | Raises `NotImplementedError`. |
| Unsupported operating system | Raises `KeyError` for the platform name, or `KeyError` for an unrecognised pointer width — not the `NotImplementedError` the URL helper documents. |
| `__version__` | Fetched over HTTP from `docs/CHANGELOG.md` on `main`; the literal string `"0.0.0"` on any network or parse failure. |
| Import cost | `import py7zip` and `import py7zip.py7zip` perform no I/O and no network access. Only construction does. |

### Aliases

`decompress` and `extract` run the `x` (extract) operation; `compress`,
`archive` and `backup` run the `a` (add) operation. All five forward to the
single `wrapper` method.

**Every alias discards the caller's `options` argument.** Each one passes the
literal empty string to `wrapper`, so `obj.extract(a, b, options="-y")` runs
without `-y`. Only calling `wrapper(..., options=...)` directly forwards them.
This is characterized by
`tests/test_characterization_wrapper.py::test_aliases_silently_discard_the_callers_options`.

### Return values and errors

`wrapper` and all five aliases return `None` unconditionally. A nonzero exit
code from 7za is caught inside `wrapper`; nothing is raised, nothing is
returned, and diagnostics are only printed when `verbose` or `debug` is set.
There is no way for a caller to learn that an operation failed.

### The snapshot family

`full`, `incremental`, `differential` and `snapshot` are public methods that
share the `wrapper` signature and return `None` without doing anything. They
run no subprocess and have no implementation. They are **not** advertised
features and are removed in Phase 4.

### Unspecified behaviour

* `wrapper` builds one shell string and passes it to
  `subprocess.run(..., shell=True)`. The caller's `options` text is
  interpolated verbatim, so it is interpreted by the shell.
* Source and destination are never validated. Nonexistent paths and paths
  containing `..` are passed through unchanged.
* Downloaded bytes are written to disk and marked `0o755` with no size bound,
  content check, or digest.
* `Py7zip.cd` changes the working directory of the entire process.

## Target contract (from Phase 2 onward)

| Aspect | Target |
|--------|--------|
| Construction | Performs detection only. Binary acquisition is an explicit `ensure_binary()` call or an opt-in constructor flag. |
| Import and install | Offline and side-effect free. Enforced by `tests/test_import_hygiene.py`. |
| Execution | Argument lists, never shell strings. Explicit timeout, structured result carrying exit code and diagnostics, typed errors. |
| Errors | `UnsupportedPlatformError`, download, integrity, permission, timeout, cancellation and archive-failure types. |
| Options | A typed allowlist or an explicit sequence, never an opaque shell fragment. |
| `__version__` | Sourced from package metadata; no network at any point. |
| Extraction | Refuses members that escape the destination root; documented overwrite and partial-output policy. |

## Migration map

| Current | Becomes | Action for callers |
|---------|---------|--------------------|
| `from py7zip.py7zip import Py7zip` | unchanged | None. |
| `import py7zip` then `py7zip.Py7zip(...)` | still unsupported today; the package root exports nothing | Import from `py7zip.py7zip`. A root-level re-export may be added later as an *additive* change, not a break. |
| `Py7zip()` implicitly downloading a binary | explicit `ensure_binary()` | Call `ensure_binary()` where the download used to happen implicitly. |
| `Py7zip.__version__` from HTTP | package metadata; no network | No change for correct callers. Callers that relied on `"0.0.0"` as an offline sentinel must handle the metadata-backed value. |
| `wrapper(src, dst, options, method)` shell string | argv-based, typed options | Replace any free-text options string with the typed structure or explicit sequence. |
| Ignoring the return value of `compress` / `decompress` | a structured `ArchiveResult` | Inspect the result or catch the typed error; failures will no longer be silent. |
| `full`, `incremental`, `differential`, `snapshot` | removed | Stop calling them. They have never done anything. |
| `pip install py7zip` gaining a `py7zip-setup` console script | removed | The entry point called a bound instance method with no arguments and raised `TypeError` every time. It never worked. |
| `requests` as an install dependency | removed | The only consumer was the removed version probe. Nothing else in the package imports it. |

## Rules for changing this contract

1. A behaviour may only move from "current" to "target" when a test exists for
   both sides of the change.
2. Removing something that never worked is a correctness fix, not a break, and
   is recorded here with the reason it never worked.
3. No test may be weakened or deleted to make a contract change pass. The
   characterization tests are updated to the *new* documented contract in the
   same commit as the change, never silently.

## Recorded contract changes

Decisions made after the Phase 0 baseline, each with the commit that carried
it and the test that pins the new behaviour.

### 1. The safe runtime is the default (constructor `legacy=False`)

`Py7zip(verbose=False, debug=False, *, legacy=False, cache_dir=None,
binary_path=None, timeout=300.0)`. Without `legacy=True`, construction performs
platform detection only; `ensure_binary()` acquires a digest-verified artifact
explicitly; execution goes through the argument-list runtime
(`py7zip/safe.py`) returning `ArchiveResult` and raising the typed error
hierarchy. `legacy=True` keeps the Phase 0 behaviour (HTTP version probe on
construction, download into the package directory, `shell=True` execution,
`None` returns) as a migration path. Pinned by
`tests/test_characterization_wrapper.py`, `tests/test_safe_unit.py`, and
`tests/test_e2e_bundled.py`.

### 2. The five aliases forward `options` again

`compress`, `archive`, `backup`, `decompress`, and `extract` now pass the
caller's `options` through. In safe mode an opaque string (anything that is not
the empty default or `None`) is rejected with `TypeError` — individual switch
arguments are required. The Phase 0 silent-discard behaviour is gone. Pinned by
`tests/test_e2e_bundled.py::test_compat_api_rejects_string_options`.

### 3. `wrapper` returns a structured result in safe mode

The safe path returns `ArchiveResult` and raises typed errors instead of
swallowing failures; verbose diagnostics are printed only when requested. The
legacy path still prints and returns `None`, unchanged.

### 4. `full`, `incremental`, `differential`, `snapshot` are implemented

Instead of being removed, the four backup-family methods are implemented over
the argv runtime and covered end to end (deletion retention for incremental,
base-untouched plus two-step restore for differential, name stamping for
snapshot). Pinned by `tests/test_e2e_bundled.py::TestBackupModes` and
`tests/test_safe_unit.py::TestBackupModeConstruction`. The characterization
pin that documented the no-op stubs was replaced in the same commits that
implemented them, per rule 3.

### 5. The package root re-exports the public API (additive)

`import py7zip; py7zip.Py7zip()` now works: `py7zip/__init__.py` re-exports
`Py7zip`, `SafePy7zip`, `ArchiveResult`, the error hierarchy, and the
platform/acquisition types. This is the additive change the migration map
anticipated; `from py7zip.py7zip import Py7zip` is unchanged. Pinned by
`tests/test_import_hygiene.py`.

### 6. `requests` remains an install dependency

The migration map's "removed" row was not taken. Legacy mode still probes
`docs/CHANGELOG.md` over HTTPS, so `requests` stays a runtime dependency for
that path. Removing it requires deprecating the legacy version probe first.

### 7. A `py7zip` command-line interface is added (additive)

The package installs a `py7zip` console script and a `python -m py7zip`
entrypoint (`py7zip/cli.py`) exposing eight subcommands over `SafePy7zip`:
`download`, `compress`, `full`, `incremental`, `extract`, `list`,
`differential`, `snapshot`. The CLI is a thin dispatcher: it adds no runtime
behaviour of its own and cannot reach legacy mode. Exit codes are part of the
contract — `0` success, `1` archive execution or binary acquisition failure,
`2` usage error, `3` timeout, `4` refused unsafe archive members, `5`
unsupported platform — with errors printed as one `py7zip: ...` line on
stderr. Two supporting additions were made to `py7zip/safe.py`, both additive:
`SafePy7zip.list_entries()` (member listing on the safe runtime, pinned by
`tests/test_safe_unit.py`) and the module-level naming helpers
`snapshot_name()` / `differential_name()` used by both the runtime and the CLI
so the derived names cannot drift. Pinned by `tests/test_cli.py` (parser
surface, happy paths on the bundled binary, and every exit code) and
`tests/test_import_hygiene.py` (the entrypoints add no import-time I/O).


