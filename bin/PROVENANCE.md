# Artifact provenance ledger

One row per non-empty binary under `bin/`, plus the empty placeholder
slots. This ledger is the inventory of record for `bin/` (it supersedes
the older, conflicting lists in `INFO.md`, which now describes layout
only).

Conventions:

- **Anchored** = byte-identity (sha256) to a specific upstream-published
  artifact, with URL and digest recorded.
- **UNPROVEN** = no upstream anchor has been recorded for the file. The
  row states what *is* known (static format and banner evidence). An
  UNPROVEN row is not a claim of innocence or of support; it is an open
  item for the overhaul plan (OVH-02 rows; the darwin row is adjudicated
  by gate OVH-29 / D-OVH-6).
- Banner lines are static `strings` output. **No bundled binary was
  executed** to produce this ledger.
- "Introduced" is the commit that first added the file to this
  repository; the upstream source of every file was never recorded and
  is treated as unrecorded unless an anchor says otherwise.
- Checks re-run on **2026-10-20** (Fedora Linux x86-64 NVMe checkout of
  branch `agent/py7zip-overhaul-20261019`, then equal to `origin/main`
  `a06615f`) unless marked otherwise.

Summary counts: 7 non-empty artifacts (one anchored, six UNPROVEN), 6
empty placeholders (not distributed). Per `AGENTS.md`, no
platform-support claim may be made from this ledger alone.

## Non-empty artifacts

| Artifact | Size (bytes) | sha256 | Static format | Embedded banner (static `strings`) | Upstream version | Provenance | Introduced |
|---|---|---|---|---|---|---|---|
| `bin/lin/pc/x64/7za` | 2,837,048 | `12ef12519899ecda8ba59940d7f25a3f4818c97693538d49e894e6b783fb3081` | ELF x86-64, dynamically linked (`/lib64/ld-linux-x86-64.so.2`) | `7-Zip (z) 24.00 (x64) : Copyright (c) 1999-2024 Igor Pavlov : 2024-01-30` | 24.00 | **Anchored** — see row note A | `1fabd26` (2024-02-24) |
| `bin/lin/pc/x86/7za` | 3,139,200 | `ca0950c6d4b6e4ed2c7d0d1759b2beb68aecaf95ed31d9e5c1ae9faa914c37b9` | ELF i386, dynamically linked (`/lib/ld-linux.so.2`) | `7-Zip (z) 24.00 (x86) : Copyright (c) 1999-2024 Igor Pavlov : 2024-01-30` | 24.00 | UNPROVEN | `1fabd26` (2024-02-24) |
| `bin/lin/arm/x64/7za` | 2,428,216 | `271f123d64fb339f3011388005ff781958e4c17b9eb781e4d7a7b38712808a41` | ELF aarch64, dynamically linked (`/lib/ld-linux-aarch64.so.1`) | `7-Zip (z) 24.00 (arm64) : Copyright (c) 1999-2024 Igor Pavlov : 2024-01-30` | 24.00 | UNPROVEN | `1fabd26` (2024-02-24) |
| `bin/lin/arm/x32/7za` | 1,519,768 | `1414d731e764b969c22dae77d3948c6f0d1fca7b33eb7a16d016038e4e8ea753` | ELF ARM (EABI5, armhf), dynamically linked (`/lib/ld-linux-armhf.so.3`) | `7-Zip (z) 24.00 (armt) : Copyright (c) 1999-2024 Igor Pavlov : 2024-01-30` | 24.00 | UNPROVEN | `1fabd26` (2024-02-24) |
| `bin/win/pc/x64/7za.exe` | 1,314,816 | `827f88db392fbb679ca0dcf0818f32e74b59242061d0e6bc05bac9c672bbde51` | PE32+ console, x86-64 | `7-Zip (a) 24.01 (x64) : Copyright (c) 1999-2024 Igor Pavlov : 2024-01-31` | 24.01 | UNPROVEN | `1fabd26` (2024-02-24) |
| `bin/win/pc/x86/7za.exe` | 841,216 | `4721caf434de02b9aeb80b930702bbca75a1d54a5308c3445ec0db0778cfe693` | PE32 console, i386 | `7-Zip (a) 24.01 (x86) : Copyright (c) 1999-2024 Igor Pavlov : 2024-01-31` | 24.01 | UNPROVEN | `1fabd26` (2024-02-24) |
| `bin/mac/any/7za` | 5,792,768 | `c76d80526586c039e11d9d2ea8fe02324798c5082711178304b5060565859742` | Mach-O universal (x86_64 + arm64) | `7-Zip (z) 24.00 (x64)` and `7-Zip (z) 24.00 (arm64)`, both `: 2024-01-30` | 24.00 (both slices) | UNPROVEN — adjudicated by gate **OVH-29** (D-OVH-6) | `1fabd26` (2024-02-24) |

Row note A — the anchor for `bin/lin/pc/x64/7za`: the file is
byte-identical (sha256 above) to the official dynamic `7zz` inside
`7z2400-linux-x64.tar.xz`, recovered from the Wayback capture
(`web.archive.org/web/20240221221419/…`) of the official URL
`https://7-zip.org/a/7z2400-linux-x64.tar.xz` (pruned from the live
site today; upstream published no digest for 24.00-era assets). The
archived tarball's sha256 was computed during the 2026-10-11 probe as
`3bb85b8209a34e24e2938f0434fb0866e9a5750463478c82b977ca7ad49b90ff`
(trust-on-first-use caveat: the digest is ours, upstream published
none). The bundled file's digest was re-verified against this row on
2026-10-20; the archived tarball itself was not re-downloaded on that
date.

Row notes for the UNPROVEN rows:

- `bin/lin/pc/x86`, `bin/lin/arm/x64`, `bin/lin/arm/x32`: same-era
  official-format banners, no upstream anchor recorded. The 24.00-era
  archival procedure of the overhaul handoff (probe V19) has not been
  run for these rows; a Wayback availability re-check on 2026-10-20 was
  rate-limited (HTTP 429) and produced no new evidence.
- `bin/win/pc/x64`, `bin/win/pc/x86`: version evidence is 24.01, one
  patch after the other Linux/mac rows, and the banner brand is
  `7-Zip (a)` rather than the console builds' `7-Zip (z)`. Anchoring
  these requires the 24.01-era Windows distribution (installer or
  `-extra` package); that source decision is owned by gate OVH-07
  (D-OVH-2) and must not be preempted here.
- `bin/mac/any`: version-evidenced 24.00 in both slices; provenance
  UNPROVEN. No archived copy of the official 24.00 mac asset was
  located as of the 2026-10-11 probe (V19); the availability re-check
  belongs to gate OVH-29 at decision time.

## Placeholder slots (empty, not distributed)

All six files below are 0 bytes (sha256 of empty input
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`).
The artifact catalog (`py7zip/platforms.py`) intentionally carries no
entry for them; requests for these hosts resolve to a typed
`UnsupportedPlatformError`.

- `bin/win/arm/x32/7za`
- `bin/win/arm/x64/7za`
- `bin/mac/arm/x64/7za`
- `bin/mac/arm/x86/7za`
- `bin/mac/pc/x64/7za`
- `bin/mac/pc/x86/7za`

## Consistency checks

- `find bin -type f -size +0c | sort` (binaries only) yields exactly
  the seven artifacts tabled above — one ledger row each, re-verified
  2026-10-20.
- All seven digests and sizes above match
  `ArtifactCatalog._ARTIFACTS` (`py7zip/platforms.py`) exactly,
  re-verified 2026-10-20.
