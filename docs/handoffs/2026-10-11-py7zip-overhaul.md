# py7zip overhaul handoff — 2026-10-11

**Scope:** execution plan for the requested overhaul — host detection
(OS/CPU/libc), acquisition of **official upstream** 7-Zip binaries,
integrity/authenticity verification, safe cache/install/update behavior,
Python API/CLI ergonomics, packaging, tests, CI/release, supply-chain and
support policy.

**Evidence boundary:** branch `codex/py7zip-handoff-20261011`, HEAD
`9d428da` (= `origin/main` at branch time; `origin/main` has since advanced
one docs commit to `68721cf`). Working tree clean at audit start. All local
commands were run in this worktree on 2026-10-10; environment: Linux
x86-64, Python CPython 3.13.5. Upstream facts were verified by live fetch
on 2026-10-10 and are cited below. No runtime code was edited for this
handoff.

**Relationship to the landed audit.** `origin/main` already carries
`docs/handoffs/PLATFORM_ARCHITECTURE_PY7ZIP_2026-10-10.md` (PR #20,
`68721cf`): a findings audit (F1–F14) with its own P0/P1/P2 plan. That
document remains authoritative for its findings. This handoff is the
**execution plan for the overhaul**: it consumes those findings (mapped
below), adds newly verified evidence the audit marked UNKNOWN (bundled
binary version/provenance, official upstream verification channels), and
sequences the work. Where the two disagree, this doc says so explicitly.

---

## 1. First production blocker (priority)

**B0 — `pip install py7zip` still serves 0.6.2 (2024-02-25), the legacy
runtime with `shell=True` option interpolation and unverified binary
download, while every hardening line is unreleased.**

- Verified: PyPI JSON (`https://pypi.org/pypi/py7zip/json`, fetched
  2026-10-10) — latest release **0.6.2, 2024-02-25**; no 0.7.x/0.8.x/0.9.x
  exists on PyPI.
- Verified: this tree declares `version = "0.7.3"` (`pyproject.toml:7`) and
  tags `v0.8.0`/`v0.9.0` exist in-repo but were published only as GitHub
  releases from the audit branch (never PyPI).
- Verified: default `Py7zip()` here is safe-by-default (`legacy=False`,
  argv-only, checksum-verified acquisition — `py7zip/py7zip.py:19–40`,
  pinned by `tests/test_default_api.py`), so a release from this line
  actually ships the fix.

Unblocking B0 does **not** require the full overhaul; it requires the P0
tasks below (metadata hygiene + claim reconciliation + a release receipt
per `AGENTS.md`). Everything else in this plan can proceed after or in
parallel.

Secondary blocker-grade fact (blocks the overhaul's core promise):
acquisition today downloads binaries from **this repo's own mutable
`raw/main`** (`py7zip/acquisition.py:40`), with digests pinned in the same
repository (trust-on-first-use) — not from official upstream channels. The
bundled binaries identify as **"7-Zip (z) 24.00 (x64) … 2024-01-30"**
(banner probe, Appendix A.4) — 2+ major versions behind upstream 26.04.
P1 below replaces this with official-release acquisition.

## 2. Verification log (what was actually run)

| # | Command (abbreviated) | Outcome |
|---|-----------------------|---------|
| V1 | `unshare -rn python3 -m pytest tests -p no:cacheprovider -q` | **128 passed** (offline, network namespace), CPython 3.13.5 |
| V2 | `python3 -m pip wheel . --no-deps -w /var/tmp/py7zip-wheel-iso` | **Succeeds**; `py7zip-0.7.3-py3-none-any.whl`, 13,312 bytes, sha256 `d1970a66ac8f9c4992bc70013effd36cffbbebdba41d7cb56eb3a4284cd338d3` |
| V3 | Wheel inspection | 11 entries; **no `bin/`**; `Requires-Dist: requests`; `Classifier: Development Status :: 1 - Planning` |
| V4 | `python3 -m pip wheel . --no-deps --no-build-isolation` | **Fails**: `` `project.classifiers[6]` must be trove-classifier`` — value `"Programming Language :: Python :: 3 :: 9"` (ambient user-site setuptools) |
| V5 | `sha256sum` of all `bin/**/7za*` vs `ArtifactCatalog` | All 7 catalog digests + sizes **match exactly**; 6 additional committed files are **0-byte placeholders** (sha256 `e3b0c442…855`) |
| V6 | `./bin/lin/pc/x64/7za` (banner) | `7-Zip (z) 24.00 (x64) : Copyright (c) 1999-2024 Igor Pavlov : 2024-01-30` |
| V7 | `file` on bundled binaries | `lin/pc/x64`: ELF x86-64, **dynamically linked**, `/lib64/ld-linux-x86-64.so.2`; `mac/any`: **Mach-O universal (x86_64 + arm64)** |
| V8 | Download official `7z2604-linux-x64.tar.xz` from `github.com/ip7z/7zip` release 26.04; `sha256sum` vs GitHub API `assets[].digest` | 1,576,336 bytes; local sha256 `fc0327ba27e89bd086cf426dff17d77de582953cdbbc10a6576540a06853ffcd` == API digest — **dual-channel verification works** |
| V9 | Static inspection of official `7zz`/`7zzs` (no execution) | `7zz`: dynamic, GLIBC symbols up to **2.16**; `7zzs`: **statically linked** (no interpreter); embedded banner `7-Zip (z) 26.04 (x64) … 2026-10-05`; tarball ships `License.txt` beside the binaries |
| V10 | Branch topology | `origin/main` = `68721cf`; merge-base(origin/main, audit) = `4713a75`; origin/main-only = 2 commits, audit-only = **22 commits**; local `main` ref is stale (`a7b396c`); tags `v0.8.0`, `v0.9.0` are inside the audit line only |
| V11 | `git -C /nas/Temp/worktrees/py7zip-phase4-git status/diff --stat` (read-only) | Dirty: **all 7 non-empty bundled binaries modified, same byte sizes**; HEAD `03abefb` on `codex/py7zip-phase4-runtime` (based on pre-merge `b11f8c3`) |
| V12 | `git ls-remote gitforge` | No output within 20 s — GitForge remote unreachable at audit time |

Probe artifacts left for the next worker: `/var/tmp/py7zip-upstream-probe/`
(official tarball + `release.json`), `/var/tmp/py7zip-wheel-iso/` (wheel +
build log), `/var/tmp/py7zip-wheelbuild.log` (ambient-setuptools failure).

## 3. Fact register

### 3.1 Verified locally (source or execution)

1. Catalog digests/sizes match the 7 committed non-empty binaries exactly;
   catalog correctly refuses to reference the 6 zero-byte placeholders
   (`py7zip/platforms.py:95–106`, V5).
2. Bundled Linux x64 binary is official-format **7-Zip 24.00** (V6) and
   glibc-dynamic (V7); `bin/mac/any/7za` is a universal x86_64+arm64 Mach-O
   (V7). No per-artifact upstream version/provenance is recorded anywhere
   in the repo (`bin/INFO.md` lists paths only) — fixed by OVH-02.
3. **"(z)" in the banner is official upstream branding, not a fork marker**:
   the official 26.04 binary embeds the same banner format (V9). (An early
   hypothesis attributing "(z)" to the mcmilk/7-Zip-zstd fork was tested and
   refuted — Appendix A.5.)
4. The wheel ships **no binaries**; acquisition is runtime-download
   (`acquisition.py` base URL default
   `https://github.com/aliasfoxkde/py7zip/raw/main`) (V3, source).
5. Offline suite is genuinely offline: `tests/conftest.py` denies sockets;
   import hygiene is enforced in a clean interpreter
   (`tests/test_import_hygiene.py`); root package exports nothing (pinned).
6. `requests` remains a hard dependency solely for the legacy version probe
   (`py7zip/py7zip.py:9,85–115`); the safe runtime is stdlib-only
   (`acquisition.py` uses `urllib`).
7. CI runs the offline suite on 3.9–3.13 (ubuntu-only) and builds/validates
   the wheel with isolated `python -m build` (`.github/workflows/ci.yml`);
   publish is release-triggered, tag-matched, trusted-publishing
   (`.github/workflows/publish.yml`). **Both workflows target a repo whose
   wheel metadata claims `Development Status :: 1 - Planning`.**
8. Classifier set is invalid for older setuptools (V4) though isolated
   builds pass (V2) — a portability defect, not a CI blocker.
9. Platform detection has **no libc dimension** (`platforms.py` keys on
   system/family/architecture only) while the bundled Linux x64 binary
   requires the glibc dynamic loader (V7) — musl/Alpine hosts are silently
   routed to a binary that will not load there.
10. Topology per V10: the audit branch (CLI, 206 tests, 0.9.0) is **22
    commits ahead of, and not an ancestor of, `origin/main`**; several
    commits exist as same-subject duplicates on both lines (e.g. main
    `9d428da` vs audit `50371c9`, both "ci: harden test and release
    workflows"). Integration is a content merge, not a fast-forward.

### 3.2 Verified upstream (cited, fetched 2026-10-10)

| Fact | Source |
|------|--------|
| Current upstream release: **7-Zip 26.04** (page dated 2026-10-05; release published 2026-10-06T07:55:39Z) | <https://www.7-zip.org/download.html>; <https://api.github.com/repos/ip7z/7zip/releases/latest> |
| Linux artifacts (tar.xz, console): `7z2604-linux-x64.tar.xz`, `…-linux-x86.tar.xz`, `…-linux-arm64.tar.xz`, `…-linux-arm.tar.xz`; **no musl variants listed** | download.html (above) |
| macOS: single universal `7z2604-mac.tar.xz` (arm64/x86-64) | download.html (above) |
| Windows: installers `7z2604-x64.exe`/`7z2604.exe`/`7z2604-arm64.exe`, MSI alternatives, and `7z2604-extra.7z` ("standalone console version, 7z DLL…") — the console binary is distributed **inside a .7z package** | download.html (above) |
| Official release assets are hosted on GitHub: `github.com/ip7z/7zip/releases`; **the GitHub API exposes a per-asset `digest` (sha256) field**, verified equal to a locally computed digest (V8) | api.github.com (above) |
| The official download page and release body publish **no checksum list and no signatures** (checksum.html does not exist — HTTP 404) | download.html; `https://www.7-zip.org/checksum.html` → 404; release body |
| Official Linux x64 tarball contains `7zz` (dynamic, glibc ≤ 2.16) **and `7zzs` (statically linked)** plus `License.txt`, `MANUAL`, `readme.txt` | V8/V9 (artifact contents, upstream URL above) |
| License: LGPL-2.1-or-later for all files; `7z.dll` additionally BSD-3-clause (LZFSE, ZSTD) and BSD-2-clause (XXH64); unRAR restriction; **"Redistributions in binary form must reproduce related license information"** | <https://www.7-zip.org/license.txt> |

### 3.3 Inferred (reasoning stated, not directly executed)

- The 7 bundled binaries are most plausibly official-format upstream builds
  (banner format identical to official; copyright line is Igor Pavlov's) at
  version 24.00 for Linux x64 — but per-file provenance is unrecorded, so
  OVH-02 must treat every file as UNPROVEN until ledgered.
- The macOS `bin/mac/any/7za` (5.7 MB universal) likely cannot be produced
  from the official macOS tarball layout alone (single tarball, yes — but
  its exact upstream origin/version is unrecorded).
- Windows arm paths (`bin/win/arm/x32/7za`, `bin/win/arm/x64/7za`) are
  0-byte placeholders with no catalog entries; upstream ships a real
  `7z2604-arm64.exe` installer — a support surface the catalog could serve
  later.

### 3.4 Unknown (do not guess; task-linked)

- U1: Exact upstream origin (URL + release tag) of **each** of the 7
  binaries → OVH-02.
- U2: Whether official Linux builds run on musl/Alpine → resolved for the
  overhaul by D-OVH-3 (prefer static `7zzs`; no musl claim without a
  receipt per `AGENTS.md`).
- U3: macOS binary provenance/version → OVH-02 row.
- U4: Whether PyPI trusted publishing is configured for this project on
  PyPI (workflows are written for it; no publish has ever run) → OVH-18
  dry-run.
- U5: GitForge CI availability right now (V12: unreachable) → receipts for
  OVH-20 may need GitHub Actions instead.

## 4. Target architecture (delta, not rewrite)

Keep the current seams — `platforms.py` (pure detection + catalog),
`acquisition.py` (explicit, locked, atomic, checksum-verified),
`safe.py` (argv runner + traversal guard), `Py7zip` facade (safe default).
The overhaul changes **what the catalog describes and where bytes come
from**, and completes the API/packaging/policy surface:

1. **Upstream-anchored catalog** — new `upstream.py` describing, per
   `PlatformInfo` (+ new libc dimension), the official release asset
   (name, tag, in-archive path, digest, upstream URL) pinned at each
   wrapper release.
2. **Official acquisition** — fetch release assets over HTTPS, verify
   digest against the pinned value **and**, when online, the GitHub API
   `digest` field (dual channel, proven live in V8); unpack; install
   binary **with the upstream `License.txt`** beside it (license.txt
   redistribution requirement, §3.2).
3. **Cache/install/update** — versioned cache layout
   `~/.cache/py7zip/<upstream-version>/`, atomic replace + per-artifact
   lock (already implemented — keep), explicit `update()`/`status()`; no
   automatic updates, ever.
4. **libc-aware refusal** — unsupported libc raises
   `UnsupportedPlatformError` with the reason, per the support policy.
5. **API/CLI ergonomics** — root re-export, stub removal, options story,
   optional CLI (from the audit line), docs truth-pass.

## 5. Phase order and task ledger

Owners are roles: **Maint** (maintainer/decision authority), **Impl**
(implementation agent), **Docs**, **QA**, **Rel** (release manager),
**Sec** (maintainer with security hat). Every task is one reviewed commit
(rollback = revert that commit) unless noted. Mapping to the landed audit
plan is in the "Consumes" column.

| ID | Phase | Task | Owner | Depends on | Consumes |
|----|-------|------|-------|-----------|----------|
| OVH-01 | P0 | Fix invalid trove classifiers + Development Status | Impl | — | new (this doc, V3/V4) |
| OVH-02 | P0 | Artifact provenance ledger (`bin/PROVENANCE.md`) | Sec | — | P0.4 |
| OVH-03 | P0 | Docs truth-pass (USAGE/FEATURES/SETUP) | Docs | — | P0.2 |
| OVH-04 | P0 | Platform-claim reconciliation (README checklist) | Docs+Maint | OVH-02 | P0.1 |
| OVH-05 | P0 | Fix `get_binary_url()` safe-path bug | Impl | — | P0.3 |
| OVH-06 | P1 | Decision: integration strategy for audit line | Maint | — | new (D-OVH-1) |
| OVH-07 | P1 | Decision: Windows bootstrap source | Maint | — | new (D-OVH-2) |
| OVH-08 | P1 | Decision: Linux binary policy (7zz/7zzs/musl) | Maint+Sec | — | new (D-OVH-3) |
| OVH-09 | P1 | `upstream.py` release catalog module | Impl | OVH-02, OVH-08 | P2.1 |
| OVH-10 | P1 | libc detection + typed refusal | Impl | OVH-08 | new |
| OVH-11 | P1 | Official acquisition + dual-channel verify + license install | Impl | OVH-09 | P2.1 |
| OVH-12 | P1 | Versioned cache, `update()`/`status()` API | Impl | OVH-11 | new |
| OVH-13 | P1 | Windows acquisition path per OVH-07 | Impl | OVH-07, OVH-09 | new |
| OVH-14 | P2 | Remove snapshot stubs + `cd` | Impl | — | P1.2 |
| OVH-15 | P2 | Root re-export `Py7zip`, `__version__` | Impl | OVH-14 | P1.3 |
| OVH-16 | P2 | Options bridge decision + impl | Maint+Impl | — | P1.1 |
| OVH-17 | P2 | Local-binary discovery (PR #8 rework) + PR disposition | Impl+Maint | OVH-14 | P1.4, P1.6 |
| OVH-18 | P2 | CLI surface (port from audit line) | Impl | OVH-06, OVH-15 | new |
| OVH-19 | P3 | Legacy sunset; drop `requests` dependency | Impl+Maint | OVH-16 | P1.5 |
| OVH-20 | P3 | Decision + impl: distribution model | Maint | OVH-11 | new (D-OVH-4) |
| OVH-21 | P3 | Release cut from main → PyPI (fixes B0) | Rel | OVH-01…05, OVH-20 | new |
| OVH-22 | P4 | Multi-OS CI lanes + 3.14/classifier alignment | Maint | — | P2.2 |
| OVH-23 | P4 | Platform qualification receipts (CI, not local) | QA | OVH-11, OVH-22 | P2.3 |
| OVH-24 | P4 | Extraction-safety policy completion (symlinks/overwrite) | Impl+Sec | — | P2.4 |
| OVH-25 | P4 | SECURITY.md + support policy + release hygiene | Sec+Maint | OVH-02 | P0.4 rest, P2.5 |

Phase rationale: **P0** makes the tree releasable and truthful (B0
prerequisites; all docs/test-only or one-line code fixes). **P1** is the
overhaul core — decisions before code, then the upstream-anchored
acquisition spine. **P2** finishes the Pythonic API surface and unblocks
legacy removal. **P3** ships (B0 cleared). **P4** hardens claims (CI
lanes, receipts, safety policy). Receipts per `AGENTS.md` are the gate
between P3 and any support-claim promotion.

## 6. Task specifications (acceptance criteria and commands)

### P0 — release unblock

**OVH-01 — Fix invalid trove classifiers + Development Status** *(the
bounded, low-risk next task)*
Files: `pyproject.toml` (classifiers). Replace the six malformed entries
(`"Programming Language :: Python :: 3 :: 9"` … `":: 3 :: 14"`) with the
valid forms (`"Programming Language :: Python :: 3.9"` … `":: 3.14"`),
and raise `Development Status :: 1 - Planning` → `:: 4 - Beta` (the safe
runtime is default and tested; the current value misdescribes the
package, V3).
Acceptance (all must pass):
```
python3 -m pip wheel . --no-deps --no-build-isolation -w /var/tmp/ovh01a   # V4 must now succeed
python3 -m pip wheel . --no-deps -w /var/tmp/ovh01b                        # V2 stays green
python3 -m twine check /var/tmp/ovh01a/*.whl
python3 -m pytest tests -p no:cacheprovider -q                             # 128 passed
```
Rollback: revert the single commit. Risk: none at runtime (metadata only).

**OVH-02 — Artifact provenance ledger.** New `bin/PROVENANCE.md`: one row
per non-empty binary — upstream version (banner probe, V6-style), where
obtained, upstream-published anchor (URL/digest) or explicit `UNKNOWN`,
check date; plus the 6 placeholder paths marked "empty, not distributed".
Start from V5/V6/V7 (Linux x64 = official-format 24.00, glibc-dynamic;
mac = universal). Acceptance: `find bin -type f -size +0c | sort` has
exactly one ledger row each, and any `UNKNOWN` row links the follow-up
task. Consumed later by OVH-09/11. Rollback: revert (docs only).

**OVH-03 — Docs truth-pass** per landed P0.2 (USAGE import line, FEATURES
stub labeling, SETUP publish flow). Acceptance: every import/command line
in the edited docs executes in a clean interpreter; no doc references
`setup.py`/`push.bat` as current.

**OVH-04 — Platform-claim reconciliation** per landed P0.1, now with
OVH-02's ledger as the receipt source. Acceptance:
`grep -n "\[x\]" README.md` returns only receipt-backed rows.

**OVH-05 — `get_binary_url()` safe path** per landed P0.3 (F2: returns a
nonexistent path on the default runtime). Prefer deprecation/delegate to
`ensure_binary()`; keep legacy branch byte-identical; new pinning test in
`tests/test_default_api.py`. Acceptance:
`python3 -m pytest tests/test_default_api.py -q` plus full offline suite.

### P1 — official-upstream acquisition core (decisions first)

**OVH-06 — Integration strategy (D-OVH-1).** Verified shape: audit line =
22 commits, contains the CLI (`ebca3ad`, `ac2b034`, `13fe83e`), 206-test
suite, 0.8.0/0.9.0 release machinery, and same-subject duplicates of
main's chain; main has 2 unique commits (CI hardening `9d428da`, landed
handoff `68721cf`). Options: (a) merge audit → main accepting duplicate
resolution, (b) cherry-pick the CLI + receipts slices only, (c) leave
diverged and port by re-implementation. Decision gates OVH-18 (and
partly OVH-17). Deliverable: decision record in `docs/planning/` naming
the chosen strategy and conflict inventory
(`git log --oneline origin/main..audit/py7zip-qualification-20260909`).

**OVH-07 — Windows bootstrap (D-OVH-2).** Upstream distributes the Windows
console binary inside `7z2604-extra.7z` (a .7z — bootstrap problem) or as
installers. Options: (i) keep repo-hosted Windows binaries refreshed from
official extra package with ledgered provenance, (ii) bundle Windows
binary in platform wheels (ties to OVH-20), (iii) document system-7z
discovery for Windows. Deliverable: decision + rationale; OVH-13
implements.

**OVH-08 — Linux binary policy (D-OVH-3).** Evidence: official Linux x64
ships **dynamic `7zz` (glibc ≤ 2.16)** and **static `7zzs`** (V9).
Recommended default: **`7zzs`** — removes the libc dimension for Linux,
covers musl without claims, one artifact for glibc+musl; keep dynamic
`7zz` behind an explicit opt-in if a receipt justifies it. Also decides
the executable-name migration (`7za` → `7zz`/`7zzs`) and its doc impact.
Deliverable: decision record; gates OVH-09/10/11/13.

**OVH-09 — `upstream.py` release catalog.** Frozen-dataclass catalog: per
`(system, family, architecture[, libc])` → official asset name, release
tag, in-archive member path, sha256 (pinned at wrapper-release time from
the GitHub API `digest` field — the mechanism proven in V8), upstream
URL. Include the wrapper's upstream-version pin and a `source_url()`
helper. Tests: pure, offline, table-driven (`tests/test_platforms.py`
style). Acceptance: `pytest tests/test_upstream.py -q` green offline;
every catalog entry carries tag+digest+URL (no bare paths).

**OVH-10 — libc detection + typed refusal.** Extend `PlatformInfo` with
`libc` (values `glibc`/`musl`/`unknown`) detected without subprocess where
possible (`platform.libc_ver()`; musl heuristic via loader path). Per
OVH-08: with `7zzs`, Linux has no libc constraint — record `libc` for
reporting only; if the dynamic binary is ever selected on a musl host,
raise `UnsupportedPlatformError` explaining why. Acceptance: table-driven
tests for glibc/musl/unknown; refusal message names the constraint.

**OVH-11 — Official acquisition.** Extend `ArtifactManager`: fetch the
pinned release asset, verify sha256 against the catalog **and** against
the GitHub API `digest` when online (skip API check offline — catalog pin
remains authoritative; both channels proven equal in V8); unpack member +
`License.txt` into the cache; keep atomic replace, size bound, lock, and
stale-lock recovery unchanged. Opt-in network test per `AGENTS.md`
("explicitly opts into an integration probe and records the
platform/architecture"). Acceptance: offline unit tests with a fake
transport (extend `tests/fakes.py`); one `@pytest.mark.integration`
probe guarded by env var; full offline suite green.

**OVH-12 — Versioned cache + `update()`/`status()`.** Cache layout
`<cache>/<upstream-version>/<binary>`; `ensure_binary()` resolves the
pinned version; `update()` re-resolves against a newer allowed tag
(explicit call only, never automatic); `status()` reports
installed/upstream version + digests. Old-version GC only on explicit
`update(gc=True)`. Acceptance: offline tests cover fresh install,
re-ensure (no refetch), explicit update, refusal to auto-update;
`License.txt` present beside binary after install.

**OVH-13 — Windows path per OVH-07.** Acceptance: offline tests; if (i),
refresh script + ledger rows for the two Windows binaries; if (ii), wheels
per OVH-20; if (iii), documented discovery precedence.

### P2 — Pythonic API completion

**OVH-14** remove `full/incremental/differential/snapshot` and `cd` (they
are no-ops / process-global mutation; COMPATIBILITY.md already schedules
this) — update characterization tests in the same commit. Acceptance:
`python3 -c "from py7zip.py7zip import Py7zip; print([hasattr(Py7zip, m) for m in ('full','incremental','differential','snapshot','cd')])"` → all `False`.

**OVH-15** root re-export `py7zip.Py7zip`, `py7zip.__version__` (additive;
update the pinned hygiene test in the same commit, never weaken silently).
Acceptance: `python3 -c "import py7zip; py7zip.Py7zip"` offline-clean.

**OVH-16** options story: keep `TypeError` for string options on the safe
path; if a bridge exists, `shlex.split` behind explicit opt-in only;
document in USAGE; COMPATIBILITY row updated same-commit. Acceptance:
`pytest tests/test_default_api.py tests/test_safe.py -q`.

**OVH-17** local-binary discovery per landed P1.4 (opt-in, precedence
documented, never implicit in `__init__`); then disposition **PR #8**
(open, `webbrain/issue-7`, "support local 7zip installations…") — close
as superseded or hand to author, crediting the analysis.

**OVH-18** CLI per OVH-06 outcome: argparse surface with typed exit codes
and `--`-terminated 7-Zip switches (the audit line already solved two
e2e defects here: `-o/--option` untypeable → `--`; differential re-run
errno-17). If porting, keep its tests. Acceptance: console script present
(`[project.scripts]`), `py7zip --help` and exit-code table documented,
offline CLI tests green.

### P3 — packaging and the release that clears B0

**OVH-19** deprecation warning on `legacy=True` with removal version;
drop `requests` (`pyproject.toml:16`) when legacy retires. Acceptance: fresh-venv
`pip install .` pulls no `requests`; `grep -r "import requests" py7zip/`
empty.

**OVH-20** distribution model decision (D-OVH-4): (i) keep no-binary wheel
+ official-release fetch (current shape, minimal repackaging risk; needs
OVH-11 mature), or (ii) per-platform wheels bundling verified binaries
(offline installs; heavier release machinery; license files must ship —
see OVH-11's `License.txt` requirement and `AGENTS.md`'s
"keep 7-Zip's upstream license notices with distributed binary assets").
Deliverable: decision record + packaging change + `twine check`.

**OVH-21 — Release cut (clears B0).** Version bump (0.7.x→ at least
0.8.0-equivalent content), tag `v<version>`, tag/version gate already in
`publish.yml`, **trusted-publishing dry-run first** (U4 unknown),
receipts attached per `AGENTS.md` promotion rule (commit, Python, OS/arch,
binary provenance, test results, skipped lanes). Acceptance:
`pip install py7zip==<version>` in a fresh venv returns the safe-default
runtime (`Py7zip().legacy is False`); PyPI page shows the new metadata.
Rollback: PyPI releases are immutable — ship a patch release; do not
attempt deletion.

### P4 — CI, receipts, policy

**OVH-22** add `windows-latest`/`macos-latest` lanes of the same offline
suite; reconcile 3.14 classifier vs matrix. Acceptance: three green OS
lanes; classifier set == tested set.
**OVH-23** platform receipts executed on CI runners (not local hardware),
each receipt = exact Python/OS/arch/binary provenance/commands/result;
matrix tiers promoted only with receipts. GitForge is a possible runner
(U5: currently unreachable; GitHub Actions is the fallback).
**OVH-24** extraction-safety policy (symlink members, overwrite,
partial-output) — document scope as member-path-traversal rejection unless
a link audit is implemented; tests for whatever is claimed.
**OVH-25** `SECURITY.md`, support-policy page (tiers from
PLATFORM_MATRIX.md), fix/drop dead `Project Page` URL (F14), release
process single-sourced.

## 7. Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| B0 persists while overhaul work continues; users keep receiving 0.6.2 | High | Reputation/security | P0 is deliberately small; OVH-21 sequenced early |
| Audit-line integration conflicts (duplicate commits, same files: `py7zip.py`, workflows, pyproject) | High | Rework | OVH-06 decision + conflict inventory before any port |
| Phase4 dirty worktree refreshes `bin/` concurrently with OVH-02/09/11 | Medium | Clobbered work / confused provenance | `bin/` frozen for this plan until that effort lands or is dispositioned (D-OVH-5); it is read-only to this handoff |
| Windows bootstrap complexity delays parity | Medium | Feature gap | OVH-07 decision allows repo-hosted stopgap with ledgered provenance |
| musl users lose support if dynamic binary chosen | Low | Support burden | OVH-08 recommends static `7zzs` — no libc constraint |
| Upstream release churn invalidates pins | Medium | Availability | Pins are per-wrapper-release; `update()` is explicit; digest mismatch fails loudly, never silently |
| License non-compliance when redistributing binaries | Low | Legal | Ship upstream `License.txt` beside every binary (verified it ships in the official tarball, V9); AGENTS.md already requires it |
| Overloading scope: implementing everything before shipping | Medium | B0 drag | Phase order enforces ship-at-P3 |

## 8. Decisions required (owner: Maintainer unless noted)

- **D-OVH-1** audit-line integration strategy (OVH-06).
- **D-OVH-2** Windows acquisition source (OVH-07).
- **D-OVH-3** Linux binary policy: static `7zzs` default recommended (OVH-08).
- **D-OVH-4** distribution model: runtime-fetch vs platform wheels (OVH-20).
- **D-OVH-5** disposition of the phase4 binary-refresh effort vs
  upstream-anchored re-acquisition (they overlap; sequence before OVH-09).
- Plus the landed audit's open decisions D1–D5 (options bridge, sunset
  window, etc.) — see `docs/handoffs/PLATFORM_ARCHITECTURE_PY7ZIP_2026-10-10.md` §10.

## 9. External work in flight (observed read-only; do not touch from this branch)

- `/nas/Temp/worktrees/py7zip-phase4-git` — branch `codex/py7zip-phase4-runtime`
  at `03abefb` ("fix: preserve executable mode for bundled binaries"), dirty:
  all 7 non-empty bundled binaries modified, sizes unchanged (V11). Not
  staged, not reset, not merged here.
- `/nas/Temp/repos/py7zip` — worktree on `audit/py7zip-qualification-20260909`
  at `7822d95` (0.9.0 line).
- PR #8 (`webbrain/issue-7`) open on `aliasfoxkde/py7zip` since 2026-08-06.
- Local `main` ref is stale at `a7b396c` — run `git fetch origin` before any
  main-based work.
- GitForge remote unreachable during this audit (V12).

## 10. Next worker: start here

**Do OVH-01 only** (classifier fix + status bump, §6): metadata-only,
four acceptance commands, zero runtime risk, unblocks both CI packaging
and the release train. Then bring OVH-02 (provenance ledger) to the
maintainer with the V5–V9 evidence above.

---

## Appendix A — evidence detail

### A.1 Suite (V1)
```
$ unshare -rn python3 -m pytest tests -p no:cacheprovider -q
........................................................................  [ 56%]
........................................................                 [100%]
128 passed
```

### A.2 Wheel (V2/V3)
```
py7zip-0.7.3-py3-none-any.whl  13312 bytes
sha256 d1970a66ac8f9c4992bc70013effd36cffbbebdba41d7cb56eb3a4284cd338d3
11 entries; no bin/, no 7za*; METADATA: Requires-Dist: requests;
Requires-Python: >=3.9; Classifier: Development Status :: 1 - Planning
```

### A.3 Ambient-setuptools failure (V4, verbatim core)
```
configuration error: `project.classifiers[6]` must be trove-classifier
GIVEN VALUE: "Programming Language :: Python :: 3 :: 9"
ValueError: invalid pyproject.toml config: `project.classifiers[6]`.
```

### A.4 Bundled-binary probes (V5–V7)
```
bin/lin/pc/x64/7za: ELF 64-bit LSB pie executable, x86-64, dynamically
  linked, interpreter /lib64/ld-linux-x86-64.so.2, stripped
  banner: 7-Zip (z) 24.00 (x64) : Copyright (c) 1999-2024 Igor Pavlov : 2024-01-30
bin/mac/any/7za: Mach-O universal binary with 2 architectures: [x86_64] [arm64]
catalog vs disk: all 7 digests+sizes match; 6 committed 0-byte placeholders
  (win/arm/x32, win/arm/x64, mac/arm/x64, mac/arm/x86, mac/pc/x64, mac/pc/x86)
```

### A.5 Official-upstream probe (V8/V9), `/var/tmp/py7zip-upstream-probe`
```
curl -fsSLO https://github.com/ip7z/7zip/releases/download/26.04/7z2604-linux-x64.tar.xz
sha256sum 7z2604-linux-x64.tar.xz
  fc0327ba27e89bd086cf426dff17d77de582953cdbbc10a6576540a06853ffcd
GitHub API assets[].digest (release 26.04):
  sha256:fc0327ba27e89bd086cf426dff17d77de582953cdbbc10a6576540a06853ffcd  (match)
tarball contents: 7zz, 7zzs, History.txt, License.txt, MANUAL, readme.txt
7zz : ELF x86-64, dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2,
      GLIBC symbol versions up to GLIBC_2.16
7zzs: ELF x86-64, statically linked (no interpreter)
embedded banner: 7-Zip (z) 26.04 (x64) : Copyright (c) 1999-2026 Igor Pavlov : 2026-10-05
```
The identical `7-Zip (z) <ver>` banner format between the official 26.04
binary and the bundled 24.00 binary refuted the mid-audit hypothesis that
"(z)" marked the mcmilk/7-Zip-zstd fork (which the surrounding releases
title as "7-Zip ZS …" — <https://github.com/mcmilk/7-Zip-zstd>).

### A.6 Upstream citations (fetched 2026-10-10)

- Official download page (artifact names, 26.04, GitHub/SourceForge links,
  no checksums, no musl variants):
  <https://www.7-zip.org/download.html>
- Official releases + per-asset digests:
  <https://api.github.com/repos/ip7z/7zip/releases/latest> (tag `26.04`,
  published 2026-10-06T07:55:39Z, 16 assets)
- Licensing (LGPL-2.1+, BSD-3/BSD-2 portions, unRAR restriction, binary
  redistribution must reproduce license information):
  <https://www.7-zip.org/license.txt>
- PyPI state (latest 0.6.2, 2024-02-25):
  <https://pypi.org/pypi/py7zip/json>
- Checksum page absent: `https://www.7-zip.org/checksum.html` → HTTP 404

### A.7 Topology (V10/V11)
```
origin/main = 68721cf  (9d428da + docs handoff PR #20)
merge-base(origin/main, audit/py7zip-qualification-20260909) = 4713a75
origin/main-only: 2    audit-only: 22
local main ref: a7b396c (stale)
tags: v0.8.0, v0.9.0 (audit line; not ancestors of origin/main)
phase4 worktree: dirty, 7 binaries modified (same sizes), HEAD 03abefb
```
