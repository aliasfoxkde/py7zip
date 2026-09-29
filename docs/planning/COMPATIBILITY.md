# py7zip compatibility policy

This document states the public contract of `py7zip` as it stands at the
Phase 0 baseline, the contract the revamp is moving to, and the migration map
between them. It is written before the contract changes so that each break is
a recorded decision rather than an accident of refactoring.

The behaviour described in "current contract" is not asserted from reading
the source; every line is pinned by a test in `tests/`.

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
