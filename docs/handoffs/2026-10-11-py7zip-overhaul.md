# py7zip overhaul handoff — 2026-10-11

**Scope:** execution plan for the requested overhaul — host detection
(OS/CPU/libc), acquisition of **official upstream** 7-Zip binaries,
integrity/authenticity verification, safe cache/install/update behavior,
Python API/CLI ergonomics, packaging, tests, CI/release, supply-chain and
support policy.

**Evidence boundary (revision 3):** baselined against branch
`codex/py7zip-production-handoff-20261011`, HEAD `d606b75` — which is
`origin/main` itself after PR #22 landed OVH-05 (2026-10-11). The audit
beneath this plan was executed on branch `codex/py7zip-handoff-20261011`
at HEAD `9d428da` (= `origin/main` at branch time, later advanced to
`68721cf` by PR #20 and to `d606b75` by PR #22); the working tree was
clean at audit start. Local commands ran in NVMe worktrees on 2026-10-10
(audit) and 2026-10-11 (revisions 2–3); environment: Linux x86-64, Python
CPython 3.13.5. Upstream facts were verified by live fetch on 2026-10-10
and 2026-10-11 and are cited below. PR #22 removed one import line from
`py7zip/py7zip.py`, shifting that file's line numbers; every `py7zip.py`
citation in this revision was re-verified at `d606b75`.

**Revision 2 (2026-10-11).** Refined to resolve independent review: audit
decision D1/D2/D3/D4 are now wired as explicit ledger gates (§5), the
publication decision (audit P0.5/D3) is mapped to OVH-21, OVH-11 carries an
offline digest-mismatch acceptance test, OVH-21 specifies collision-safe
version/tag selection, a macOS resolution gate (OVH-29) precedes asset
pinning, non-core scope is separated from the B0 critical path (§5.1), and
the probe-artifact dependency on `/var/tmp` was removed. New upstream and
provenance evidence was gathered on **2026-10-11** (V13–V19, Appendix A.8)
and is dated as such everywhere it appears; 2026-10-10 evidence is
unchanged. Still docs-only: no runtime code edited.

**Revision 3 (2026-10-11).** Rebases the evidence boundary onto
`origin/main` = `d606b75` (PR #22): **OVH-05 has landed** and is recorded
as done throughout (§1, §5.1, ledger, §6). Incorporates the five
independently reviewed gaps: (1) OVH-14 is now a deprecation-then-removal
sequence, grounded in V20 — the PyPI 0.6.2 sdist ships all five methods,
so direct removal would break upgrade callers; (2) B0's Windows behavior
and its governed fallback are stated explicitly (§1), and D-OVH-2/OVH-07
carries a bounded decision deadline with escalation (§6 OVH-07); (3)
acceptance rules no longer reference fixed `/var/tmp` paths — runner-owned
`mktemp` scratch is required and historical probe artifacts are classified
as non-acceptance evidence (§2.1, §6 OVH-01); (4) env-guarded integration
probes are stated to be non-gating for OVH-11/OVH-21 (§6 OVH-11); (5) new
§6.2 enumerates the supported platform/architecture rows and binds them
into OVH-03/04/09/11/23 acceptance. New evidence: V20 (0.6.2 sdist probe,
2026-10-11). `publish.yml` tag-gate citation tightened to `:28–35`. Still
docs-only: no runtime code edited in this revision.

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
  2026-10-10, **re-verified 2026-10-11**, V13) — latest release **0.6.2**
  (uploaded 2024-02-25T04:57:50Z); the complete PyPI release set is
  0.3.0–0.6.2 (7 releases); no 0.7.x/0.8.x/0.9.x exists on PyPI.
- Verified: this tree declares `version = "0.7.3"` (`pyproject.toml:7`).
  Tags `v0.8.0`/`v0.9.0` exist on **both remotes** (`origin` and `gitforge`,
  `git ls-remote --tags`, 2026-10-11, V14) and as two **published, non-draft
  GitHub Releases** on `aliasfoxkde/py7zip` — "py7zip 0.8.0 — Safe Runtime
  Qualification" (2026-09-29) and "py7zip 0.9.0 - Command-Line Interface"
  (2026-10-03) — each carrying `py7zip-0.8.0`/`0.9.0` wheel + sdist assets
  (V15). They were never published to PyPI. Consequence for OVH-21: version
  numbers 0.8.0/0.9.0 are publicly consumed (their release assets are
  installable directly from GitHub) and their tags are occupied on both
  remotes — they must never be reused or moved.
- Verified: default `Py7zip()` here is safe-by-default (`legacy=False`,
  argv-only, checksum-verified acquisition — `py7zip/py7zip.py:18–39`,
  pinned by `tests/test_default_api.py`), so a release from this line
  actually ships the fix.

Unblocking B0 does **not** require the full overhaul. The B0 critical path
is exactly: **OVH-01 → OVH-02 → OVH-26 → (OVH-03, OVH-04) →
publication decision (audit P0.5/D3, taken inside OVH-21) → OVH-21**
(§5.1). Of the original P0 set, **OVH-05 has landed** (PR #22, `d606b75`)
and no longer blocks. The CLI port (OVH-18), local-binary discovery + PR #8
disposition (OVH-17), SECURITY.md/support policy (OVH-25), legacy sunset
(OVH-19), and CI/receipt lanes (OVH-22/23) are post-release or
decision-gated work, not release blockers.

**Windows on the B0 path (explicit, not implied).** A release cut from
this line gives Windows users exactly the following, and the OVH-21
release notes must state it:

- Safe runtime (default): `windows/pc/x64` and `windows/pc/x86` resolve
  repo-hosted `bin/win/pc/{x64,x86}/7za.exe` through checksum-verified
  acquisition (`py7zip/platforms.py:100–101`) — digests pinned in this
  repository (trust-on-first-use), provenance rows UNPROVEN until OVH-02
  anchors or excepts them. This is the **governed fallback** until
  D-OVH-2 lands (bounded deadline and escalation: §6 OVH-07).
- `windows/arm` (any width): no catalog row (0-byte placeholders, §3.3) →
  typed `UnsupportedPlatformError` refusal.
- Legacy runtime (`legacy=True`): unchanged 0.6.2-era behavior —
  unverified `raw.githubusercontent` download with `shell=True` option
  interpolation; the exact surface B0 exists to retire.
- No support claim may accompany the fallback: gate OVH-26 (§6.1) decides
  whether the README's `[x] Windows x64` row survives, and its rule is
  "uncheck claims", never "assume support".

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

### 2.1 Re-verification and new evidence (2026-10-11, this revision)

| # | Command (abbreviated) | Outcome |
|---|-----------------------|---------|
| V13 | `curl -s https://pypi.org/pypi/py7zip/json` | Latest **0.6.2** (2024-02-25T04:57:50Z); complete release set 0.3.0–0.6.2 (7 releases); no 0.7.x/0.8.x/0.9.x — B0 claim holds |
| V14 | `git ls-remote --tags origin` **and** `git ls-remote --tags gitforge` | Both remotes carry `v0.8.0` (peeled `3252d397`) and `v0.9.0` (peeled `5a60a7c2`); GitForge is reachable again (supersedes V12's "unreachable" for tags) |
| V15 | `curl -s https://api.github.com/repos/aliasfoxkde/py7zip/releases` | Exactly 2 releases: `v0.9.0` (2026-10-03) and `v0.8.0` (2026-09-29), both non-draft, each with wheel + sdist assets |
| V16 | `curl -s https://api.github.com/repos/ip7z/7zip/releases/latest` | Still `26.04` (published 2026-10-06T07:55:39Z); 16 assets, **every asset carries a `digest` field**; `7z2604-linux-x64.tar.xz` digest unchanged: `sha256:fc0327ba…53ffcd` == V8; `7z2604-mac.tar.xz` size 1,861,928, digest `sha256:bee04358cbcbc7106273cee0e8d72916db2696c48067a3538c34d8cd6fd16578` |
| V17 | Download `7z2604-mac.tar.xz`; `sha256sum`; `tar -tJf`; `file` on contents (no execution) | Local sha256 `bee04358…` == API digest (V16); contains **one universal Mach-O `7zz` (x86_64 + arm64, 6,051,824 bytes)** plus `License.txt`, `readme.txt`, `History.txt`, `MANUAL/` — the official macOS release **is** a universal binary in a single tarball |
| V18 | `strings -a bin/mac/any/7za \| grep '7-Zip (z)'` (static, no execution) | Both slices embed official-format banners: `7-Zip (z) 24.00 (x64) … : 2024-01-30` and `7-Zip (z) 24.00 (arm64) … : 2024-01-30` |
| V19 | Historical 24.00 anchoring probe (detail in A.8) | No GitHub release/tag `24.00` exists (release list: 21.07, 22.00, 22.01, 23.01, 24.05…26.04; tag API → 404); `7-zip.org/a/7z2400-*.tar.xz` → 404 today; SourceForge has no `7-Zip/24.00` directory; Wayback snapshot of `download.html` (2024-02-15) shows the official 24.00 artifacts at `a/7z2400-*.tar.xz`; `7z2400-linux-x64.tar.xz` **is archived** (2024-02-21 snapshot) and its inner `7zz` sha256 `12ef1251…` == bundled `bin/lin/pc/x64/7za`; `7z2400-mac.tar.xz` has **no located archived copy** |
| V20 | *(2026-10-11, revision 3)* Download `py7zip-0.6.2.tar.gz` sdist from PyPI; `sha256sum`; `tar -xzf`; `grep -n` the wrapper | sdist sha256 `ca0f81b3eb4367fc4d54959eecad01d7155cc06db84a52fbcec685ec6dfd68d6`; its `py7zip/py7zip.py` defines `cd` (l. 48), `full`/`incremental`/`differential` (l. 110–112), `snapshot` (l. 114) — **all five methods ship in the release 0.6.2 users actually run** (git anchor: same methods at `69927d5`, 2024-02-24, one day before the PyPI upload). Grounds the OVH-14 upgrade sequence |

**Probe artifacts are not part of this document, and are not acceptance
artifacts.** Transient copies of the downloads behind V8/V17/V19/V20 were
relocated to `/nas/Temp/artifacts/py7zip-probes-20261011/` (outside Git;
GC-eligible scratch). Every fact above is reproducible from the cited
URL + command + digest. Classification rule: fixed host paths appearing in
evidence rows (e.g. V2's wheel under `/var/tmp`) describe historical probe
runs only — they are evidence, never requirements. **No acceptance
criterion in this plan may require a `/var/tmp` or `/nas` path to exist**,
and every acceptance command that produces files must create runner-owned
scratch itself (`mktemp -d`, honoring `TMPDIR`), as §6 OVH-01 now does.

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
   (`py7zip/py7zip.py:9,84–114`); the safe runtime is stdlib-only
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
11. *(2026-10-11, V18)* The bundled universal macOS binary embeds
    official-format **24.00** banners in both slices (`7-Zip (z) 24.00
    (x64)` / `(arm64)`, build date 2024-01-30) — established by static
    `strings` inspection only; the binary was not executed (per
    `AGENTS.md` this yields version evidence, not platform support).
12. *(2026-10-11, V19)* The bundled Linux x64 binary is **byte-identical**
    (sha256 `12ef1251…783fb3081`) to the official dynamic `7zz` inside
    `7z2400-linux-x64.tar.xz` recovered from the Wayback-archived official
    URL (`web.archive.org/web/20240221221419/https://7-zip.org/a/…`,
    tarball sha256 `3bb85b82…ad49b90ff` as computed locally — upstream
    published no digest for 24.00). This is the first anchored provenance
    row; the bundled file is a renamed copy of upstream `7zz`.

### 3.2 Verified upstream (fetched 2026-10-10; re-verified 2026-10-11, V13–V19)

| Fact | Source |
|------|--------|
| Current upstream release: **7-Zip 26.04** (page dated 2026-10-05; release published 2026-10-06T07:55:39Z; unchanged at re-check) | <https://www.7-zip.org/download.html>; <https://api.github.com/repos/ip7z/7zip/releases/latest> |
| Linux artifacts (tar.xz, console): `7z2604-linux-x64.tar.xz`, `…-linux-x86.tar.xz`, `…-linux-arm64.tar.xz`, `…-linux-arm.tar.xz`; **no musl variants listed** (page contains no "checksum" and no "musl" text; re-checked 2026-10-11) | download.html (above) |
| macOS: single universal `7z2604-mac.tar.xz` (arm64/x86-64) whose **sole binary is one universal `7zz` Mach-O (x86_64 + arm64, 6,051,824 bytes)**, alongside `License.txt`, `readme.txt`, `History.txt`, `MANUAL/`; asset digest `sha256:bee04358…d16578` verified equal to a locally computed digest (V17) | download.html; GitHub API asset digest (V16); tarball contents (V17) |
| Windows: installers `7z2604-x64.exe`/`7z2604.exe`/`7z2604-arm64.exe`, MSI alternatives, and `7z2604-extra.7z` ("standalone console version, 7z DLL…") — the console binary is distributed **inside a .7z package** | download.html (above) |
| Official release assets are hosted on GitHub: `github.com/ip7z/7zip/releases`; **the GitHub API exposes a per-asset `digest` (sha256) field** (re-confirmed on all 16 assets of 26.04), verified equal to a locally computed digest (V8, V16) | api.github.com (above) |
| The official download page and release body publish **no checksum list and no signatures** (checksum.html does not exist — HTTP 404, re-checked 2026-10-11) | download.html; `https://www.7-zip.org/checksum.html` → 404; release body |
| Official Linux x64 tarball contains `7zz` (dynamic, glibc ≤ 2.16) **and `7zzs` (statically linked)** plus `License.txt`, `MANUAL`, `readme.txt` | V8/V9 (artifact contents, upstream URL above) |
| **Historical releases: GitHub has no 24.00** — the ip7z/7zip release list is 21.07, 22.00, 22.01, 23.01, 24.05–24.09, 25.00–26.04 (16 releases; tag `24.00` → API 404). The 24.00-era Linux/mac console artifacts were hosted only at `https://www.7-zip.org/a/7z2400-*.tar.xz` (proven by the Wayback snapshot of download.html, 2024-02-15) and are **pruned today** (404). `7z2400-linux-x64.tar.xz` survives in the Wayback Machine (snapshot 2024-02-21); `7z2400-mac.tar.xz` has **no located archived copy** (GitHub, SourceForge, 7-zip.org, Wayback all checked) | <https://api.github.com/repos/ip7z/7zip/releases>; <https://web.archive.org/web/20240215060208/https://www.7-zip.org/download.html>; V19/A.8 |
| License: LGPL-2.1-or-later for all files; `7z.dll` additionally BSD-3-clause (LZFSE, ZSTD) and BSD-2-clause (XXH64); unRAR restriction; **"Redistributions in binary form must reproduce related license information"** | <https://www.7-zip.org/license.txt> |

### 3.3 Inferred (reasoning stated, not directly executed)

- The 7 bundled binaries are most plausibly official-format upstream builds
  (banner format identical to official; copyright line is Igor Pavlov's) at
  version 24.00 for Linux x64 — now **anchored** in one case: Linux x64 is
  byte-identical to official 24.00 `7zz` (§3.1 item 12). The remaining six
  rows have no recorded per-file provenance, so OVH-02 must treat every
  unanchored file as UNPROVEN until ledgered.
- **macOS (corrects revision 1):** the official macOS release layout itself
  *is* a single universal binary — `7z2604-mac.tar.xz` contains one
  universal `7zz` Mach-O (x86_64 + arm64), verified 2026-10-11 (V17). A
  universal `bin/mac/any/7za` is therefore fully consistent with an
  official-format origin, and static banner evidence pins its version at
  **24.00** for both slices (V18). What remains **unverified** is
  byte-identity to an official 24.00 mac asset: that asset is pruned from
  `7-zip.org/a/`, absent from GitHub (no 24.00 release) and SourceForge,
  and has no located Wayback copy — so the check cannot be performed today
  (V19). The bundled mac binary is accordingly *version-evidenced but
  UNPROVEN for provenance*; the row is resolved only by OVH-02's ledger
  plus the OVH-29 gate (anchor, re-acquire from a current release, or
  record an explicit maintainer exception).
- Windows arm paths (`bin/win/arm/x32/7za`, `bin/win/arm/x64/7za`) are
  0-byte placeholders with no catalog entries; upstream ships a real
  `7z2604-arm64.exe` installer — a support surface the catalog could serve
  later.

### 3.4 Unknown (do not guess; task-linked)

- U1: Exact upstream origin (URL + release tag) of **each** of the 7
  binaries — **partially resolved 2026-10-11**: Linux x64 is anchored
  (official 24.00 `7zz`, byte-identical, §3.1 item 12); the other six rows
  remain unanchored → OVH-02 (same archival procedure per row).
- U2: Whether official Linux builds run on musl/Alpine → resolved for the
  overhaul by D-OVH-3 (prefer static `7zzs`; no musl claim without a
  receipt per `AGENTS.md`).
- U3: macOS binary provenance — **version dimension resolved** (24.00 both
  slices, static banner evidence, V18); **provenance/byte-identity still
  unknown** (no archived official 24.00 mac asset exists to compare
  against, V19) → OVH-02 row, and **OVH-29 must resolve or explicitly
  disposition it before any darwin asset is pinned** in the OVH-09
  catalog.
- U4: Whether PyPI trusted publishing is configured for this project on
  PyPI (workflows are written for it; no publish has ever run) → OVH-21
  **trusted-publishing dry-run** (the release task — revision 1 mispointed
  this at OVH-18, the CLI task).
- U5: GitForge CI availability (V12: unreachable at audit time; tags
  reachable again 2026-10-11, V14 — CI-run availability still unproven) →
  receipts for OVH-23 may need GitHub Actions instead.

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

**Ledger rules.** IDs are assigned in plan-revision order; execution order
is defined by the **Phase** column plus **Depends on**, never by row order
(OVH-26–29 sit at the end of the table but execute inside P0/P1/P2).
Decision tasks (**OVH-06–08, OVH-26–29**) and the **publication gate inside
OVH-21** are *gates*: a consuming task must not start until the decision
record it depends on exists, and no phase may skip a gate — an implementer
who reaches a gated task without its decision record stops and escalates to
the owner instead of proceeding on a default.

### 5.1 B0 critical path (what actually blocks the release)

Release-blocking, and nothing else: **OVH-01 → OVH-02 → OVH-26 (audit D4
receipt decision) → (OVH-03, OVH-04) → publication gate (audit
P0.5/D3, taken inside OVH-21) → OVH-21.** OVH-05 is **landed** (PR #22,
`d606b75`) and no longer part of the open path. OVH-21's dependency on OVH-20 is
**conditional**: it applies only if D-OVH-4 changes the packaging
(platform wheels); if D-OVH-4 keeps the current no-binary wheel +
official-fetch model, the release does not wait on the P1 spine at all
(matching §1). Explicitly **not** release-blocking: the CLI port (OVH-18),
local-binary discovery + PR #8 disposition (OVH-17), legacy sunset
(OVH-19), multi-OS CI (OVH-22), platform receipts (OVH-23), extraction
policy (OVH-24), SECURITY.md/support policy (OVH-25), and the
audit-line-integration decision (OVH-06) except where OVH-18 consumes it.

| ID | Phase | Task | Owner | Depends on | Consumes |
|----|-------|------|-------|-----------|----------|
| OVH-01 | P0 | Fix invalid trove classifiers + Development Status | Impl | — | new (this doc, V3/V4) |
| OVH-02 | P0 | Artifact provenance ledger (`bin/PROVENANCE.md`) | Sec | — | P0.4 |
| OVH-03 | P0 | Docs truth-pass (docs/USAGE, docs/FEATURES, docs/SETUP) | Docs | — | P0.2 |
| OVH-04 | P0 | Platform-claim reconciliation (README checklist) | Docs+Maint | OVH-02, OVH-26 | P0.1 |
| OVH-05 | P0 | ~~Fix `get_binary_url()` safe-path bug~~ — **LANDED** (PR #22, `d606b75`) | Impl | — | P0.3 |
| OVH-06 | P1 | Decision: integration strategy for audit line | Maint | — | new (D-OVH-1) |
| OVH-07 | P1 | Decision: Windows bootstrap source | Maint | — | new (D-OVH-2) |
| OVH-08 | P1 | Decision: Linux binary policy (7zz/7zzs/musl) | Maint+Sec | — | new (D-OVH-3) |
| OVH-09 | P1 | `upstream.py` release catalog module | Impl | OVH-02, OVH-08, OVH-29 | P2.1 |
| OVH-10 | P1 | libc detection + typed refusal | Impl | OVH-08 | new |
| OVH-11 | P1 | Official acquisition + dual-channel verify + license install | Impl | OVH-09 (inherits OVH-29 via OVH-09) | P2.1 |
| OVH-12 | P1 | Versioned cache, `update()`/`status()` API | Impl | OVH-11 | new |
| OVH-13 | P1 | Windows acquisition path per OVH-07 | Impl | OVH-07, OVH-09 | new |
| OVH-14 | P2 | Deprecate, then remove snapshot stubs + `cd` (two commits, §6) | Impl | — | P1.2 |
| OVH-15 | P2 | Root re-export `Py7zip`, `__version__` | Impl | OVH-14 | P1.3 |
| OVH-16 | P2 | Options bridge decision + impl | Maint+Impl | — | P1.1, audit D5 |
| OVH-17 | P2 | Local-binary discovery (PR #8 rework) + PR disposition *(post-B0; gated)* | Impl+Maint | OVH-14, OVH-28 | P1.4 (audit D2), P1.6 |
| OVH-18 | P2 | CLI surface (port from audit line) *(post-B0, optional scope)* | Impl | OVH-06, OVH-15 | new |
| OVH-19 | P3 | Legacy sunset; drop `requests` dependency | Impl+Maint | OVH-16, OVH-27 | P1.5 (audit D1) |
| OVH-20 | P3 | Decision + impl: distribution model *(gates OVH-21 only if packaging changes)* | Maint | OVH-11 | new (D-OVH-4) |
| OVH-21 | P3 | Release cut from main → PyPI (fixes B0) | Rel | OVH-01…05; OVH-20 only if D-OVH-4 changes packaging; publication gate (audit D3) taken in-task | **audit P0.5 (D3 publication decision)** |
| OVH-22 | P4 | Multi-OS CI lanes + 3.14/classifier alignment | Maint | — | P2.2 |
| OVH-23 | P4 | Platform qualification receipts (CI, not local) | QA | OVH-11, OVH-22 | P2.3 |
| OVH-24 | P4 | Extraction-safety policy completion (symlinks/overwrite) | Impl+Sec | — | P2.4 |
| OVH-25 | P4 | SECURITY.md + support policy + release hygiene *(post-B0 policy work)* | Sec+Maint | OVH-02 | P0.4 rest, P2.5 |
| OVH-26 | P0 | **Gate:** Windows/WSL receipt audit — does evidence exist for the README's tested claims? | Maint | — | audit D4 |
| OVH-27 | P2 | **Gate:** legacy-runtime sunset window/removal version | Maint | — | audit D1 |
| OVH-28 | P2 | **Gate:** local-binary precedence policy (PATH-discovered vs pinned-catalog-first) | Maint (security hat) | — | audit D2 |
| OVH-29 | P1 | **Gate:** macOS support surface + provenance resolution (U3) before any darwin asset is pinned | Maint+Sec | OVH-02 | new (this doc, §3.2/V17–V19; D-OVH-6) |

Phase rationale: **P0** makes the tree releasable and truthful (B0
prerequisites; all docs/test-only or one-line code fixes; includes the
OVH-26 receipt gate). **P1** is the overhaul core — decisions before code
(OVH-06/07/08/29), then the upstream-anchored acquisition spine. **P2**
finishes the Pythonic API surface and unblocks legacy removal (OVH-27/28
gates inside it). **P3** ships (B0 cleared; OVH-19 legacy sunset and OVH-20
distribution decision land here, with OVH-20 gating OVH-21 only if
packaging changes). **P4** hardens claims (CI lanes, receipts, safety
policy). Receipts per `AGENTS.md` are the gate between P3 and any
support-claim promotion.

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
Acceptance (all must pass; wheel outputs go to runner-owned scratch —
`mktemp -d`, honoring `TMPDIR` — never a fixed `/var/tmp` path, §2.1):
```
scratch="$(mktemp -d)"
python3 -m pip wheel . --no-deps --no-build-isolation -w "$scratch/ovh01a"   # V4 must now succeed
python3 -m pip wheel . --no-deps -w "$scratch/ovh01b"                        # V2 stays green
python3 -m twine check "$scratch"/ovh01a/*.whl
python3 -m pytest tests -p no:cacheprovider -q   # green; V1 recorded 128 at the 9d428da baseline, before PR #22 added one test
```
Rollback: revert the single commit. Risk: none at runtime (metadata only).

**OVH-02 — Artifact provenance ledger.** New `bin/PROVENANCE.md`: one row
per non-empty binary — upstream version (banner probe, V6-style), where
obtained, upstream-published anchor (URL/digest) or explicit `UNKNOWN`,
check date; plus the 6 placeholder paths marked "empty, not distributed".
Start from V5/V6/V7 plus the 2026-10-11 evidence: the Linux x64 row can
cite the byte-identity anchor (official 24.00 `7zz`, archived URL +
computed tarball digest — upstream published no digest for 24.00-era
assets, so the row records that TOFU caveat explicitly, §3.1 item 12);
the macOS row records version 24.00 (static banner, V18) with
provenance UNPROVEN and is adjudicated by gate **OVH-29**; the remaining
rows follow the same archival procedure per artifact (V19 method).
Acceptance: `find bin -type f -size +0c | sort` has exactly one ledger
row each, and any `UNKNOWN` row links the follow-up task (OVH-29 for the
darwin row). Consumed later by OVH-09/11. Rollback: revert (docs only).

**OVH-03 — Docs truth-pass** per landed P0.2 (`docs/USAGE.md` import line,
`docs/FEATURES.md` stub labeling, `docs/SETUP.md` publish flow). Acceptance:
every import/command line in the edited docs executes in a clean
interpreter; no doc references `setup.py`/`push.bat` as current.

**OVH-04 — Platform-claim reconciliation** per landed P0.1 (which depends
on audit decision **D4** — wired here as gate OVH-26), now with OVH-02's
ledger as the receipt source. Acceptance:
`grep -n "\[x\]" README.md` returns only receipt-backed rows.

**OVH-05 — `get_binary_url()` safe path — LANDED (PR #22, `d606b75`).**
Per landed P0.3 (F2: returned a nonexistent fabricated cache-relative
path on the default runtime). As merged, the safe path raises
`NotImplementedError` directing callers to `download_binary()`/
`ensure_binary()` or a pre-verified `binary_path=` constructor argument —
a deliberate deviation from this spec's original "delegate to
`ensure_binary()`" preference, keeping acquisition explicit instead of
implicit on attribute access. The legacy branch stayed byte-identical and
the pinning test `test_get_binary_url_raises_on_safe_runtime` landed at
`tests/test_default_api.py:33` (with a `.github/CHANGELOG.md` entry).
Nothing open; retained for the record and rollback history.

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
**Bounded deadline:** D-OVH-2 is to be taken in the same maintainer pass
that discharges gate OVH-26 (both turn on the same Windows-evidence
question), and **no later than the OVH-09 catalog-freeze commit** — OVH-09
must not pin a `windows/*` row whose asset source D-OVH-2 has not chosen
(already enforced by OVH-13's `Depends on`).
**Governed fallback while the decision is open:** the §1 "Windows on the
B0 path" behavior — checksum-pinned repo-hosted binaries, provenance rows
UNPROVEN in the OVH-02 ledger, no support claim, release-notes
disclosure. The fallback may cover **at most the first release after B0
clearance**; if D-OVH-2 is still unrecorded when a subsequent release is
cut, that release's notes must carry an explicit "Windows
upstream-acquisition decision overdue" notice and the gate escalates to
the maintainer — the fallback is never silently re-extended.

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
platform/architecture").
Acceptance (all must pass):
```
python3 -m pytest tests/test_acquisition.py tests/test_upstream.py -q    # offline suite subset
python3 -m pytest tests -p no:cacheprovider -q                           # full offline suite green
```
plus, as table-driven offline tests with a fake transport (extend
`tests/fakes.py`, `FakeUrllibRequest` at `tests/fakes.py:126`):
1. **Digest-mismatch fails closed, before install or use**: the fake
   transport serves a payload whose sha256 ≠ the catalog pin →
   `ArtifactIntegrityError` (`py7zip/acquisition.py:21`, raised by
   `_verify`, `py7zip/acquisition.py:102–114`) and the assertion set must
   include: the destination/install path does **not** exist afterwards and
   no subprocess was spawned (proves failure precedes install *and* use —
   this is the test backing the §7 risk promise "digest mismatch fails
   loudly, never silently").
2. The same fail-closed assertion for a **tampered archive member** at the
   unpack stage (member content ≠ the digest the catalog pins for it), and
   for the online second channel (API `digest` ≠ local digest → refuse
   install).
3. One `@pytest.mark.integration` probe guarded by env var, recording
   platform/architecture per `AGENTS.md` — the marker must be registered
   in `pyproject.toml` (`[tool.pytest.ini_options] markers = [...]`),
   since the suite runs with `--strict-markers` (`pyproject.toml:44`).

**Gate status of env-guarded integration probes.** The probe is a
deliverable of OVH-11 but **is not a gate** — not for OVH-11, not for
OVH-21. The gates are the two offline acceptance commands plus the
table-driven offline tests 1–2; the offline suite never sets the opt-in
env var, and CI lanes must not set it. What OVH-11 must ship is the probe
*existing*: registered marker, env-guarded, skipped by default. When a
maintainer opts in on real hardware, the run's output becomes evidence
for OVH-23 receipts under the `AGENTS.md` promotion rule — so an unrun
probe blocks **support claims**, never the release. A probe run records
exactly one of §6.2's enumerated rows.

Rollback: revert the commit; the pre-existing acquisition tests
(`tests/test_acquisition.py`, incl. `test_manager_rejects_corrupt_cached_artifact`
at `tests/test_acquisition.py:48`) keep pinning current behavior.

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

**OVH-14** deprecate, then remove `full/incremental/differential/snapshot`
and `cd` (silent no-ops / process-global mutation;
`docs/planning/COMPATIBILITY.md` already schedules this).
**Why not direct removal:** every one of the five methods exists and is
callable in the 0.6.2 sdist users actually run (V20 — `cd` l. 48,
family l. 110–114), and PyPI users are still on 0.6.2 (V13). Direct
removal converts today's silent success into an `AttributeError` on
upgrade with no warning ever shown; the sequence below gives every
upgrade path a visible signal while behavior is unchanged.
**Commit 1 — deprecate:** keep all five methods with unchanged
no-op/`chdir` behavior; each call emits `DeprecationWarning` naming the
planned removal version and the migration (family: no replacement — they
never did anything; `cd`: manage the working directory in caller code).
Update the characterization pins in the same commit
(`tests/test_characterization_wrapper.py:300–353`) to assert the warning
via `pytest.warns` — never delete or weaken them (COMPATIBILITY.md rule
3); note the suite runs with `filterwarnings = ["error"]`
(`pyproject.toml:45`), so an unasserted warning fails the suite by
design. Mirror both COMPATIBILITY.md migration rows in the same commit:
the family row currently says the stubs are removed in Phase 4 with no
window, while the `cd` row already prescribes deprecation before removal
— both are harmonized here onto one deprecate-then-remove sequence.
**Commit 2 — remove (next feature release):** delete the methods; update
the same tests to pin absence; release notes carry the migration callout.
Gate: commit 2 merges only after the deprecating release is verifiably on
PyPI (re-run the OVH-21 enumeration commands), so no user can upgrade
0.6.2 → removal without a deprecation-carrying release published in
between.
Acceptance, commit 1:
`python3 -m pytest tests/test_characterization_wrapper.py -q` green with
warning-asserting pins.
Acceptance, commit 2:
`python3 -c "from py7zip.py7zip import Py7zip; print([hasattr(Py7zip, m) for m in ('full','incremental','differential','snapshot','cd')])"` → all `False`,
plus full offline suite green.

**OVH-15** root re-export `py7zip.Py7zip`, `py7zip.__version__` (additive;
update the pinned hygiene test in the same commit, never weaken silently).
Acceptance: `python3 -c "import py7zip; py7zip.Py7zip"` offline-clean.

**OVH-16** options story (records audit decision **D5**): keep `TypeError`
for string options on the safe path; if a bridge exists, `shlex.split`
behind explicit opt-in only; document in `docs/USAGE.md`;
`docs/planning/COMPATIBILITY.md` row updated same-commit. Acceptance:
`pytest tests/test_default_api.py tests/test_safe.py -q`.

**OVH-17** local-binary discovery per landed P1.4 — **post-B0 scope, gated
by OVH-28 (audit D2)**: opt-in, precedence documented, never implicit in
`__init__`; then disposition **PR #8** (open, `webbrain/issue-7`,
"support local 7zip installations…") — close as superseded or hand to
author, crediting the analysis. The PR #8 disposition half (audit P1.6) is
maintainer follow-up after this task merges; neither half blocks OVH-21.
Acceptance: offline unit tests with a fake `PATH` prove default-runtime
behavior is unchanged (no implicit search/download); precedence matches
the OVH-28 record.

**OVH-18** CLI per OVH-06 outcome — **post-B0, optional scope** (port of
the audit line's CLI; not required to clear B0, §5.1): argparse surface
with typed exit codes and `--`-terminated 7-Zip switches (the audit line
already solved two e2e defects here: `-o/--option` untypeable → `--`;
differential re-run errno-17). If porting, keep its tests. Acceptance:
console script present (`[project.scripts]`), `py7zip --help` and
exit-code table documented, offline CLI tests green.

### P3 — packaging and the release that clears B0

**OVH-19** deprecation warning on `legacy=True` with a removal version —
**the window/removal version is audit decision D1, wired here as gate
OVH-27** (and the options story of OVH-16 must exist first, so legacy
callers have a documented migration path); drop `requests`
(`pyproject.toml:16`) when legacy retires. Acceptance: fresh-venv
`pip install .` pulls no `requests`; `grep -r "import requests" py7zip/`
empty.

**OVH-20** distribution model decision (D-OVH-4): (i) keep no-binary wheel
+ official-release fetch (current shape, minimal repackaging risk; needs
OVH-11 mature), or (ii) per-platform wheels bundling verified binaries
(offline installs; heavier release machinery; license files must ship —
see OVH-11's `License.txt` requirement and `AGENTS.md`'s
"keep 7-Zip's upstream license notices with distributed binary assets").
Deliverable: decision record + packaging change + `twine check`. **Gate
relation to the release:** outcome (i) leaves OVH-21 with no dependency on
this task; only outcome (ii) puts OVH-20 on the release path (§5.1).

**OVH-21 — Release cut (clears B0).**
*Publication decision first (consumes audit **P0.5**, decision **D3**):*
option (a) publish now, acknowledging pip users are on legacy 0.6.2, or
(b) a recorded decision + dated issue explaining the delay. Option (a)
requires, per audit P0.5's gate, that every OVH-02 provenance row is
upstream-anchored **or** carries an explicit maintainer exception naming
the artifact, its UNKNOWN row, and its open investigation task (§3.1 item
12 anchors the Linux x64 row; the OVH-29 outcome governs the macOS row).
An unadjudicated UNKNOWN row forces outcome (b).

*Version and tag selection (collision-safe — the audit line's
`v0.8.0`/`v0.9.0` are occupied, V14/V15):* before choosing, enumerate every
occupied version and never reuse one:
```
git fetch origin --tags && git ls-remote --tags origin && git ls-remote --tags gitforge
curl -s https://api.github.com/repos/aliasfoxkde/py7zip/releases | grep -o '"tag_name": *"[^"]*"'
curl -s https://pypi.org/pypi/py7zip/json | grep -o '"[0-9]*\.[0-9]*\.[0-9]*"' | sort -Vu
```
Verified occupied set (2026-10-11): PyPI {0.3.0–0.6.2}, in-tree 0.7.3
(unpublished), remotes + GitHub Releases {v0.8.0, v0.9.0}. Rules: the
release version is the smallest unused version ≥ `pyproject.toml`'s
(smallest free as of 2026-10-11 is 0.7.4; if the release ships the P1
overhaul content, prefer ≥ 0.10.0 to avoid implying continuity with the
already-published audit-line 0.8.0/0.9.0 releases — final pick belongs to
Rel, re-running the enumeration at release time); **never create a tag
that already exists, never overwrite, force-move, or delete a tag**
(`git push --force` is prohibited; create with `git tag -s v<version>` —
it fails if the ref exists, which is the guard — and verify with
`git push --dry-run origin v<version>` before the real push). The
`publish.yml` tag/version gate (`.github/workflows/publish.yml:28–35`)
must pass as-is.

*Trusted publishing (resolves U4):* run a **trusted-publishing dry-run
before the release** — repository setting *Settings → Environments →
pypi* must show the trusted publisher, exercised via a
`workflow_dispatch` run of `.github/workflows/publish.yml` against a test
index if available, or verified by a maintainer in the PyPI project
settings UI; either way the check and its log are attached to the release
receipt (U4 is unknown: the workflow is written for trusted publishing,
`.github/workflows/publish.yml:10` (`id-token: write`), but no publish
has ever run).

*Receipts* per `AGENTS.md` promotion rule (commit, Python, OS/arch,
binary provenance, test results, skipped lanes). Acceptance:
`pip install py7zip==<version>` in a fresh venv returns the safe-default
runtime (`Py7zip().legacy is False`); PyPI page shows the new metadata;
`git ls-remote --tags origin` shows exactly one new tag and both
pre-existing tags unmodified (same SHAs as V14).
Rollback: PyPI releases are immutable — ship a patch release; do not
attempt deletion. Tag rollback before an accidental publish: delete the
local tag and the *just-created* remote tag only if no release objects to
it — never touch v0.8.0/v0.9.0.

### P4 — CI, receipts, policy

**OVH-22** add `windows-latest`/`macos-latest` lanes of the same offline
suite; reconcile 3.14 classifier vs matrix. Acceptance: three green OS
lanes; classifier set == tested set.
**OVH-23** platform receipts executed on CI runners (not local hardware),
each receipt = exact Python/OS/arch/binary provenance/commands/result;
matrix tiers promoted only with receipts. GitForge is a possible runner
(U5: CI-run availability unproven — tag access recovered 2026-10-11, V14;
GitHub Actions is the fallback).
**OVH-24** extraction-safety policy (symlink members, overwrite,
partial-output) — document scope as member-path-traversal rejection unless
a link audit is implemented; tests for whatever is claimed.
**OVH-25** `SECURITY.md`, support-policy page (tiers from
`docs/planning/PLATFORM_MATRIX.md`), fix/drop dead `Project Page` URL
(F14), release process single-sourced.

### 6.1 Gate task specifications

**OVH-26 — Gate (P0): Windows/WSL receipt audit (audit D4).** Owner: Maint.
Files: none required to start; output is the input OVH-04 needs (audit P0.1
depends on D4: "is F1 a doc fix or a false claim to retract?").
Deliverable: a one-page decision record in `docs/planning/` answering, with
cited receipts or their absence, whether Windows x64 / WSL qualification
receipts exist for the README checklist and the 0.7.3 changelog claim.
Commands: search the repo and issue/PR history for receipts —
```
grep -rn "WSL\|windows" README.md docs/planning/PLATFORM_MATRIX.md docs/CHANGELOG.md
git log --all --oneline --grep="windows\|wsl" -i
gh search issues --repo aliasfoxkde/py7zip "windows receipt"
```
Acceptance: the record names every README `[x]` row and marks it
receipt-backed / to-uncheck; OVH-04 cannot start before this record
exists (ledger rule, §5).
Rollback/decision handling: docs-only revert; the decision itself is
recorded, not silently defaulted — if no receipt is found, the outcome is
"uncheck claims", never "assume support".

**OVH-27 — Gate (P2): legacy-runtime sunset window (audit D1).** Owner: Maint.
Files: decision record in `docs/planning/` (row mirrored into
`docs/planning/COMPATIBILITY.md` in the OVH-19 commit, not before).
Deliverable: the removal version and deprecation window for `legacy=True`,
deciding when `requests` can be dropped (audit F8). Evidence to weigh:
safe runtime is already default (`legacy=False`, `py7zip/py7zip.py:23`),
PyPI users are
still on 0.6.2 (V13) so no released user depends on the current
`legacy=True` flag shape.
Acceptance: named removal version + window; OVH-19 blocked without it.
Rollback: revise the record (a decision, not code).

**OVH-28 — Gate (P2): local-binary precedence policy (audit D2).** Owner: Maint
(security hat). Files: decision record in `docs/planning/`.
Deliverable: choose PATH-discovered-first vs pinned-catalog-first for
opt-in local-binary discovery (OVH-17), with the trust implication of
executing a user-writable binary stated. Acceptance: OVH-17 blocked
without it; the chosen precedence appears verbatim in OVH-17's docs.
Rollback: revise the record.

**OVH-29 — Gate (P1): macOS support surface + provenance resolution (U3,
D-OVH-6).** Owner: Maint+Sec. Depends on: OVH-02 (the ledger rows this
gate adjudicates). Files: decision record in `docs/planning/`; possible
`bin/PROVENANCE.md` update.
Deliverable — pick and record exactly one per darwin row, before OVH-09
pins any darwin asset:
(a) **Anchor**: byte-identity to an official asset. Current evidence makes
    this unavailable for 24.00 (the official mac asset is pruned from
    `7-zip.org/a/` and unarchived — V19); re-run the availability check at
    gate time before concluding.
(b) **Re-acquire**: drop the legacy `bin/mac/any/7za` row and pin the
    current official universal asset (`7z2604-mac.tar.xz`, digest
    `sha256:bee04358…d16578`, V16/V17) as the catalog's darwin entry —
    version evidence (V18) and layout (V17) support this as the
    recommended outcome.
(c) **Exclude**: no darwin entry in the OVH-09 catalog for this release;
    unsupported-platform refusal until a receipt exists.
Commands:
```
curl -s -o /dev/null -w '%{http_code}\n' https://www.7-zip.org/a/7z2400-mac.tar.xz
curl -s "http://archive.org/wayback/available?url=www.7-zip.org/a/7z2400-mac.tar.xz"
strings -a bin/mac/any/7za | grep -m2 '7-Zip (z)'
```
Acceptance: the record names the chosen outcome, the provenance row it
dispositions, and the OVH-09 catalog consequence; OVH-09 must not carry a
darwin entry whose provenance is neither (a) nor (b).
Rollback: docs-only revert; re-acquisition path (b) additionally reverts
the catalog commit.

### 6.2 Supported platform/architecture rows (acceptance binding)

These are the only rows acceptance criteria and claims may refer to —
exactly what `ArtifactCatalog` resolves today (`py7zip/platforms.py:95–106`)
plus its typed refusals. Any receipt, README check, or catalog entry
outside this table would promote a claim this plan has not authorized.

| Row (`system/family/architecture`) | Artifact resolved | Provenance state | Bound to |
|------------------------------------|-------------------|------------------|----------|
| `linux/pc/x64` | `bin/lin/pc/x64/7za` | **Anchored** — byte-identical to official 24.00 `7zz` (§3.1 item 12) | OVH-02 row |
| `linux/pc/x86` | `bin/lin/pc/x86/7za` | UNPROVEN until ledgered | OVH-02 |
| `linux/arm/x64` | `bin/lin/arm/x64/7za` | UNPROVEN until ledgered | OVH-02 |
| `linux/arm/x32` | `bin/lin/arm/x32/7za` | UNPROVEN until ledgered | OVH-02 |
| `windows/pc/x64` | `bin/win/pc/x64/7za.exe` | UNPROVEN; §1 B0 fallback behavior applies | OVH-02; D-OVH-2 |
| `windows/pc/x86` | `bin/win/pc/x86/7za.exe` | UNPROVEN; §1 B0 fallback behavior applies | OVH-02; D-OVH-2 |
| `darwin/pc/x64` | `bin/mac/any/7za` (universal) | version-evidenced 24.00, provenance UNPROVEN (V18/V19) | OVH-29 adjudicates |
| `darwin/pc/x86` | `bin/mac/any/7za` (universal) | same artifact as above | OVH-29 |
| `darwin/arm/x64` | `bin/mac/any/7za` (universal) | same artifact as above | OVH-29 |
| `windows/arm/*`, `darwin/arm/x32`, any system outside {`linux`, `windows`, `darwin`} | **none — typed `UnsupportedPlatformError`** | refusal, documented (§3.3) | OVH-03 states it; no claim |

Bindings: **OVH-04** reconciles README rows 1:1 against this table — a
README line with no row above gets unchecked; **OVH-09** must carry an
entry or an explicit refusal for every row above, including the libc
dimension once OVH-08/10 land; **OVH-11**'s opt-in probe records exactly
one of these rows per `AGENTS.md`; **OVH-23** receipts are valid only for
rows executed on CI hardware. A lane or receipt for a row not in this
table is out of scope by definition.

## 7. Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| B0 persists while overhaul work continues; users keep receiving 0.6.2 | High | Reputation/security | P0 is deliberately small; OVH-21 is gated only by the §5.1 critical path (default ship at P3, fast path after P0 + D3) |
| Audit-line integration conflicts (duplicate commits, same files: `py7zip.py`, workflows, pyproject) | High | Rework | OVH-06 decision + conflict inventory before any port |
| Phase4 dirty worktree refreshes `bin/` concurrently with OVH-02/09/11 | Medium | Clobbered work / confused provenance | `bin/` frozen for this plan until that effort lands or is dispositioned (D-OVH-5); it is read-only to this handoff |
| Windows bootstrap complexity delays parity | Medium | Feature gap | OVH-07 bounded deadline + escalation (§6); the §1 governed fallback covers at most the first post-B0 release and is never silently re-extended |
| musl users lose support if dynamic binary chosen | Low | Support burden | OVH-08 recommends static `7zzs` — no libc constraint |
| Upstream release churn invalidates pins | Medium | Availability | Pins are per-wrapper-release; `update()` is explicit; digest mismatch fails loudly, never silently — proven by OVH-11 acceptance test 1 (offline tampered-payload → `ArtifactIntegrityError` before install/use) |
| Release version/tag collides with the audit line's published v0.8.0/v0.9.0 (tags on both remotes + GitHub Releases with assets, V14/V15) | High if unaddressed | Failed release or tag overwrite | OVH-21 selection procedure: enumerate PyPI + both remotes + GitHub Releases, take smallest unused, `git tag -s` fails on existing ref, `--dry-run` before push, force-move prohibited |
| License non-compliance when redistributing binaries | Low | Legal | Ship upstream `License.txt` beside every binary (verified it ships in the official 26.04 Linux and mac tarballs, V9/V17); AGENTS.md already requires it |
| Overloading scope: implementing everything before shipping | Medium | B0 drag | §5.1 separates the B0 critical path from optional/decision-gated scope; ship at P3 by default, or immediately after P0 + D3 via the fast path |

## 8. Decisions required (owner: Maintainer unless noted)

Every decision below is a ledger gate (§5 rules) — the consuming task
cannot start until the decision record exists.

This plan's decisions:

- **D-OVH-1** audit-line integration strategy (OVH-06; consumes: OVH-18,
  partly OVH-17).
- **D-OVH-2** Windows acquisition source (OVH-07; consumes: OVH-13;
  bounded deadline + governed fallback: §6 OVH-07).
- **D-OVH-3** Linux binary policy: static `7zzs` default recommended
  (OVH-08; consumes: OVH-09/10/11/13).
- **D-OVH-4** distribution model: runtime-fetch vs platform wheels
  (OVH-20; consumes: OVH-21 **only if** packaging changes, §5.1).
- **D-OVH-5** disposition of the phase4 binary-refresh effort vs
  upstream-anchored re-acquisition (they overlap; sequence before OVH-09).
- **D-OVH-6** macOS support surface + provenance resolution (OVH-29;
  consumes: OVH-09 darwin entries, OVH-11 darwin acquisition).

Landed audit's decisions (audit §10), each wired to a gate task:

- **D1** legacy-runtime removal version/window → **OVH-27**; consumes:
  OVH-19.
- **D2** binary-resolution precedence when a local 7-Zip exists →
  **OVH-28**; consumes: OVH-17.
- **D3** publish-now vs delay (audit P0.5) → **taken inside OVH-21** as the
  publication gate; consumes: OVH-21 (mapped in the Consumes column).
- **D4** do Windows x64 / WSL receipts exist → **OVH-26**; consumes: OVH-04.
- **D5** options-string bridge (`TypeError` vs opt-in `shlex.split`) →
  **recorded by OVH-16** (decision + impl in one task); consumes: OVH-19.

Source: `docs/handoffs/PLATFORM_ARCHITECTURE_PY7ZIP_2026-10-10.md` §10.

## 9. External work in flight (observed read-only; do not touch from this branch)

- `/nas/Temp/worktrees/py7zip-phase4-git` — branch `codex/py7zip-phase4-runtime`
  at `03abefb` ("fix: preserve executable mode for bundled binaries"), dirty:
  all 7 non-empty bundled binaries modified, sizes unchanged (V11). Not
  staged, not reset, not merged here.
- `/nas/Temp/repos/py7zip` — worktree on `audit/py7zip-qualification-20260909`
  at `7822d95` (0.9.0 line).
- PR #8 (`webbrain/issue-7`) open on `aliasfoxkde/py7zip` since 2026-08-06.
- Published GitHub Releases `v0.8.0`/`v0.9.0` with wheel+sdist assets
  (V15) and their tags on both remotes (V14) are **external surface —
  never overwrite, re-publish, or force-move them**; OVH-21 selects an
  unused version instead (§6 OVH-21).
- Local `main` ref is stale at `a7b396c` — run `git fetch origin` before any
  main-based work.
- GitForge remote was unreachable during the 2026-10-10 audit (V12); tag
  listing succeeded on 2026-10-11 (V14). CI-run availability on GitForge
  remains unproven (U5) — GitHub Actions is the fallback for OVH-23.

## 10. Next worker: start here

**Do OVH-01 only** (classifier fix + status bump, §6): metadata-only,
four acceptance commands, zero runtime risk, unblocks both CI packaging
and the release train. OVH-05 is already done (PR #22, `d606b75`), so
OVH-01 is the only remaining mechanical P0 task. Then bring OVH-02
(provenance ledger) to the maintainer with the V5–V9 evidence above —
OVH-02 now has a head start: the Linux x64 row can cite the byte-identity
anchor (§3.1 item 12), and the macOS row feeds gate OVH-29. In the same
maintainer pass, get **OVH-26 (audit D4)** answered and take **D-OVH-2**
(its bounded deadline rides on this pass, §6 OVH-07) — OVH-04 cannot
start without OVH-26 (§5 rules).

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

### A.5 Official-upstream probe (V8/V9; reproducible from the commands below)
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

### A.6 Upstream citations (fetched 2026-10-10; re-verified 2026-10-11)

- Official download page (artifact names, 26.04, GitHub/SourceForge links,
  no checksums, no musl variants):
  <https://www.7-zip.org/download.html>
- Official releases + per-asset digests:
  <https://api.github.com/repos/ip7z/7zip/releases/latest> (tag `26.04`,
  published 2026-10-06T07:55:39Z, 16 assets, all carrying `digest`);
  full release-tag list:
  <https://api.github.com/repos/ip7z/7zip/releases>
- Licensing (LGPL-2.1+, BSD-3/BSD-2 portions, unRAR restriction, binary
  redistribution must reproduce license information):
  <https://www.7-zip.org/license.txt>
- PyPI state (latest 0.6.2, 2024-02-25; full release set 0.3.0–0.6.2):
  <https://pypi.org/pypi/py7zip/json>
- This project's GitHub releases (v0.8.0, v0.9.0 with wheel+sdist assets):
  <https://api.github.com/repos/aliasfoxkde/py7zip/releases>
- Checksum page absent: `https://www.7-zip.org/checksum.html` → HTTP 404
- Historical 24.00 anchors: Wayback snapshot of the official download page
  showing `a/7z2400-*.tar.xz` links (2024-02-15):
  <https://web.archive.org/web/20240215060208/https://www.7-zip.org/download.html>;
  archived official Linux x64 tarball (2024-02-21):
  <https://web.archive.org/web/20240221221419/https://7-zip.org/a/7z2400-linux-x64.tar.xz>

### A.7 Topology (V10/V11)
```
origin/main = 68721cf  (9d428da + docs handoff PR #20)
merge-base(origin/main, audit/py7zip-qualification-20260909) = 4713a75
origin/main-only: 2    audit-only: 22
local main ref: a7b396c (stale)
tags: v0.8.0, v0.9.0 (audit line; not ancestors of origin/main)
phase4 worktree: dirty, 7 binaries modified (same sizes), HEAD 03abefb
```

### A.8 Revision-2 probes (V13–V19), 2026-10-11 — commands and outcomes

All downloads below are reproducible from these exact URLs; transient
copies live in GC-eligible scratch outside Git (§2.1) and nothing here
depends on them.

```
# V13 — PyPI state
curl -s https://pypi.org/pypi/py7zip/json
  → info.version = 0.6.2; releases keys = 0.3.0,0.4.0,0.4.1,0.4.2,0.5.0,0.6.0,0.6.2
    latest upload 2024-02-25T04:57:50Z; no 0.7.x/0.8.x/0.9.x

# V14/V15 — occupied versions on the project's own surfaces
git ls-remote --tags origin      → v0.8.0 (peeled 3252d397…), v0.9.0 (peeled 5a60a7c2…)
git ls-remote --tags gitforge    → same two tags
curl -s https://api.github.com/repos/aliasfoxkde/py7zip/releases
  → 2 releases, non-draft: v0.8.0 "py7zip 0.8.0 — Safe Runtime Qualification"
    (2026-09-29), v0.9.0 "py7zip 0.9.0 - Command-Line Interface" (2026-10-03);
    assets: py7zip-0.8.0/-0.9.0 wheel + tar.gz

# V16 — upstream 26.04 still current; digest field universal
curl -s https://api.github.com/repos/ip7z/7zip/releases/latest
  → tag 26.04, published 2026-10-06T07:55:39Z, 16 assets, each with digest
    7z2604-linux-x64.tar.xz digest sha256:fc0327ba…53ffcd (== V8)
    7z2604-mac.tar.xz       digest sha256:bee04358…d16578, size 1,861,928

# V17 — official macOS layout (download + listing + file; no execution)
curl -fsL -O https://github.com/ip7z/7zip/releases/download/26.04/7z2604-mac.tar.xz
sha256sum 7z2604-mac.tar.xz → bee04358cbcbc7106273cee0e8d72916db2696c48067a3538c34d8cd6fd16578
tar -tJf 7z2604-mac.tar.xz  → 7zz, readme.txt, History.txt, License.txt, MANUAL/
file 7zz → Mach-O universal binary with 2 architectures: [x86_64] [arm64]
           size 6,051,824 bytes

# V18 — bundled mac binary version (static only; binary not executed)
strings -a bin/mac/any/7za | grep '7-Zip (z)'
  → 7-Zip (z) 24.00 (x64)    : Copyright (c) 1999-2024 Igor Pavlov : 2024-01-30
    7-Zip (z) 24.00 (arm64)  : Copyright (c) 1999-2024 Igor Pavlov : 2024-01-30

# V19 — historical 24.00 anchoring
curl -s https://api.github.com/repos/ip7z/7zip/releases?per_page=100
  → tags: 21.07, 22.00, 22.01, 23.01, 24.05–24.09, 25.00, 25.01, 26.00–26.04
    (no 24.00)
curl -s https://api.github.com/repos/ip7z/7zip/git/ref/tags/24.00 → 404
curl -s -o /dev/null -w '%{http_code}' https://www.7-zip.org/a/7z2400-linux-x64.tar.xz → 404
curl -s -o /dev/null -w '%{http_code}' https://www.7-zip.org/a/7z2400-mac.tar.xz      → 404
curl -sIL .../sevenzip/files/7-Zip/24.00/7z2400-linux-x64.tar.xz/download      → 404
# Wayback download.html snapshot 2024-02-15 lists hrefs a/7z2400-{linux-*,mac}.tar.xz
# → the 24.00 console artifacts were hosted only at 7-zip.org/a/, now pruned
curl -fsL "http://web.archive.org/web/20240221221419/https://7-zip.org/a/7z2400-linux-x64.tar.xz"
sha256sum → 3bb85b8209a34e24e2938f0434fb0866e9a5750463478c82b977ca7ad49b90ff  (computed; upstream published none)
tar -xJf; sha256sum lin2400/7zz
  → 12ef12519899ecda8ba59940d7f25a3f4818c97693538d49e894e6b783fb3081
sha256sum bin/lin/pc/x64/7za (repo)
  → 12ef12519899ecda8ba59940d7f25a3f4818c97693538d49e894e6b783fb3081  (BYTE-IDENTICAL)
# mac 24.00 asset:
curl -s "http://archive.org/wayback/available?url=www.7-zip.org/a/7z2400-mac.tar.xz"
  → archived_snapshots: {}  (no archived copy located anywhere)
```
