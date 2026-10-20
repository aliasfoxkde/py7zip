# INFO
This directory contains the platform-specific 7-Zip binaries referenced by
the `py7zip` module. The authoritative per-file inventory — including size,
digest, and provenance state — is [`PROVENANCE.md`](PROVENANCE.md); this
file describes the layout convention only.

## Structure
- The directory tree for binaries follows this convention:
  - ./bin/{platform}/{type}/{architecture}/7za{extension}
  - platforms: `lin` | `mac` | `win`
  - types: `pc` | `arm`
  - architectures: `x64` | `x86` (pc), `x64` | `x32` (arm)
  - extension: `.exe` (windows) or empty (linux, mac)
- Examples (all present on disk today):
  - Windows: ./bin/win/pc/x64/7za.exe
  - Linux:   ./bin/lin/arm/x32/7za
  - Mac:     ./bin/mac/any/7za

## On-disk inventory

Non-empty (cataloged by `py7zip/platforms.py`; provenance in
[`PROVENANCE.md`](PROVENANCE.md)):
- bin/lin/pc/x64/7za
- bin/lin/pc/x86/7za
- bin/lin/arm/x64/7za
- bin/lin/arm/x32/7za
- bin/win/pc/x64/7za.exe
- bin/win/pc/x86/7za.exe
- bin/mac/any/7za

Empty placeholders (0 bytes, not cataloged, not distributed):
- bin/win/arm/x32/7za
- bin/win/arm/x64/7za
- bin/mac/arm/x64/7za
- bin/mac/arm/x86/7za
- bin/mac/pc/x64/7za
- bin/mac/pc/x86/7za
