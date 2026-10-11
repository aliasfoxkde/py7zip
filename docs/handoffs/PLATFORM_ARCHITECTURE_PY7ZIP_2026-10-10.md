# Platform Architecture handoff — aliasfoxkde/py7zip — 2026-10-10

**Status:** active handoff for execution planning. Docs-only slice; no runtime code changed here.
**Supersedes for execution planning:** `docs/planning/HANDOFF.md` (2026-08-13 audit, whose
"execution authority" paths point at `/nas` and are not readable from this checkout).
**Task ledger:** `docs/PLANNING.md` (annotated in the same commit as this file; it stays canonical).

Evidence labels used below: **OBSERVED** (read directly from this checkout, CI, GitHub, or PyPI on
2026-10-10), **INFERRED** (conclusion drawn from OBSERVED facts, reasoning shown), **UNKNOWN**
(no authoritative evidence available; an investigation task exists).

## 1. Evidence boundary

| Field | Value | How verified |
|---|---|---|
| Branch | `codex/pa-handoff-py7zip-20261010` | `git branch --show-current` |
| HEAD | `9d428da` ("ci: harden test and release workflows", 2026-09-01) | `git log` |
| vs. `origin/main` | identical SHA `9d428da…` at time of writing | `gh api repos/aliasfoxkde/py7zip/commits/main` |
| Working tree | clean (0 dirty entries) | `git status` |
| Filesystem | NVMe (`/dev/nvme0n1p2`, ext4) — not `/nas` | `findmnt -T "$PWD"` |
| Suite runs | **none** (docs-only task; the offline suite runs in CI on every PR) | this slice's command log (§9) |

Per repository guidance (`AGENTS.md`), no platform-support claim in this document is based on
source inspection alone; unexecuted combinations are labeled best effort or UNKNOWN.

## 2. Package purpose (the contract this handoff protects)

py7zip is a Pythonic wrapper that detects the host platform, obtains the matching upstream 7-Zip
(`7za`) executable, and invokes it for archive operations (`AGENTS.md` "Scope"; `README.md`).
Non-negotiables from `AGENTS.md`: preserve the public `Py7zip` API and MIT license for the
wrapper; keep 7-Zip upstream license notices with any distributed binary; never claim platform
support without a recorded receipt (exact Python/OS/arch/provenance/result).

## 3. Current-state scorecard

Ratings are advisory engineering judgments over OBSERVED evidence; they are not
production-readiness claims (see `docs/planning/PLATFORM_MATRIX.md` for the same caveat).

| Dimension | Rating | Basis |
|---|---|---|
| Purpose fit (detect / obtain / safely invoke 7za) | **Partial** | Safe runtime does all three (`py7zip/safe.py`, `py7zip/acquisition.py`, `py7zip/platforms.py`) but legacy runtime and stale facade helpers contradict it (F2, F5) |
| Binary acquisition integrity | **Partial** | Checksum + size bound + atomic replace + lock (`py7zip/acquisition.py:53–166`), but hashes are self-declared in the same repo (TOFU); no upstream provenance (F7); legacy path writes unverified bytes (`py7zip/py7zip.py:131–145`) |
| Archive execution safety | **Good (default path)** | argv-only, no shell, timeout, typed errors (`py7zip/safe.py:50–121`); traversal member validation (`py7zip/safe.py:124–144`); limits noted in F12 |
| Public API compatibility | **Good, with friction** | `Py7zip` signature preserved; safe runtime default since commit `4713a75`; string-options now raise `TypeError` by design (F4) |
| Packaging / distribution | **Weak** | pyproject is modern, but PyPI's latest published release is **0.6.2** — the safe runtime has never shipped to pip users (F3) |
| Release automation | **Adequate, unproven** | Trusted publishing with tag/version gate (`.github/workflows/publish.yml:28–38`); no release has exercised it (0.7.3 unpublished, F3) |
| Tests | **Good** | 88 offline test functions across 10 files; network-denial enforced in `tests/conftest.py:43–52`; catalog-vs-artifact digest check (`tests/test_acquisition.py:85`) |
| CI coverage | **Partial** | 3.9–3.13 on ubuntu only (`.github/workflows/ci.yml:18–22`); no Windows/macOS lane; 3.14 classifier untested in CI (F9) |
| Documentation truthfulness | **Weak** | `docs/USAGE.md`, `docs/FEATURES.md`, `docs/SETUP.md` describe behavior that no longer exists or never worked (F6); README install-note wrong for current packaging (F13) |
| Security policy | **Absent** | No `SECURITY.md` / `CONTRIBUTING.md` in repo (F11) |

## 4. Baseline — what is (OBSERVED)

### 4.1 Runtime architecture: dual-runtime facade

`Py7zip.__init__` (`py7zip/py7zip.py:19–76`) selects between two runtimes:

- **Safe runtime (default, `legacy=False`)** — constructs `SafePy7zip` (`py7zip/safe.py:155–177`).
  Construction performs platform detection only; no download, no process start. Binary acquisition
  is explicit (`ensure_binary`, `py7zip/safe.py:171–177`) into `~/.cache/py7zip` by default.
- **Legacy runtime (`legacy=True`)** — the historical behavior: network version probe via
  `requests` (`py7zip/py7zip.py:85–115`), download of an unverified binary into the package
  directory (`py7zip/py7zip.py:72–74, 131–145`), and `subprocess.run(..., shell=True)` with an
  interpolated command string (`py7zip/py7zip.py:166–176`).

### 4.2 Platform catalog and artifact integrity

`py7zip/platforms.py` normalizes host identity without I/O (`PlatformInfo.detect`, lines 31–79)
and resolves it against a catalog of exactly 7 artifacts with pinned SHA-256 and size
(`ArtifactCatalog._ARTIFACTS`, lines 95–106). Windows/ARM resolves to a typed refusal
(`tests/test_platforms.py:65`).

Independently verified in this slice: `sha256sum` of all files under `bin/` matches the catalog
7/7; the other 6 `bin/` entries (`bin/win/arm/*`, `bin/mac/pc/*`, `bin/mac/arm/*`) are 0-byte
placeholders the catalog correctly excludes.

### 4.3 Acquisition

`ArtifactManager` (`py7zip/acquisition.py`) downloads from
`https://github.com/aliasfoxkde/py7zip/raw/main` (base URL injectable, line 40) with: streaming
size bound (lines 84–87), SHA-256 + size verification before publish (lines 101–114), `0o755`
chmod and atomic `os.replace` (lines 91–92), destination-escape check (lines 116–122), and a
cache lock with stale-owner recovery via recorded PID liveness (lines 124–166).

### 4.4 Safe execution

`ArchiveRunner` (`py7zip/safe.py:41–121`): argv-only (`shell=False`), positive-timeout enforced,
structured `ArchiveResult` with returncode/stdout/stderr, typed errors
(`ArchiveExecutionError`/`ArchiveTimeoutError`), NUL-byte rejection. `decompress` lists members
via 7-Zip's `-slt -ba` machine output and rejects absolute/traversal members before extraction
(`validate_archive_members`, lines 124–144; `SafePy7zip.decompress`, lines 199–207).

### 4.5 Tests

88 test functions across `tests/` (counted via `grep "def test_"`); many are parametrized so the
collected case count is higher. `tests/conftest.py:43–52` turns any socket use into a failure
(autouse), plus cwd-restore and package-tree snapshot fixtures. Characterization tests pin the
legacy runtime's exact shell semantics (`tests/test_characterization_wrapper.py:186–214`),
including proof that options strings are shell-evaluated (`test_options_can_run_additional_commands`,
line 214). The suite ran green at 89 cases in the recorded Phase-0/1 slice
(`docs/planning/PLATFORM_MATRIX.md:77–88`, CPython 3.14.6 / Fedora 44); it was **not** executed in
this slice.

### 4.6 CI and release automation

- `ci.yml`: pytest (offline) on Python 3.9–3.13, ubuntu-latest only; separate wheel build +
  `twine check` job.
- `publish.yml`: triggers on published release or manual dispatch; verifies the tag matches
  `pyproject.toml` version; publishes via PyPI trusted publishing (`id-token: write`,
  `pypa/gh-action-pypi-publish@release/v1`). Only fires the publish step for release events.

### 4.7 Packaging

`pyproject.toml`: version **0.7.3**, `requires-python >=3.9`, single runtime dependency
`requests`, `Development Status :: 1 - Planning`, classifiers 3.9–3.14, wheel includes only
`py7zip*` packages (line 38–39) — **no `bin/` data ships in the wheel**; binaries are obtained at
runtime. PyPI (checked 2026-10-10): latest published version **0.6.2** (releases 0.3.0–0.6.2,
`requires_python >=3`) — so 0.7.3 has never been published (F3).

## 5. Findings

| # | Severity | Finding | Evidence |
|---|---|---|---|
| F1 | High (truthfulness) | Platform-support claims conflict. README's checklist marks Windows x64 tested (`README.md:55`); `docs/CHANGELOG.md:17` claims 0.7.3 was tested on "Linux (Ubuntu through WSL)"; `docs/planning/PLATFORM_MATRIX.md` records zero real-binary executions on any host. `AGENTS.md` promotion rule requires receipts. Whether a Windows/WSL receipt exists is **UNKNOWN** (D4). | Files cited; no receipts found in repo |
| F2 | Medium (defect) | `Py7zip.get_binary_url()` on the default runtime returns `f"{cache_dir}/{spec.relative_path}"` — a path that never exists (acquisition writes `cache_dir/<exe name>`, `py7zip/acquisition.py:56`) and is not a URL. Latent: nothing internal calls it on the safe path. | `py7zip/py7zip.py:147–151` |
| F3 | High (distribution) | pip users receive **0.6.2** — the legacy runtime with `shell=True` option-string execution and unverified binary download. All safe-runtime work (commits `7661132..9d428da`, 2026-09-01) is GitHub-only. `docs/PLANNING.md:47` "actions not automatically updating PyPi" is confirmed live. | PyPI JSON API, 2026-10-10; `pyproject.toml:7` |
| F4 | Medium (compat friction) | On the default runtime, string `options` raise `TypeError` ("options must be a sequence of individual arguments"). Pinned intentionally (`tests/test_default_api.py:26–30`; `py7zip/safe.py:60–61`), but every legacy caller that passed an options string breaks loudly. Needs a decision (D5), not silent re-introduction of shell text. | Files cited |
| F5 | Medium (API debt) | `full`/`incremental`/`differential`/`snapshot` are public no-op stubs and `cd` mutates process-global cwd — all still shipped. `docs/planning/COMPATIBILITY.md:44–49,84` schedules their removal ("Phase 4"), not yet executed. | `py7zip/py7zip.py:127–129, 208–219`; `tests/test_characterization_wrapper.py:301–312` |
| F6 | Medium (docs) | `docs/USAGE.md:2–15` instructs `import py7zip; py7zip.Py7zip()` — impossible: the package root exports nothing (pinned by `tests/test_import_hygiene.py:104–123`; `py7zip/__init__.py` is empty). `docs/FEATURES.md:3–4` advertises snapshot/incremental features that are stubs. `docs/SETUP.md` documents a `push.bat` + `PYPI_API_KEY` + `python setup.py sdist bdist_wheel` flow; `setup.py` does not exist and publishing is trusted-publishing based. | Files cited |
| F7 | High (provenance) | No recorded upstream provenance for any shipped artifact: `bin/INFO.md` lists paths only, no 7-Zip version or source. Catalog SHA-256s anchor integrity to self-declared values checked into the same repository (trust-on-first-use), not to official 7-Zip releases. Issue #7 explicitly demands verification against official 7-Zip checksums. Which upstream versions these binaries correspond to is **UNKNOWN** (P0.4/P2.1). | `bin/INFO.md`; `py7zip/platforms.py:95–106`; issue #7 body |
| F8 | Low (dependency) | `requests` is installed by every consumer solely so the legacy runtime can fetch `docs/CHANGELOG.md` over HTTPS for `__version__` (`py7zip/py7zip.py:9, 93`). The safe runtime uses stdlib only. Drop when legacy retires (P1.5). | Files cited |
| F9 | Medium (CI) | Test matrix is ubuntu-only although the suite is offline and OS-portable; no Windows/macOS lane catches path/`os.replace`/`shutil` regressions. Python 3.14 is advertised by classifier (`pyproject.toml:30`) but absent from the CI matrix (3.9–3.13). | `.github/workflows/ci.yml:18–22` |
| F10 | Low (docs drift) | `docs/planning/COMPATIBILITY.md:30–35` states "Every alias discards the caller's `options` argument". Current source forwards `options=options` in all five aliases (`py7zip/py7zip.py:188–206`) and the current suite pins "legacy aliases forward the caller's options" (`tests/test_characterization_wrapper.py:266`). The Phase-0 description no longer matches the code it describes. | Files cited |
| F11 | Medium (policy) | No `SECURITY.md`, `CONTRIBUTING.md`, or `CODE_OF_CONDUCT` anywhere in the repo — for a package whose whole security story is "how binaries are acquired and executed". | `ls .github/` (only `CHANGELOG.md`, `workflows/`) |
| F12 | Medium (safety limit) | Extraction safety validates member *names* only (`py7zip/safe.py:124–144`). Symlink/special-file members, overwrite behavior, and partial-output-on-failure policy are neither handled in code nor documented. Do not claim "safe extraction" beyond traversal-name rejection until investigated (P2.4). | File cited; no doc statement found |
| F13 | Low (docs) | README's install note ("when using `pip install` … only the binary for the given system is included", `README.md:60–62`) is wrong for current packaging: the wheel ships no binaries at all (`pyproject.toml:38–39`); acquisition downloads at runtime. | Files cited |
| F14 | Low | `Project Page` = `https://py7zip.cyopsys.com` (`pyproject.toml:36`): `curl -sI` returned exit 0 with an **empty header block** on 2026-10-10 — not a usable page. Matches the open bug in `docs/PLANNING.md:46`. | This slice's command log (§9) |

## 6. Relationship to open PR #8 (`webbrain/issue-7`)

**OBSERVED PR facts** (via `gh`, 2026-10-10): OPEN, not draft, `mergeable: CONFLICTING`; head
`f75ec5d` on fork `webbrain-one/py7zip`, branch `webbrain/issue-7`; single commit; touches **only**
`py7zip/py7zip.py`; body closes issue #7 ("support local 7zip installations, instead of
downloading and running unchecked binaries directly from this Git repo"). CI state: **no test or
workflow checks reported** on the PR — the only passing check is the CodeRabbit review bot. Its
diff context shows the pre-revamp `py7zip.py` (no `legacy` flag, old URL construction), i.e. it is
based on a `main` that predates commits `7661132..9d428da`.

**What the diff does:** adds `_find_local_7zip()` (PATH lookup of `7za`/`7z` via `shutil.which`,
then `Program Files/7-Zip` on Windows and `/usr/bin`, `/usr/local/bin`, `/opt/homebrew/bin`
elsewhere, falling back to the bundled package-dir path) called from `__init__`; converts
`wrapper()` from a `shell=True` string to an argv list; appends `options.split()`; keeps
`check=True`.

**Overlap with current `main`:** the argv conversion is already superseded by `py7zip/safe.py`
(no shell, timeout, typed errors, traversal guard). Two ideas in PR #8 / issue #7 are **not**
yet on `main` and retain value: (a) prefer a locally installed 7-Zip before downloading;
(b) anchor binary integrity to official 7-Zip release checksums rather than self-declared repo
hashes (F7).

**Recommendation (INFERRED):** do not merge as-is. Merging would clobber the safe-runtime facade
(conflict against `9d428da`), reintroduce uncaught `CalledProcessError` (`check=True` changes the
documented return-`None` contract of `wrapper`), and `options.split()` silently mangles options
containing quoted paths. Also, `_find_local_7zip()` performs filesystem I/O in `__init__`,
contradicting the construction contract pinned by `tests/test_safe.py:77–82`. Instead: re-work the
discovery idea behind an explicit, tested API (P1.4), respond on #7 with the provenance plan
(P0.4), then close PR #8 as superseded or ask its author to rebase onto the facade.

## 7. Phased execution plan

Conventions: each task is independently shippable; "Owner" is a role, not a person. Validation
commands are runnable locally on the NVMe checkout; nothing here requires running the full suite
on `/nas`. Per `docs/planning/COMPATIBILITY.md:88–96`, any contract change lands with its
characterization-test update in the same commit.

### P0 — stop the bleeding (correctness of shipped claims and artifacts)

**P0.1 Reconcile platform-support claims** — Owner: Maintainer + Docs. Dependencies: D4.
Files: `README.md` (lines 49–62), `docs/CHANGELOG.md`, `docs/planning/PLATFORM_MATRIX.md`.
Deliverable: one consistent claim set. Every "tested" box either cites a receipt row (exact
Python/OS/arch/binary provenance/result per `AGENTS.md`) or is unchecked with "receipt required".
Validation: `grep -n "\[x\]" README.md` returns only rows backed by a matrix receipt.
Acceptance: zero tested-claims without receipts; README install note matches actual wheel
contents (fixes F13, F1). Risk: reputational only; rollback = revert commit.

**P0.2 Truth-pass on user-facing docs** — Owner: Docs. Dependencies: none.
Files: `docs/USAGE.md`, `docs/FEATURES.md`, `docs/SETUP.md`.
Deliverable: USAGE example rewritten to `from py7zip.py7zip import Py7zip` plus the safe-runtime
sequence (construct → optional `ensure_binary()` → `compress`/`decompress` returning
`ArchiveResult`); FEATURES labels `full`/`incremental`/`differential`/`snapshot` as unimplemented
or drops them; SETUP describes the `publish.yml` trusted-publishing flow and deletes the
`setup.py`/`PYPI_API_KEY` instructions. Validation: run each documented snippet's import line in a
clean interpreter (`python -c "from py7zip.py7zip import Py7zip"`). Acceptance: every command in
docs executes as written on the default runtime; no doc references `setup.py` or `push.bat` as
current process (fixes F6). Risk: none; rollback = revert.

**P0.3 Fix or deprecate `get_binary_url()` safe path** — Owner: Implementation agent.
Dependencies: none. Files: `py7zip/py7zip.py:147–154`; new test in `tests/test_default_api.py`.
Deliverable: the safe branch either returns the real catalog source URL
(`{base_url}/{spec.relative_path}` semantics) or the method is documented as legacy-only and
delegates to `ensure_binary()`; behavior pinned by a test either way (fixes F2).
Validation: `python -m pytest tests/test_default_api.py -q` plus the offline suite in CI.
Acceptance: no default-runtime code path returns a nonexistent path as a URL; characterization
tests unchanged unless the contract changes. Risk: API change → keep the legacy branch
byte-identical; prefer deprecation over behavior change.

**P0.4 Artifact provenance ledger + SECURITY.md** — Owner: Maintainer (security hat).
Dependencies: none; blocks P2.1. Files: `bin/INFO.md` (or a new `bin/PROVENANCE.md`), new
`SECURITY.md`. Deliverable: for each of the 7 non-empty artifacts: upstream 7-Zip version,
where obtained, upstream-published checksum cross-reference, and date — or an explicit UNKNOWN
row; a security policy stating how binary-provenance reports are handled. Validation: manual
review; every non-empty `bin/` file has a row. Acceptance: no artifact ships without either an
upstream anchor or a recorded UNKNOWN + investigation task (starts F7; partially answers #7).
Risk: the provenance answer may force re-acquisition of binaries (then P2.1 executes that);
rollback = revert docs.

**P0.5 Publication decision for 0.7.3** — Owner: Maintainer/Release. Dependencies: P0.1, P0.2;
D3. Files: none required (tag + `pyproject.toml` version already aligned; `.github/CHANGELOG.md`
"Unreleased" section must be finalized). Deliverable: either (a) publish `v0.7.3` and record the
receipt, acknowledging pip users currently get legacy 0.6.2 with `shell=True`, or (b) a recorded
decision + dated issue explaining the delay. Validation: `python -m build && twine check dist/*`
locally; CI green on the release commit; `publish.yml` tag gate passes.
Acceptance: PyPI latest is no longer 0.6.2, or a dated decision record exists (fixes F3's
indefinite drift). Risk: publishing is effectively irreversible — treat (a) as gated on P0.4's
provenance row not contradicting the shipped binaries; rollback not available post-publish (yank
only).

### P1 — finish the migration (API completion, PR #8 disposition)

**P1.1 Options-bridge decision and implementation** — Owner: Implementation agent. Dependencies:
D5. Files: `py7zip/py7zip.py` (`wrapper`, lines 156–164), `py7zip/safe.py` (no change if
documented), `tests/test_default_api.py`, `docs/planning/COMPATIBILITY.md` migration map row.
Deliverable: either keep `TypeError` and document it in `docs/USAGE.md`, or bridge legacy string
options via `shlex.split` **behind an explicit opt-in** (e.g. `Py7zip(legacy_options=True)`), never
implicitly. Acceptance: behavior pinned by tests; COMPATIBILITY updated in the same commit
(addresses F4 without reintroducing shell semantics). Validation: `pytest tests/test_default_api.py
tests/test_safe.py -q`. Risk: silent misparsing of legacy strings if bridged wrong — mitigation:
opt-in flag + tests with quoted-path cases. Rollback: revert single commit.

**P1.2 Snapshot-family and `cd` disposition** — Owner: Implementation agent. Dependencies: none.
Files: `py7zip/py7zip.py:127–129, 208–219`, `tests/test_characterization_wrapper.py:301–347`,
`docs/planning/COMPATIBILITY.md`. Deliverable: execute the already-recorded decision — remove the
four stubs and deprecate/remove `cd` (or convert to a context manager), updating the
characterization tests in the same commit per the contract rules. Acceptance: public surface
contains only implemented behavior; `python -c "from py7zip.py7zip import Py7zip;
[hasattr(Py7zip, m) for m in ('full','incremental','differential','snapshot')]"` returns all
False. Validation: full offline suite in CI. Risk: breaking no-op callers — mitigated by the
COMPATIBILITY note that they never did anything; changelog entry required
(`.github/CHANGELOG.md`). Rollback: revert.

**P1.3 Root re-export (additive)** — Owner: Implementation agent. Dependencies: P1.2 (so the
exported surface is final). Files: `py7zip/__init__.py`, `tests/test_import_hygiene.py:104–123`
(updated in same commit), `docs/USAGE.md`. Deliverable: `py7zip.Py7zip` and `py7zip.__version__`
exported, keeping import side-effect-free; the pinned hygiene test is updated to the new
documented contract, never weakened silently. Acceptance: `python -c "import py7zip;
py7zip.Py7zip"` works in a clean interpreter with no network (assert via the existing probe
pattern). Validation: `pytest tests/test_import_hygiene.py -q`. Risk: low; additive per the
migration map (`docs/planning/COMPATIBILITY.md:79`). Rollback: revert.

**P1.4 Local-binary discovery, reworked from PR #8** — Owner: Implementation agent.
Dependencies: D2; supersedes PR #8 (P1.6). Files: `py7zip/safe.py` (new explicit resolver, e.g.
`SafePy7zip(binary_path="auto")` or a `discover_local_7zip()` helper mirroring PR #8's search
list), `py7zip/py7zip.py` (facade passthrough), `tests/test_safe.py`. Deliverable: opt-in
discovery with documented precedence (see D2); performed at `ensure_binary()` time, never in
`__init__`; a discovered binary is integrity-checked against the catalog when its digest is
known, and treated as user-supplied (skip catalog check, document trust implication) when it is
not. Acceptance: offline unit tests with a fake `PATH` prove (1) default runtime never searches
or downloads implicitly, (2) discovery finds `7za`/`7z` in precedence order, (3) no catalog-
verifiable binary is executed unverified when verification is requested. Validation:
`pytest tests/test_safe.py tests/test_default_api.py -q`; then close PR #8 referencing this task.
Risk: trusting a user-writable PATH binary is a policy decision — hence D2 precedes code.
Rollback: revert; the flag defaults to off.

**P1.5 Legacy runtime sunset** — Owner: Maintainer + Implementation agent. Dependencies: D1;
P1.1 (callers have a documented options story). Files: `py7zip/py7zip.py:42–76, 85–154`,
`pyproject.toml:15–17` (drop `requests`), `docs/planning/COMPATIBILITY.md`,
`.github/CHANGELOG.md`. Deliverable: deprecation warning on `legacy=True` with a stated removal
version; on removal, delete the HTTP version probe and the `requests` dependency in the same
commit (fixes F8). Acceptance: `pip install py7zip` in a fresh venv pulls no `requests` once
removed; grep shows no `import requests` under `py7zip/`. Validation: `python -m pytest tests -q`
plus `python -m build` (dependency metadata change). Risk: breaking legacy users — mitigated by
the deprecation window (length = D1) and the fact that the safe runtime is already default.
Rollback: revert; keep the deprecation-warning commit even if removal slips.

**P1.6 PR #8 / issue #7 disposition** — Owner: Maintainer. Dependencies: P1.4 merged (or
explicitly rejected). Deliverable: comment on #7 linking P0.4's provenance ledger and P1.4's
discovery task; then close PR #8 as superseded (or request rebase if the author prefers to
deliver P1.4 themselves). Acceptance: both the PR and the issue have a response naming the
replacement tasks; PR state reflects the decision. Risk: community friction — mitigation: credit
the author's analysis; the diff's ideas are adopted in reworked form. Rollback: n/a (comment
only).

### P2 — qualification and hardening

**P2.1 Upstream-anchored artifact pipeline** — Owner: Maintainer + QA. Dependencies: P0.4.
Files: `py7zip/platforms.py:95–106` (catalog), `bin/` refresh, `py7zip/acquisition.py:40`
(base URL), `bin/PROVENANCE.md`. Deliverable: each artifact re-derived from a named official
7-Zip release with the upstream SHA-256 recorded beside the repo-pinned hash (fixes F7's TOFU
gap; the heart of issue #7). Consider serving binaries from GitHub release assets instead of
`raw/main` (the base URL is already injectable, making this a data change). Acceptance: every
catalog entry cites an upstream release URL + upstream checksum; a documented re-derivation
procedure reproduces each artifact hash. Validation: `sha256sum bin/**/*` vs catalog + provenance
rows; `pytest tests/test_platforms.py tests/test_acquisition.py -q`. Risk: current binaries may
fail upstream anchoring (UNKNOWN until P0.4) — contingency: rebuild/replace artifacts and bump
catalog hashes in one reviewed commit. Rollback: revert catalog/artifact commit.

**P2.2 Multi-OS CI lanes and Python 3.14 alignment** — Owner: Maintainer (CI). Dependencies:
none. Files: `.github/workflows/ci.yml`. Deliverable: add `windows-latest` and `macos-latest`
runs of the same offline suite (it is network-denied and fixture-based, so no downloads occur);
either add 3.14 to the matrix or drop the 3.14 classifier until tested. Acceptance: green CI
lanes on all three OSes at the matrix's Python versions; classifier set == tested set.
Validation: workflow run history on the PR. Risk: Windows path-normalization failures in
`validate_archive_members`/lock code are *possible* — that is the point; fix forward (they are
real cross-platform defects). Rollback: revert workflow change (no runtime impact).

**P2.3 Platform qualification receipts** — Owner: QA/Release. Dependencies: P2.1, P2.2.
Files: `docs/planning/PLATFORM_MATRIX.md` (evidence record section), `.github/CHANGELOG.md`.
Deliverable: execute real 7za archive create/extract on each claimed host combination and record
exact Python/OS/arch/binary provenance/commands/results per the `AGENTS.md` promotion rule;
promote matrix rows from "Best effort" to "Tested" only with receipts. Acceptance: README
checklist and matrix tiers agree with recorded receipts; unexecuted rows explicitly say so.
Validation: receipts are the validation. Risk: some combinations will fail (e.g. the 0-byte
placeholder paths) — record honestly; those become catalog refusals, not silent support claims.
Rollback: n/a (records only).

**P2.4 Extraction-safety completion** — Owner: Implementation agent + Maintainer (security hat).
Dependencies: none; informs docs claims. Files: `py7zip/safe.py:124–144`, `docs/FEATURES.md` or a
new safety doc. Deliverable: decide and document the policy for symlink members, overwrites, and
partial output on failure; implement what is feasible (e.g. post-extraction link audit or
documented restriction) or explicitly scope the guarantee to "member-path traversal rejection"
(fixes F12's over-claim risk). Acceptance: a written policy plus tests for any new check; USAGE
states exactly what is and is not guaranteed. Validation: `pytest tests/test_safe.py -q` plus any
new test file. Risk: low (may be docs-only); rollback: revert.

**P2.5 Release hygiene** — Owner: Maintainer. Dependencies: D3. Files: `pyproject.toml:36`
(Project Page), `.github/CHANGELOG.md`, `docs/CHANGELOG.md` (historical, frozen).
Deliverable: fix or drop the dead `Project Page` URL (F14); keep `.github/CHANGELOG.md` as the
canonical forward log per `AGENTS.md`; optionally single-source the version so the
`publish.yml` tag gate cannot drift. Acceptance: no dead URLs in package metadata; release
process documented in one place (replaces `docs/SETUP.md`'s stale flow). Validation:
`python -m build && twine check dist/*`; render README/PyPI metadata. Risk: minimal; rollback:
revert.

## 8. How the overhaul replaces the current design without a big bang

The strangler pattern is already in place and this plan only completes it:

1. **The facade is the seam.** `Py7zip` keeps its constructor signature and method names while
   defaulting to the safe runtime (commit `4713a75`). Nothing that imports `py7zip.py7zip.Py7zip`
   changes during P0–P2; behavior under the default runtime improves in place.
2. **Characterization tests are the ratchet.** The legacy runtime's exact semantics are pinned by
   tests (`tests/test_characterization_wrapper.py`), and `docs/planning/COMPATIBILITY.md` records
   each planned break with its migration row. Every task above moves one row from "current" to
   "target" with both sides tested in the same commit — no behavioral drift without a record.
3. **Acquisition is already injectable.** `ArtifactManager(base_url=…)` (`py7zip/acquisition.py:40`)
   means P2.1's move from `raw/main` to release assets (or any mirror) is a data/catalog change,
   not a caller change.
4. **Legacy dies by flag, then by deletion.** P1.5 keeps `legacy=True` working through a
   deprecation window; the deletion commit is small because the facade has long since stopped
   calling it on the default path. `requests` leaves in that same commit.
5. **PR #8's idea lands re-based, not merged.** Discovery enters as an opt-in, tested capability
   (P1.4) instead of a conflicting rewrite of the file it targeted.

At no point does a consumer of the documented API face a flag-day: the only intentional breaks
(stub removal, options-string `TypeError`) are ones the compatibility policy already schedules
and the characterization suite already fences.

## 9. Validation performed in this slice (actual commands and outcomes)

| Command | Outcome |
|---|---|
| `git status` / `git branch --show-current` | clean tree; branch `codex/pa-handoff-py7zip-20261010` |
| `findmnt -T "$PWD"` | `/dev/nvme0n1p2` ext4 (NVMe; no `/nas` involvement) |
| `git log --oneline -5` | HEAD `9d428da`; safe-runtime series dated 2026-09-01 |
| `gh api repos/aliasfoxkde/py7zip/commits/main` | remote main == `9d428da…` |
| `gh pr view 8 --json …` / `gh pr diff 8` / `gh pr checks 8` | facts in §6; checks: CodeRabbit pass only, no workflow checks |
| `gh issue view 7` | issue body demands local-install support and official-checksum verification |
| `find bin -type f -size +0c -exec sha256sum {} \;` + read of `py7zip/platforms.py` | 7 non-empty artifacts, digests match catalog 7/7; 6 zero-byte placeholders |
| `curl -s https://pypi.org/pypi/py7zip/json` | latest **0.6.2**; releases 0.3.0–0.6.2; `requires_python >=3` |
| `curl -sI -m 8 https://py7zip.cyopsys.com` | exit 0 with empty header block (page unusable) |
| `grep -rc "def test_" tests/*.py` | 88 test functions |
| codebase-memory MCP `index_repository` (moderate) | indexed: 317 nodes / 1154 edges; discovery via `search_graph`/`get_architecture` |
| Markdown/link check | repo provides **no** markdown/link checker (no markdownlint/pre-commit config found). Manual audit performed on the files changed in this commit: every relative link resolves to an existing path (see commit diff); no test suites or builds were run, per task scope |

## 10. Decisions genuinely required (evidence-backed only)

| # | Decision | Why it cannot be defaulted | Owner |
|---|---|---|---|
| D1 | Legacy-runtime removal version/window | Determines when `requests` can be dropped (F8) and how long `shell=True` stays one flag away | Maintainer |
| D2 | Binary resolution precedence when a local 7-Zip exists: local-first (PR #8/issue #7 preference) vs. pinned-catalog-first | Security policy: a PATH-discoverable binary is user-writable; local-first trades supply-chain determinism for user trust. Needs an owner decision before P1.4 code | Maintainer (security hat) |
| D3 | Publish 0.7.3 now vs. after P0.4 provenance rows | pip users are on legacy 0.6.2 today (F3), but publishing is irreversible and P0.4 may force artifact replacement (P2.1 contingency) | Maintainer/Release |
| D4 | Do Windows x64 / WSL receipts exist for the README checklist and 0.7.3 changelog claims? | Determines whether F1 is a doc fix or a false claim to retract; **UNKNOWN** — no receipts found in repo | Maintainer |
| D5 | Options-string bridge: document `TypeError` vs. opt-in `shlex.split` shim | Both are defensible; the characterization suite pins the current `TypeError`, so either choice is a recorded contract change | Maintainer + Implementation |

## 11. Open investigation register (UNKNOWNs)

1. Upstream 7-Zip version/origin of each of the 7 shipped artifacts (P0.4 → P2.1). No record
   exists in-repo; do not guess, re-derive from official releases.
2. Existence of any Windows/WSL qualification receipts (D4).
3. Whether GitHub CI runs at all on fork PRs for this repo — PR #8 shows no workflow checks; if
   fork-CI is suppressed by policy, record it so "CI state" on future PRs is read correctly.
4. Real 7za execution behavior on any platform (nothing executed to date per
   `docs/planning/PLATFORM_MATRIX.md`) — closed by P2.3.
