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
5. Release automation: validate the CI/publish workflow through GitForge (the
   primary CI platform) before cutting a release. **Open.**

## Promotion gate

A promotion receipt must name the exact commit, Python version, OS/architecture,
commands, binary provenance, test results, and any skipped platform lanes.
The Linux x86-64 receipt above satisfies the gate for this slice; no other
platform claim is promoted.
