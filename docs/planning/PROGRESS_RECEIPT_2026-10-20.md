# Progress receipt — 2026-10-20 — B0 tranche: OVH-02, OVH-26, OVH-03, OVH-04

Execution of `docs/handoffs/2026-10-11-py7zip-overhaul.md` (revision 4),
feature branch `agent/py7zip-overhaul-20261019`, based on `origin/main`
`a06615f` (branch and `origin/main` were identical at tranche start;
working tree clean). This receipt records what was done, the exact
commands and outcomes, and the gates that remain open. No platform
support is claimed by this receipt (`AGENTS.md` promotion rule).

## Environment

- Checkout: `/home/mkinney/agent-work/py7zip-quality-20261019` on
  `/dev/nvme0n1p3` (btrfs, NVMe) — device confirmed before any test or
  build run; work isolated in a git worktree of that checkout.
- CPython 3.14.8 (`/usr/bin/python3`), pytest 9.1.1. **Note:** 3.14 is
  outside the CI test matrix (3.9–3.13); the GitHub CI run on the base
  commit covers the matrix (below). No 3.9–3.13 interpreter with pytest
  was available locally.
- Fedora Linux x86-64 (kernel 7.2.9). No GPU was touched; no binary in
  `bin/` was executed (static `strings`/`file` probes only).

## Baseline verification (before implementation)

- `git fetch origin`; `origin/main` = `a06615f` = local HEAD; tree clean.
- GitHub Actions on `a06615f`: run `38230476390`, "CI" on `main`,
  completed / **success**.
- Baseline suite: `unshare -rn python3 -m pytest tests -p no:cacheprovider`
  → **129 passed** (offline, network namespace).
- GitForge: **not registered in this checkout** — `git remote -v` lists
  only `origin` (github.com/aliasfoxkde/py7zip); `git ls-remote gitforge`
  → `fatal: 'gitforge' does not appear to be a git repository`. The
  canonical pipeline therefore cannot be GitForge here; GitHub Actions is
  the CI surface (per U5's fallback).

## Tasks landed (one commit each)

### OVH-02 — Artifact provenance ledger

- New `bin/PROVENANCE.md`: one row per non-empty binary (7 rows) with
  size, sha256, static format, static banner, upstream version,
  provenance state, introducing commit (`1fabd26`, 2024-02-24, for all
  rows); six placeholder slots listed as empty/not distributed.
- New evidence gathered 2026-10-20 (static probes, no execution):
  `bin/lin/pc/x86` banner `7-Zip (z) 24.00 (x86)`;
  `bin/lin/arm/x64` banner `7-Zip (z) 24.00 (arm64)`;
  `bin/lin/arm/x32` banner `7-Zip (z) 24.00 (armt)` (all 2024-01-30);
  `bin/win/pc/x64` and `bin/win/pc/x86` banners `7-Zip (a) 24.01
  (x64)/(x86)` (2024-01-31) — found by broader `strings` probing; the
  2026-10-11 handoff probes had only searched for `(z)`.
- `bin/lin/pc/x64/7za` digest `12ef1251…` re-verified 2026-10-20 against
  the recorded 24.00 anchor (overhaul handoff §3.1 item 12 / V19); the
  archived tarball itself was not re-downloaded.
- Provenance states: linux x64 **Anchored**; the other six **UNPROVEN**
  (mac row adjudicated by gate OVH-29; win rows source-decided by gate
  OVH-07 / D-OVH-2).
- `bin/INFO.md` reconciled to the on-disk inventory: pattern line now
  includes the architecture level and the `.exe`-or-empty extension, the
  Linux example corrected to `bin/lin/arm/x32/7za`, the nonexistent
  `bin/win/arm/*.exe` / `bin/mac/arm/x32/7za` paths removed, the
  unlisted `bin/mac/pc/*` placeholders added, and
  `bin/PROVENANCE.md` named the inventory of record.
- Acceptance run: `find bin -type f -size +0c | sort` → exactly the 7
  binaries, one ledger row each; programmatic check confirmed all 7
  catalog digests/sizes in `py7zip/platforms.py` match disk and that the
  ledger covers every catalog artifact.
- Wayback availability re-check for `7z2400-linux-{x86,arm64,arm}` and
  `7z2400-mac` → HTTP 429 (rate-limited), no new evidence; recorded as
  such, not retried to avoid hammering the service.

### OVH-26 — Gate: Windows/WSL receipt audit (audit D4)

- New `docs/planning/DECISION_WINDOWS_RECEIPTS_2026-10-20.md`.
- Searches run 2026-10-20: repo greps (claims only, no receipts),
  `git log --all --grep` (one hit: the handoff doc commit),
  `gh search issues "windows receipt"` (0 results), `gh search issues
  "WSL"` (issue #5 only — a PyPI-divergence bug report, not a receipt),
  full GitHub issue/PR inventory (no receipt artifacts).
- Outcome (the plan's mandated rule, applied — no receipts found):
  **uncheck claims.** README `[x] Windows x64` → to-uncheck; the 0.7.3
  WSL sentence and 0.6.2 Windows-x64 sentence in `docs/CHANGELOG.md`
  are unreceipted historical claims — left unrewritten, never to be
  repeated as support claims in future release notes.
- **Provenance caveat:** the gate's owner role is Maint; this record was
  written by the implementation agent under the 2026-10-20 execution
  directive ("if a gate is decision-blocked, record the exact decision
  and work adjacent unblocked tasks without bypassing it"), applying the
  gate's pre-stated outcome rule. It invents no receipt and takes no
  acquisition-strategy decision (D-OVH-2 stays open). The maintainer may
  revise or supersede it (docs-only revert).
- Scope boundaries honored: D-OVH-2 (OVH-07) remains open; the §1
  governed fallback (repo-hosted Windows binaries, no support claim)
  continues.

### OVH-03 — Docs truth-pass

- `docs/USAGE.md`: example rewritten to
  `from py7zip.py7zip import Py7zip` (the root package exports nothing —
  pinned by `tests/test_import_hygiene.py`), the safe-runtime sequence
  (construct → explicit optional `download_binary()` → compress/
  decompress returning `ArchiveResult`), individual-argument options
  (string options raise `TypeError` on the default runtime), and a
  factual safe-runtime note.
- `docs/FEATURES.md`: the two false claims at old lines 5–6 removed;
  `full`/`incremental`/`differential`/`snapshot` each labeled no-op (per
  -occurrence qualifier rule, Phase A of the snapshot-family handoff —
  no removal version claimed, v0.8.0/v0.9.0 artifacts not described);
  the "Cross platform support" line replaced with the catalog/
  typed-refusal statement plus the receipts requirement; the false
  "removes need for … CLI executing" line corrected; "implimented" typo
  fixed.
- `docs/SETUP.md`: legacy `push.bat` / `setup.py` / `PYPI_API_KEY`
  publish flow replaced with the actual `.github/workflows/publish.yml`
  flow (release-triggered, tag/version gate, trusted publishing,
  `workflow_dispatch` = rehearsal only) and locally executable
  test/build commands.
- New `tests/test_docs_truthfulness.py` (4 tests, offline): the Phase A
  per-occurrence family-qualifier guard verbatim from the handoff; the
  USAGE import + `Py7zip()` construction executed in a clean interpreter
  subprocess with socket denial (safe runtime asserted); the submodule
  import line pinned; `setup.py`/`push.bat`/`PYPI_API_KEY` barred from
  USAGE/FEATURES/SETUP/README (historical changelogs deliberately not
  policed).
- Acceptance runs: `grep -nF "point-in-time" docs/FEATURES.md` and
  `grep -nF "Simplifies lessor known features" docs/FEATURES.md` → both
  empty; the handoff's Phase A guard script → counterexample fails,
  permitted wording passes, **zero findings** in `docs/FEATURES.md`;
  documented commands executed (pytest, `pip wheel . --no-deps -w dist/`
  → built; `pip show py7zip` runs, reports "not found" in this
  non-installed environment).

### OVH-04 — Platform-claim reconciliation

- `README.md`: `[x] Windows x64 (64-bit)` unchecked per the OVH-26
  record; a receipts-required note added (rows may be checked only with
  an `AGENTS.md` promotion-rule receipt); the install note corrected to
  the actual wheel behavior (no binaries shipped; sha256-verified
  acquisition into `~/.cache/py7zip`; explicit acquisition) — audit F13.
- Acceptance run: `grep -n "\[x\]" README.md` → no matches (only
  receipt-backed rows remain; there are none).

## Validation (after all edits, before commit)

- Full offline suite: `unshare -rn python3 -m pytest tests
  -p no:cacheprovider` → **133 passed** (129 baseline + 4 new docs
  guards).
- Clean package build: `python3 -m pip wheel . --no-deps -w <scratch>`
  → `py7zip-0.7.3-py3-none-any.whl`, 13,777 bytes, sha256
  `0b9b5b9a71db1754882fd31ec20f8a95f0e022aa75d58df05aa8fbce7b3999ff`;
  11 entries, **no `bin/`**; metadata shows `Development Status :: 4 -
  Beta`, valid 3.9–3.14 classifiers, `Requires-Dist: requests` (expected
  — legacy sunset is OVH-19, not this tranche).
- `python3 -c "from py7zip.py7zip import Py7zip; …"` in a clean
  interpreter → constructs, `legacy is False`.
- `git diff --check` → clean. `twine` was not available locally;
  `twine check` was not run (CI's package job runs it).
- Not done here, by design: no release, tag, or PyPI action; no change
  to `py7zip/*.py` runtime code; no test weakened or deleted.

## Decision gates still open (recorded, not bypassed)

- **Publication gate (audit D3, taken inside OVH-21)** — decision-
  blocked on the Maintainer: outcome (a) publish-now requires every
  OVH-02 provenance row upstream-anchored or explicitly maintainer-
  excepted; six rows are UNPROVEN, which forces outcome (b) (recorded
  decision + dated issue) until anchored or excepted.
- **OVH-29 (D-OVH-6)** — macOS support surface + provenance; now has
  its ledger row waiting (OVH-02 dependency satisfied).
- **OVH-07 (D-OVH-2)** — Windows acquisition source; bounded deadline
  tied to the OVH-09 catalog freeze; governed fallback in effect.
- **OVH-06 (D-OVH-1)**, **OVH-08 (D-OVH-3)**, **OVH-20 (D-OVH-4)**,
  **OVH-27 (D1)**, **OVH-28 (D2)**, **OVH-30 (D-OVH-7)** — unrecorded;
  their consumers (OVH-09/10/11/13/14/17/18/19) remain gated.

## Exact next task

- **B0 critical path:** the next step is the **publication decision D3
  inside OVH-21**, which is owner-blocked (Maintainer). With this
  tranche, every mechanical P0 task (OVH-01, 02, 03, 04, 05) is landed;
  nothing further on the B0 path is unblocked until D3 — or until a
  maintainer anchors/excepts the six UNPROVEN provenance rows.
- **Next unblocked, non-gated implementation task:** OVH-24 (P4,
  extraction-safety policy completion; no dependencies), with OVH-22
  (P4, multi-OS CI lanes; no dependencies) as the other unblocked
  option. P1 core work (OVH-09/10/11) stays blocked on the OVH-08
  decision (D-OVH-3).
