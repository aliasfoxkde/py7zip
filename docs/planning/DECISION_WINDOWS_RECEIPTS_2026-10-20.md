# Decision record — Windows/WSL receipt audit (gate OVH-26 / audit D4)

- **Date:** 2026-10-20
- **Gate:** OVH-26 ("Windows/WSL receipt audit — does evidence exist for the
  README's tested claims?"), consuming audit decision **D4**.
- **Owner role:** Maint. **Recorded by:** the implementation agent executing
  the 2026-10-20 overhaul directive, which instructed gates that block work
  to be recorded exactly rather than bypassed. The gate's outcome rule is
  mandated by the plan itself ("if no receipt is found, the outcome is
  'uncheck claims', never 'assume support'", `docs/handoffs/2026-10-11-py7zip-overhaul.md`
  §6 OVH-26), so this record applies that rule to the evidence below; it
  invents no receipt and takes no acquisition-strategy decision. The
  maintainer may revise this record at any time (rollback: docs-only
  revert).
- **Receipt definition** (per `AGENTS.md` promotion rule): a recorded
  qualification naming the exact commit, Python version, OS/architecture,
  binary provenance, commands, and test result.

## Question

Do Windows x64 / WSL qualification receipts exist to back (a) the README
checklist's `[x] Windows x64 (64-bit)` row and (b) the 0.7.3 changelog
claim of testing "on Linux (Ubuntu through Windows Subsystem for Linux
(WSL))"?

## Searches run (2026-10-20)

| Command (abbreviated) | Outcome |
|---|---|
| `grep -rni "wsl\|windows" README.md docs/planning/PLATFORM_MATRIX.md docs/CHANGELOG.md .github/CHANGELOG.md` | Claims only, no receipts: `README.md:55` `[x] Windows x64 (64-bit)`; `docs/CHANGELOG.md:17` (0.7.3) WSL testing sentence; `docs/CHANGELOG.md:25` (0.6.2) "Tested 7za wrapper for Windows x64 platform"; `docs/planning/PLATFORM_MATRIX.md` host rows (Phase 0 historical, non-authoritative per overhaul handoff revision 4 — they record zero real-binary executions) |
| `git log --all --oneline --grep="windows\|wsl" -i` | One hit: `c86190a` (the overhaul handoff document commit itself; no receipt artifacts) |
| `gh search issues --repo aliasfoxkde/py7zip "windows receipt"` | No results |
| `gh search issues --repo aliasfoxkde/py7zip "WSL"` | One hit: issue #5, "Code In Repository Defers From Pip Package" — a bug report noting WSL reports `x86_64`; not a qualification receipt |
| GitHub issues/PR inventory, `GET /repos/aliasfoxkde/py7zip/issues?state=all` | No receipt or qualification artifacts in any issue or PR (open/closed) |
| Repository-wide file search | No receipts directory or qualification log exists anywhere under `docs/` or `.github/` |

## Findings

1. **No Windows x64 qualification receipt exists** in the repository,
   its issue/PR history, or any recorded artifact, as of 2026-10-20.
2. **No WSL qualification receipt exists** for the 0.7.3 changelog
   claim. `docs/CHANGELOG.md` is the historical release-note record for
   versions that were never published to PyPI (latest PyPI release is
   0.6.2, verified 2026-10-11); its sentences are claims, not receipts,
   and are left unrewritten as history.
3. `docs/planning/PLATFORM_MATRIX.md`'s Windows rows are Phase 0
   historical and record zero real-binary executions on any host; the
   overhaul handoff explicitly excludes that document's host rows from
   authority (revision 4, OVH-25 binding).

## Decision (applying the plan's mandated rule)

**No receipts found → the outcome is "uncheck claims."**

- The README row `[x] Windows x64 (64-bit)` is marked **to-uncheck**;
  OVH-04 executes this and may add no new checked row.
- The 0.7.3 WSL sentence and the 0.6.2 Windows-x64 sentence in
  `docs/CHANGELOG.md` are dispositioned as **unreceipted historical
  claims**: they are not rewritten (historical record), and they must
  not be repeated as support claims in any future release note
  (including the OVH-21 release notes and the §1 "Windows on the B0
  path" disclosure, which already requires the governed-fallback
  statement).
- Audit F1 resolves to the "false claim to retract" branch: the fix is
  documentation (OVH-04), executed in this tranche.

## Scope boundaries (what this record does NOT decide)

- **D-OVH-2 (OVH-07, Windows acquisition source) remains open.** This
  record decides nothing about how Windows binaries are acquired,
  bundled, or supported; the §1 governed fallback (checksum-pinned
  repo-hosted binaries, UNPROVEN provenance rows, no support claim)
  continues to apply until that gate is recorded.
- No macOS/Linux/other-platform row is affected by this record; other
  README rows are already unchecked.
- This record creates no platform-support claim and no deprecation
  window; it only reconciles claims to evidence.

## Consequences

- OVH-04 (platform-claim reconciliation) is unblocked and was executed
  against this record in the same tranche.
- A future maintainer receipt (per the `AGENTS.md` promotion rule) may
  re-check a row; that receipt supersedes this record via a docs-only
  commit.
