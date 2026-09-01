# py7zip platform and Python matrix

This document is the single place where py7zip states which host combinations
it claims, and what evidence stands behind each claim. It exists because the
project's own guidance forbids claiming platform support from source
inspection alone.

**Status of this document:** written during the Phase 0 baseline. Nothing in
it is a production-readiness claim.

## How to read the matrix

Every combination is placed in exactly one of three tiers.

| Tier | Meaning |
|------|---------|
| **Tested** | Executed on the named host during this qualification slice, with the command and result recorded below. |
| **Best effort** | The current classifier produces a code path for it, or the upstream binary layout suggests it should work, but nothing has been executed against a real 7za binary on that host. |
| **Not supported** | The current code refuses it, or no upstream artifact layout exists for it. Recorded so the refusal is documented rather than discovered. |

Best-effort entries are *not* support claims. They are the honest middle
ground between "we ran it" and "we know it fails".

## Python versions

| Version | Tier | Notes |
|---------|------|-------|
| 3.14 | **Tested** | CPython 3.14.6 on Fedora 44 x86-64. Full suite: 89 passed. |
| 3.9 – 3.13 | Best effort | `requires-python` admits them; the runtime uses no syntax newer than 3.7. Not executed in this slice. |
| 3.5 – 3.8 | Not supported | Advertised by the previous classifiers but untestable here and past end of life. Dropped in Phase 1. |
| PyPy / other implementations | Not supported | Never evaluated. |

## Operating system and architecture

The "classifier" column is what `Py7zip.__init__` actually does today, as
pinned by `tests/test_characterization_platform.py`. The "binary" column
records whether a real 7za artifact has been executed on that host.

| Host combination | Classifier today | Binary executed | Tier |
|------------------|------------------|-----------------|------|
| Linux x86-64 | `pc` / `x64` → `bin/lin/pc/x64/7za` | No | Best effort (packaging tested) |
| Linux armv7l 32-bit | `arm` / `x86` → `bin/lin/arm/x86/7za` | No | Best effort |
| Linux aarch64 | **refused** | No | Not supported |
| Linux i686 32-bit | **refused** | No | Not supported |
| Linux riscv64, ppc64le, s390x | **refused** | No | Not supported |
| Windows x86-64 | `pc` / `x64` → `bin/win/pc/x64/7za.exe` | No | Best effort |
| Windows arm64 | **refused** (machine string matched case-sensitively) | No | Not supported |
| Windows x86 32-bit | **refused** (`i386`/`i686` unmatched) | No | Not supported |
| macOS x86-64 | `pc` / `x64` → `bin/mac/pc/x64/7za` | No | Best effort |
| macOS arm64 | `arm` / `x64` → `bin/mac/arm/x64/7za` | No | Best effort |
| Any other operating system | **refused**, but as `KeyError` rather than the documented `NotImplementedError` | No | Not supported |

### Discrepancies this matrix records

These are findings from the Phase 0 characterization suite, not opinions:

1. **Linux aarch64 is refused by the current classifier.** `platform.machine()`
   returns `aarch64` there, and the test `elif 'arm' in platform.machine()`
   does not match, because `arm` is not a substring of `aarch64`. The
   repository nonetheless ships `bin/lin/arm/x64/7za`. This is a real gap
   between the shipped artifact set and the code that selects from it.
2. **Linux i686 and Windows x86 are refused** even though
   `bin/lin/pc/x86/7za` and `bin/win/pc/x86/7za.exe` are shipped. The
   classifier keys on `platform.architecture()[0]`, and no branch maps those
   machines onto the `pc` type.
3. **Windows arm64 is refused** because the comparison against the machine
   string is case-sensitive and Windows reports `ARM64`.
4. **An unsupported operating system raises `KeyError`**, not the
   `NotImplementedError` that `get_binary_url` documents, because the
   `sys_platform` dictionary lookup happens first in `__init__`.

## Evidence record for this slice

Recorded per the repository promotion rule. This is the complete set of
commands used to qualify the Phase 0 and Phase 1 work.

| Field | Value |
|-------|-------|
| Branch | `feat/py7zip-production-revamp` |
| Base commit | `2214a077a5ea1a99778e8148c27951158bcb0fe7` |
| Host OS | Fedora Linux 44 (Workstation Edition), kernel `7.1.8-200.fc44.x86_64` |
| Architecture | `x86_64`, `platform.architecture()` == `('64bit', 'ELF')` |
| Python | CPython 3.14.6 |
| Test command | `python3 -m pytest tests/ -p no:cacheprovider -q` |
| Offline isolation | `unshare -rn python3 -m pytest tests/ -p no:cacheprovider -q` (no network namespace) |
| Result | 89 passed, 0 failed, 0 skipped |
| Build command | `python3 -m build --outdir <tmp>` with `PIP_NO_INDEX=1` and `PIP_FIND_LINKS` pointing at a local wheelhouse |
| Binary provenance | None. No 7-Zip binary was downloaded or executed during this slice. |

**Consequently, the following is still unproven:** that any 7za binary
launches and produces correct archive results on any platform; that the
downloads pointed at by the current URLs return the artifacts they claim;
and that any platform other than the one row above marked "packaging tested"
can install the wheel. Those are Phase 2 through Phase 4 exit criteria and
remain open.
