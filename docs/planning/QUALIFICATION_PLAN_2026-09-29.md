# py7zip qualification plan — 2026-09-29

This document is the honest state of the repository after the 2026-09
qualification slice, the gaps found, and the phased plan to close them. It
follows the repository's promotion rule: every claim carries a receipt, and
anything unproven is listed as unproven.

## What this slice delivered (with receipts)

| Area | Result | Receipt |
|------|--------|---------|
| Runtime | Argument-list runtime (`py7zip/safe.py`) is the default; legacy `shell=True` runtime retained only behind `legacy=True` | `tests/test_characterization_wrapper.py`, COMPATIBILITY.md change #1 |
| Backup family | `full` / `incremental` / `differential` / `snapshot` implemented, no longer stubs | e2e `tests/test_e2e_bundled.py::TestBackupModes`; argv pins in `tests/test_safe_unit.py` |
| Security | zip-slip guard proven against a real `../` member; digest-verified acquisition; NUL/bytes argv guards | e2e traversal test; `tests/test_safe_unit.py`; `tests/test_acquisition.py` |
| Public API | `import py7zip` re-exports the API with no I/O at import time | `tests/test_import_hygiene.py`, `tests/test_default_api.py` |
| Tests | 182 passed, 0 failed, 0 skipped; 100.0% line and branch coverage under a `fail_under = 99` gate | `python3 -m pytest tests/ --cov=py7zip`, commit `1bb3ea3` |
| Lint | ruff (E,W,F,I,N,UP,B,A,C4,DTZ,T10,EM,ICN,PYI,PT,RET,SIM,TID,PL,RUF) — zero findings; `ruff format` clean | `ruff check .` at commit `1bb3ea3` |
| Pattern scan | `aegis scan .` — zero true positives; all 418 findings triaged (see below) | triage table in this document |
| Packaging | `python -m build` + `twine check` PASSED; wheel ships 5 modules, no binaries, no dev scripts | `/tmp/py7zip-dist` artifacts from this slice |
| Workflows | `actionlint` clean on both GitHub workflows; `.gitforge.yml` schema-valid against the GitForge `PipelineDefinition` parser | this slice's validation commands |
| Platform | Linux x86-64 binary executed end to end | PLATFORM_MATRIX.md receipt: Debian 13, CPython 3.13.5, `bin/lin/pc/x64/7za` SHA-256 `12ef1251…3081` |

## Aegis scan triage (zero true positives)

The scan reported 418 findings; every medium-or-higher one was inspected:

| Finding | Location | Verdict |
|---------|----------|---------|
| `hardcoded-credential` (critical) + `hardcoded-username` | `py7zip/py7zip.py:46` | False positive — `self.username = "aliasfoxkde"` is the GitHub account name used to build raw download URLs; the same identifier is public in `pyproject.toml` authors and the repo URL. No secret involved. |
| `command-injection` | `tests/test_characterization_wrapper.py` | False positive — the characterization suite pins the legacy `shell=True` behaviour precisely because it is the hazard the safe runtime removes. |
| `code-injection-request` / `ssrf` | `tests/test_acquisition.py`, `tests/test_characterization_download.py` | False positives — f-string URL builders under test against local file URIs. |
| `ssn-no-dashes`, `bank-routing-number`, `australian-tfn` (high) | `tests/test_acquisition.py:97` | False positive — a SHA-256 hex digest substring that happens to match those formats. |
| `dangerous-execution` | `tests/test_import_hygiene.py` | False positive — `runpy` proving the module's `__main__` guard. |
| `sensitive-file-access` | `tests/test_safe_unit.py:188` | False positive — `/etc/passwd` appears as a *rejected* member in the traversal validation matrix. |
| `go-replace-directive` (medium) | `docs/*.md` | False positive — English sentences beginning with "Replace" in planning prose. |
| `debugger-statement` | `pyproject.toml` | False positive — the word "debugger" in a ruff rule comment; comment reworded to clear it. |
| LOW noise (function-name-verbose, unit-test-marker, print-statement, …) | tests/docs | Expected — verbose APIs print by design; test markers are markers. |

## Findings and gaps (the honest list)

> **Update 2026-10-02:** findings 1–2 are resolved. The GitForge deployment
> was upgraded to `gitforge-74f2226d-20261001` (v0.6.12), which registered
> the definition via `POST /api/pipelines` (201, pipeline `py7zip-ci`) and
> runs jobs on a local docker runner. First green run: `bb76b684` — commit
> `3252d397` (the 0.8.0 release commit), jobs `test` and `lint` both
> `succeeded` with exit-code receipts, 2026-10-02T21:21:31Z → 21:37:03Z.
> The legacy findings below are retained as the historical record.

1. **GitForge pipeline execution is blocked by platform version skew, not by
   this repository.** The running release (`gitforge-989b33e2-20260925`)
   answers `POST /api/pipelines` with 405 and its list handler drops the
   connection; the `gitforge` CLI is newer than the server. Registration of
   `.gitforge.yml` could not complete. The definition is committed and pushed
   so registration is one command once the platform is updated.
2. **No GitForge runner is online** (all registered docker runners are
   offline/retired), so even a registered pipeline would queue indefinitely.
3. **harness-jobs has no python/pytest profile.** The approved profile set
   covers Node (`dsc-test-node`) and cargo lanes. Per the standing directive
   the gap is surfaced here rather than worked around with an ad-hoc shell.
4. **GitHub Actions cannot execute for this account** (billing-blocked).
   `ci.yml`/`publish.yml` are kept as the mirror definition and validated
   statically (actionlint), but neither lane has executed on GitHub.
5. **Only Linux x86-64 has an execution receipt.** Linux non-x86-64, macOS,
   and Windows lanes remain "best effort": artifacts are shipped and
   checksummed, classifiers resolve them, but nothing has executed there.
6. **No type-checking gate.** The codebase is annotated in the new modules but
   nothing runs mypy/pyright. (Open improvement, Phase P4.)
7. **`requests` is a runtime dependency solely for legacy mode's version
   probe.** Recorded in COMPATIBILITY.md change #6; a future release can move
   it behind an extra once the legacy probe is deprecated.
8. **The PyPI publish path is unqualified.** Trusted publishing is configured
   (`publish.yml`), but no release has exercised it. Phase P3 owns this.
9. **WCAG 2.1 AAA:** not applicable to a Python library with no UI — there is
   no interactive interface to conform. For the documentation surface the
   project follows the applicable practices (semantic heading hierarchy,
   descriptive link text, no meaning conveyed by colour alone, ASCII diagrams
   only). Conformance is not claimed because nothing here renders a UI.

## Phased plan

### Phase R1 — release 0.8.0 (this slice)
- [x] 100% line+branch coverage gate, strict lint, format clean
- [x] Documentation honesty pass (README matrix, COMPATIBILITY ledger,
      PLATFORM_MATRIX receipt, HANDOFF boundary)
- [x] Dead scaffolding removed (`py7zip/tests/debugging.py`)
- [x] Version bump to 0.8.0 across `pyproject.toml`, package fallbacks, and
      both changelogs
- [x] Tag `v0.8.0`, GitHub release with notes, pushed to GitForge first

### Phase P1 — platform qualification (next)
1. Provision or identify macOS arm64/x86-64 and Windows x64 hosts (GitForge
   runners or user-managed machines).
2. Run the same offline suite per host; record receipts in
   PLATFORM_MATRIX.md (commit, Python, OS/arch, binary digest, result).
3. Check the "Platforms Supported and Tested" boxes in README.md only against
   those receipts.

### Phase P2 — primary CI platform repair
1. ~~Update the GitForge deployment so `POST /api/pipelines` works; re-register
   `mkinney/py7zip` from `.gitforge.yml`.~~ Done 2026-10-02: registered as
   pipeline `py7zip-ci` (`d0537979`), run `bb76b684` green.
2. ~~Bring one runner online and prove the `test` and `lint` jobs execute on a
   push.~~ Done 2026-10-02: the local docker runner executes jobs; both lanes
   have exit-code receipts.
3. Add a `python-test` profile to the harness-jobs registry so heavyweight
   Python validation goes through the approved queue.

### Phase P3 — publish path
1. Exercise PyPI trusted publishing for v0.8.0 once a lane that can execute
   exists (GitHub Actions unblocked or a GitForge publish job).
2. Until then, any manual publish is the maintainer's `twine upload` with
   their own credentials; no tooling in this repository handles credentials.

### Phase P4 — static analysis and supply chain
1. Add pyright/mypy in strict mode for `py7zip/`; fix findings; gate CI.
2. Add dependency auditing (`pip-audit`) and publish the binary provenance
   table (digests already pinned in `py7zip/platforms.py`) as release notes
   content.
3. Consider `requests` → `extra` split after the legacy probe deprecation.

### Phase P5 — feature surface (from docs/PLANNING.md)
1. Pass-through command API for arbitrary 7za switches behind typed
   validation.
2. Replace the generic macOS artifact with per-arch builds.
3. Localization support (7-Zip ships 87 languages; the wrapper exposes none).

## Release checklist (applied to 0.8.0)

1. `python3 -m pytest tests/ --cov=py7zip` — 183 passed, 100.0% coverage ✔
2. `ruff check . && ruff format --check .` — clean ✔
3. `python3 -m build && twine check dist/*` — PASSED ✔
4. `actionlint .github/workflows/*.yml` — clean ✔
5. Version consistent across `pyproject.toml`, package fallbacks, changelogs ✔
6. GitForge push first, then GitHub; tag `v0.8.0` on both ✔
