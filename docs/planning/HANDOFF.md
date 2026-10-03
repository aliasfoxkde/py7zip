# py7zip handoff

**Evidence boundary (central audit):** branch
`audit/py7zip-qualification-20260909`, merged through `codex/py7zip-phase8-ci`
(HEAD `1bb3ea3` at the 100%-coverage milestone).
**Status:** active wrapper; safe runtime qualified on Linux x86-64, other
platforms remain receipt-pending.
**Rating:** 7/10 (advisory; not a production-readiness claim).

> **Current execution authority:** Use
> `/nas/Temp/repos/Platform-Architecture/docs/planning/HANDOFF_AUDIT_2026-08-13.md`
> and
> `/nas/Temp/repos/Platform-Architecture/docs/planning/CODEX_CLI_EXECUTION_PACKETS_2026-08-13.md`
> for cross-repository gates and bounded implementation sessions.

## Verified source facts

- The package declares MIT licensing and supports Python 3.9+ (`requires-python`,
  classifiers to 3.14; the wheel is pure Python).
- Importing the package performs no I/O and re-exports the public API
  (`Py7zip`, `SafePy7zip`, the typed error hierarchy, the artifact catalog).
- Construction performs platform detection only. Binary acquisition is the
  explicit `ensure_binary()` / `ArtifactManager.ensure()` operation.
- `full`, `incremental`, `differential`, and `snapshot` are implemented over
  the argument-list runtime and covered end to end (including the differential
  restore procedure and deletion retention semantics).
- Extraction refuses members that would escape the destination (zip-slip),
  proven against a real archive containing a `../` member.
- Historical documentation and release notes live under `docs/`; canonical
  future release notes belong under `.github/CHANGELOG.md`.

## Verified test and lint baseline

| Field | Value |
|-------|-------|
| Branch | `audit/py7zip-qualification-20260909` |
| Milestone commit | `1bb3ea3` — "test: full branch coverage and strict lint clean" |
| Host | Debian GNU/Linux 13, kernel `6.12.107+deb13-amd64`, `x86_64` |
| Python | CPython 3.13.5; pytest 9.0.2, ruff 0.16.2, coverage 7.13.4 |
| Binary provenance | `bin/lin/pc/x64/7za`, SHA-256 `12ef12519899ecda8ba59940d7f25a3f4818c97693538d49e894e6b783fb3081` (matches the catalog; banner "7-Zip (z) 24.00 (x64)") |
| Test command | `python3 -m pytest tests/ --cov=py7zip` (network-denied autouse fixture) |
| Result | 182 passed, 0 failed, 0 skipped; 100.0% line and branch coverage (444 stmts, 110 branches, 0 partial) against the `fail_under = 99` gate |
| Lint | `ruff check .` — zero findings; `ruff format .` — clean |
| Pattern scan | `aegis scan .` — zero true positives; every finding triaged as a false positive (test fixtures, hash-digest substrings, English prose) |

This does not qualify platforms other than Linux x86-64, and does not qualify
the PyPI publish path.

## Required next work

1. ~~Add deterministic unit tests without network access.~~ Done (offline
   characterization, unit, and e2e lanes).
2. ~~Replace shell-string subprocess execution with an argument-list
   boundary.~~ Done (`py7zip/safe.py`); legacy mode retains the shell string
   behind the explicit `legacy=True` migration flag.
3. ~~Decide whether `full`, `incremental`, `differential`, and `snapshot` are
   supported features.~~ Done: implemented and documented in USAGE.md.
4. Validate Linux (non-x86-64), macOS, and Windows from clean environments
   with provenance checks for acquired binaries. **Open.**
5. ~~Release automation: validate the CI/publish workflow through GitForge (the
   primary CI platform) before cutting a release.~~ **Done 2026-10-02** for the
   CI lanes: `.gitforge.yml` is registered (pipeline `py7zip-ci`) and run
   `bb76b684` graded commit `3252d397` green (`test` + `lint`, exit-code
   receipts). The PyPI publish lane remains open (see Phase P3 in
   `QUALIFICATION_PLAN_2026-09-29.md`).
6. ~~Command-line access: the package was library-only ("pythonic, not through
   the terminal") while the README advertised direct 7za use.~~ **Done
   2026-10-03** (`13fe83e`): a `py7zip` console script and `python -m py7zip`
   expose eight subcommands over the safe runtime with a typed exit-code
   contract (0/1/2/3/4/5), pinned by `tests/test_cli.py`; validated end to end
   from a clean venv against the built wheel (real dynamic download, digest
   verified; compress/list/extract; the backup family; the two-step
   differential restore via `-- -y`; direct `7za` invocation; live exit codes
   1/2/3). See `docs/USAGE.md` ("Command line") and COMPATIBILITY.md entries
   7–8.

## 0.9.0 validation findings (2026-10-03, wheel e2e on Linux x86-64)

Both defects below were found by driving the installed wheel, not by reading
source, and are fixed with pinning tests on the same commits.

1. **CLI switches could not be typed** (`ac2b034`). Every 7-Zip switch starts
   with `-`, so the `-o/--option` flag failed with argparse's
   missing-argument error for its entire purpose (`-o -y`, `-o -mx=9`);
   only `-o=-mx=9` parsed. Replaced by the `--` terminator 7-Zip itself
   documents; the tail reaches 7za verbatim. Pinned by
   `tests/test_cli.py::TestVerbatimSwitches`.
2. **`differential` failed on re-run** (`13fe83e`). 7za refuses to create the
   archive named in the `-u...!` switch when it exists (errno 17), so a
   second differential against the same base — the normal scheduled case —
   always failed on the file the previous call had written. The runtime now
   replaces a pre-existing diff, matching `compress`/`full`/`incremental`/
   `snapshot`, which all accept existing targets. Receipts: 7-Zip 24.00,
   Linux x86-64, Python 3.13.5. Pinned by
   `tests/test_safe_unit.py::TestDifferentialDiffReplacement` and
   `tests/test_e2e_bundled.py::TestBackupModes::test_differential_replaces_a_previous_diff`.
   Recorded as COMPATIBILITY.md entry 8.

Suite after both fixes: **206 passed**, 100.0% line and branch coverage
(552 statements, 132 branches), `ruff check .` and `ruff format --check .`
clean. Platform-side residual (not py7zip): GitForge's sqlite write
contention defers push-triggered CI inserts and the run trigger answers
`queued` with no run id while contention persists, so the GitForge CI run for
`13fe83e` was pending at handoff time; GitHub received the same commits.

## Promotion gate

A promotion receipt must name the exact commit, Python version, OS/architecture,
commands, binary provenance, test results, and any skipped platform lanes.
The Linux x86-64 receipt above satisfies the gate for this slice; no other
platform claim is promoted.
