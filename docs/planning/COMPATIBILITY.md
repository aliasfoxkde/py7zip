# py7zip compatibility policy

This document states the public contract of `py7zip` as it stands at the
Phase 0 baseline, the contract the revamp is moving to, and the migration map
between them. It is written before the contract changes so that each break is
a recorded decision rather than an accident of refactoring.

The behaviour described in "current contract" is not asserted from reading
the source; every line is pinned by a test in `tests/`. Where a piece of
the target contract has already landed, it is recorded in place as its own
section, naming the decision that authorised it and the tests that pin it
— see "Options contract" below.

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
single `wrapper` method, and **all five forward the caller's `options`
argument unchanged, on both runtimes.**

At the Phase 0 baseline the aliases discarded `options`: each passed the
literal empty string to `wrapper`, so `obj.extract(a, b, options="-y")` ran
without `-y` (pinned then by
`test_aliases_silently_discard_the_callers_options`). When the
safe-by-default runtime landed (`4713a75`), the aliases changed to forward
`options` and the discard pin was replaced in that same commit, per rule 3,
by forwarding pins on both runtimes:
`tests/test_characterization_wrapper.py::test_legacy_aliases_forward_the_callers_options`
and, for the safe runtime,
`tests/test_default_api.py::test_default_aliases_require_individual_option_arguments`.
This PR adds
`tests/test_default_api.py::test_default_runtime_accepts_individual_option_arguments`
as a separate pin for the safe runtime's individual-argument contract.

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

* On the legacy runtime with string `options`, `wrapper` builds one shell
  string and passes it to `subprocess.run(..., shell=True)`; the caller's
  `options` text is interpolated verbatim, so it is interpreted by the
  shell. Sequence `options` are the exception on both runtimes: they run
  as an argument vector with `shell=False`, and the safe runtime never
  builds a shell string at all (see "Options contract" below).
* Source and destination are never validated. Nonexistent paths and paths
  containing `..` are passed through unchanged.
* Downloaded bytes are written to disk and marked `0o755` with no size bound,
  content check, or digest.
* `Py7zip.cd` changes the working directory of the entire process.

## Options contract (landed 2026-10-11 — audit decision D5 / OVH-16)

`options` is typed `str | Sequence[str]` with default `""` and means
different things on the two runtimes. Every row below is pinned by a test.

| Runtime | `options` value | Behaviour | Pinned by |
|--------|-----------------|-----------|-----------|
| Safe (default, `legacy=False`) — the supported runtime | `""` | No options are forwarded. | `tests/test_default_api.py::test_default_runtime_empty_string_options_are_empty_arguments` |
| Safe (default) | Sequence | Each element is forwarded as exactly one argv element to the no-shell runner; elements are never split or re-interpreted. | `tests/test_default_api.py::test_default_runtime_accepts_individual_option_arguments`; `tests/test_safe.py::test_runner_passes_an_argument_vector_without_shell` |
| Safe (default) | Any non-empty `str` (and `bytes`) | `TypeError("options must be a sequence of individual arguments")` raised before any subprocess starts. No `shlex` bridge exists — decision D5 rejects one because POSIX-mode `shlex` silently corrupts unquoted Windows backslashes (`"-oC:\Temp"`) and raises `ValueError` on an unbalanced quote. | `tests/test_default_api.py::test_default_runtime_shell_text_never_reaches_parsing_or_execution`; `tests/test_safe.py::test_runner_rejects_opaque_option_strings` |
| Legacy (`legacy=True`) — compatibility surface, slated for sunset | `str` | Interpolated verbatim into one shell string run with `shell=True` — the historical 0.6.x behaviour, shell word-splitting and command substitution included. Retained unchanged; the existing unsafe compatibility behaviour. | `tests/test_characterization_wrapper.py::test_options_are_appended_verbatim_to_the_command_string`, `::test_the_shell_word_splits_the_options_string`, `::test_options_are_evaluated_by_the_shell`, `::test_options_can_run_additional_commands` |
| Legacy (`legacy=True`) | Sequence | Forwarded element by element as an argument vector with `shell=False`; no element is re-interpreted by a shell. | `tests/test_characterization_wrapper.py::test_sequence_options_are_forwarded_as_an_argument_vector`, `::test_sequence_options_reach_the_binary_one_argument_each`, `::test_sequence_options_with_spaces_stay_one_argument` |

All five aliases forward `options` on both runtimes (see "Aliases" above).
The legacy string path is the retained unsafe compatibility surface; its
removal is governed by the legacy-sunset gate OVH-27 (audit decision D1),
implemented by OVH-19, which requires this options story to exist first.

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
| `wrapper(src, dst, options, method)` shell string | Safe runtime (default): `""` or a sequence of individual arguments; every non-empty string raises `TypeError` before any subprocess — decision D5 landed with no `shlex` bridge. Legacy runtime: strings keep the historical `shell=True` interpolation until the legacy sunset (OVH-27/OVH-19); sequences run as `shell=False` argv (OVH-16, landed 2026-10-11). | Pass options as a sequence of individual arguments (`["-y", "-mx=9"]`), or move to the default safe runtime where that is the only accepted form. `""` still means "no options" on both runtimes. |
| Ignoring the return value of `compress` / `decompress` | a structured `ArchiveResult` | Inspect the result or catch the typed error; failures will no longer be silent. |
| `full`, `incremental`, `differential`, `snapshot` | removed | Stop calling them. They have never done anything. |
| `Py7zip.cd` (process-wide `chdir`) | deprecated, then removed | Manage the working directory in caller code (`os.chdir` / `contextlib.chdir`) or pass explicit paths; `cd` mutates process-global state and is not part of the wrapper's archive contract. |
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
