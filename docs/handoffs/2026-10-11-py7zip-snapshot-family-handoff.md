# py7zip snapshot-family handoff — 2026-10-11

**Scope:** the public no-op methods `Py7zip.full`, `Py7zip.incremental`,
`Py7zip.differential`, `Py7zip.snapshot` (the "snapshot family") — current
behavior, what the repository actually records about their intent, the
defect/legacy classification, compatibility and security implications, the
open decision gates, and the phased path to a resolved contract.

**Evidence boundary and required execution base.** The original audit
observations (W1–W13, §11) were taken on branch
`codex/py7zip-mypy-hardening-20261011`, HEAD `7f4f381` (= `origin/main`
`f6e9a1a` + one mypy-hardening commit; local `main` is stale at `a7b396c`),
working tree clean at audit start. The **required execution base for every
phase below is this branch, `docs/py7zip-snapshot-family-handoff-20261012`,
at HEAD `b134d91` or a descendant**: `b134d91` sits directly on
`origin/main` `f6e9a1a` (`f6e9a1a..b134d91` contains only this handoff
document — docs-only), so its code content equals `f6e9a1a`; the `7f4f381`
mypy-hardening commit is **not** part of this base and must not be rebased
onto it. Because that commit shifts `py7zip/py7zip.py` line numbers, all
`py7zip/py7zip.py` anchors in this revision are stated for the execution
base (family methods `224–235`, `snapshot` docstring `234`, `wrapper`
diagnostics `178–202`), not the `7f4f381` numbering. The divergent audit
line was read from local tags `v0.8.0` (`3252d39`, 2026-09-29) and `v0.9.0`
(`5a60a7c2`, 2026-10-03); its branch tip is `7822d95`. Topology:
`origin/main...audit/py7zip-qualification-20260909` is **6 behind / 22
ahead** at merge-base `4713a75` (each side has commits the other lacks), and
`v0.9.0` is **not** an ancestor of HEAD. All citations are to files in this
worktree at the execution base unless prefixed with a ref (e.g. `v0.9.0:`).

**Status:** docs-only handoff. **No source file was changed and no test was
weakened, deleted, or edited.** Nothing in this document authorizes a code
change; every code-touching step below is bound to an already-recorded plan
task and its decision gate.

---

## 1. Verdict: deliberate placeholders that are now a user-facing defect

Both classifications are true, at different points in the timeline. Stated
precisely with citations:

**Deliberate at introduction (2024).** The four methods were committed as
explicit one-line `pass` stubs in `767cb4d` (2024-02-24, "Improved Pipeline
and Workflow, see CHANGELOG v0.5.0"; the commit is an ancestor of HEAD), and
the 0.6.2 changelog entry records the intent sentence:
"Put in various placeholders for future logic." (`docs/CHANGELOG.md:28`).
They have never been wired to any execution path on the main line: the
pickaxe search `git log --all -S "def snapshot" -- py7zip/py7zip.py` fires
only at `767cb4d` — the methods were introduced once and never restructured
into working code on this line.

**User-facing defect today.** Three independent repo surfaces establish the
defect, not the deliberateness:

1. **The wrapper's own reference docs advertise them as working features.**
   `docs/FEATURES.md:5–6` claims "Simplified 'point-in-time' backups and
   full/incremental schemas using snapshots" and "Simplifies lessor known
   features of 7zip. Such as full, differential, incremental backups, etc."
   The repository's own audit flags exactly this contradiction as finding
   **F6** (Medium, docs): "`docs/FEATURES.md:3–4` advertises
   snapshot/incremental features that are stubs"
   (`docs/handoffs/PLATFORM_ARCHITECTURE_PY7ZIP_2026-10-10.md:156`).
2. **They ship no-op in the release users actually install.** PyPI's latest
   published release is 0.6.2 (2024-02-25) — verified 2026-10-11 against the
   official PyPI JSON API, <https://pypi.org/pypi/py7zip/json> (the release
   keys end at `0.6.2`) — and its sdist defines all five methods as silent
   no-ops: evidence item **V20** in the overhaul handoff
   (`docs/handoffs/2026-10-11-py7zip-overhaul.md:180`). A caller on the
   PyPI release gets `None` and no archive.
3. **The repo's own compatibility policy classifies them for removal and
   mislabels them as unadvertised.** `docs/planning/COMPATIBILITY.md:44–49`
   says the family is "**not** advertised features … removed in Phase 4",
   and the migration map (`:84`) says "Stop calling them. They have never
   done anything." The "not advertised" half is factually wrong against
   `docs/FEATURES.md:5–6` (that is F6 again); the "never done anything" half
   is true on this line.

The failure mode is the harmful part: **silent success**. `wrapper` on a real
failure at least prints diagnostics under `verbose`/`debug`
(`py7zip/py7zip.py:178–202`); the snapshot family prints nothing, raises
nothing, spawns nothing, and returns `None`. For a method whose docstring
says "Streamlines the process for creating a snapshot"
(`py7zip/py7zip.py:234`) and whose sibling docs promise backup schemas, a
caller who believes the call ran has no archive and no error. On a backup
API, a false success is a data-protection hazard, not a cosmetic gap.

**The "deliberate legacy, leave it alone" framing is supported by no repo
surface.** No document describes the no-ops as intended final behavior. The
only forward-looking statements about the family are the removal plans
already cited above and in §3.1–§3.2 (audit P1.2; overhaul OVH-14) or the
competing implemented contract on the divergent audit line (§3.3). "Decide
whether … implement them or remove them from the public surface" is recorded
as *open work* in `docs/planning/HANDOFF.md:39–40`, and the deciding records
still do not exist (§6).

## 2. Current behavior (verified at execution base `b134d91`, code identical to `f6e9a1a`)

- `py7zip/py7zip.py:224–235` — all four methods share the signature
  `(self, src, dst, options="")` and their bodies are a bare `return`.
  Only `snapshot` carries a docstring (`:234`); the other three have none.
- The no-op is **unconditional across both runtimes**: the methods never
  consult `self.legacy`, `self._safe`, or any attribute. Identical behavior
  on the safe (default) and legacy runtimes.
- No argument is validated, no result type exists for them, and `options`
  is accepted and discarded — on the safe runtime the same `options` value
  would raise `TypeError` if passed to `compress`/`decompress`
  (pinned by `tests/test_default_api.py:26–30`), so the family silently
  accepts values the rest of the safe API rejects.
- Characterization pins (load-bearing; do not weaken or delete outside the
  same-commit rule, `docs/planning/COMPATIBILITY.md:95–97`):
  - `tests/test_characterization_wrapper.py:300–308`
    (`test_snapshot_family_methods_do_nothing`, parametrized over all four
    names): asserts the return is `None` **and** the recorded subprocess
    command list is empty (`runner.commands == []`) — no process is spawned.
  - `tests/test_characterization_wrapper.py:311–321`
    (`test_snapshot_family_methods_accept_the_shared_signature`): pins the
    parameter list to exactly `["self", "src", "dst", "options"]`.
- Test environment facts that constrain any change: the suite runs offline
  with socket denial (`tests/conftest.py:43–52`), with
  `filterwarnings = ["error"]` (`pyproject.toml:45`) — an unasserted
  `DeprecationWarning` fails the suite by design — and `make_wrapper`
  constructs the **legacy** runtime (`tests/conftest.py:118`), which is why
  the family pins sit in the legacy characterization file even though the
  no-op is runtime-independent.

## 3. Verified intended contract — what the repo actually says

There is **no single verified intended contract**. The repository carries
four mutually inconsistent statements plus a divergent implementation. This
section is the complete register; §6 defines the gates that resolve it.

### 3.1 The four in-repo statements

| Surface | Claim | Citation |
|---|---|---|
| `docs/FEATURES.md` | The family is a feature ("point-in-time backups", "full, differential, incremental backups") | `docs/FEATURES.md:5–6` |
| `docs/CHANGELOG.md` | Deliberate placeholders for future logic (0.6.2) | `docs/CHANGELOG.md:28` |
| `docs/planning/COMPATIBILITY.md` | Not advertised features; removed in Phase 4; "they have never done anything" | `docs/planning/COMPATIBILITY.md:44–49, 84` |
| `docs/PLANNING.md` | Task "Add simplified functions for … (full, incremental, differential, snapshot)" still open; annotated 2026-10-10 "handoff P1.2 decides remove-vs-implement" | `docs/PLANNING.md:13–14` |

`docs/planning/HANDOFF.md` states the decision is open in so many words:
"several unfinished snapshot/incremental APIs; these are not
release-qualified features" (`:19–20`) and "Decide whether `full`,
`incremental`, `differential`, and `snapshot` are supported features;
implement them or remove them from the public surface" (`:39–40`).

### 3.2 The recorded main-line plan (current authority, unexecuted)

The 2026-10-11 overhaul handoff (revision 4) is the current execution plan
and commits the main line to **deprecate, then remove**:

- **OVH-14** (`2026-10-11-py7zip-overhaul.md:383` ledger, `:621–655` spec):
  two commits — commit 1 adds `DeprecationWarning`s to the four methods and
  `cd`, quoting verbatim the removal version recorded by gate OVH-30, and
  updates the characterization pins to `pytest.warns` **without deleting or
  weakening them** (cites COMPATIBILITY rule 3); commit 2 (next feature
  release, only after the deprecating release is verifiably on PyPI) deletes
  the methods and pins absence.
- Grounding for the deprecation sequence: V20 (§1, item 2, with the PyPI
  source and observation date) — the PyPI 0.6.2 sdist ships all five
  methods, so direct removal would convert today's silent success into an
  `AttributeError` on upgrade with no warning ever shown (rationale at
  `:626–633`).
- **OVH-30** (gate; `:399` ledger, `:858–874` spec) = decision **D-OVH-7**
  (`:938–939`): the removal version and window. **No removal version is
  recorded yet** (§6, DG-1); OVH-14 commit 1 is blocked without it
  (`:872–873`).
- Revision 4 also records that COMPATIBILITY.md's family row ("removed in
  Phase 4 with no window") must be harmonized onto this sequence in the
  OVH-14 commit (`:640–643`).
- The platform-architecture audit's P1.2
  (`PLATFORM_ARCHITECTURE_PY7ZIP_2026-10-10.md:270–279`) says the same thing
  in its older vocabulary ("remove the four stubs"), under an explicit
  recorded exception to `AGENTS.md`'s "preserve the public API"
  non-negotiable (`:33–43`), and grades the family as **F5** (Medium, API
  debt, `:155`).

### 3.3 The competing contract: implemented and published on the audit line

This is the fact the main-line plan does not account for. The divergent
branch `audit/py7zip-qualification-20260909` (tip `7822d95`; 22 commits
ahead of / 6 behind `origin/main`, merge-base `4713a75` — see the evidence
boundary; `v0.9.0` not an ancestor of HEAD) **implemented the family**, and
the implementation is published:

- Implementation commit `1bb3ea3` (2026-09-29, "test: full branch coverage
  and strict lint clean") introduced the e2e suite
  `tests/test_e2e_bundled.py::TestBackupModes` (pickaxe over
  `TestBackupModes`).
- Tag **v0.8.0** (`3252d39`, 2026-09-29) already carries the full
  implementation; **v0.9.0** (`5a60a7c2`, 2026-10-03) additionally carries a
  real `differential` bug fix (`13fe83e`: a stale diff archive is replaced
  on re-run — recorded in
  `docs/planning/QUALIFICATION_PLAN_2026-09-29.md:49–61`).
- Both tags are published, non-draft GitHub Releases **with installable
  wheel + sdist assets** (overhaul handoff V15, `:175`; occupied-version
  register at `:723–730`). They were never published to PyPI.
- The branch's own qualification receipt:
  `docs/planning/QUALIFICATION_PLAN_2026-09-29.md:13` — "Backup family |
  `full` / `incremental` / `differential` / `snapshot` implemented, no
  longer stubs | e2e `tests/test_e2e_bundled.py::TestBackupModes`; argv pins
  in `tests/test_safe_unit.py`" (verified in local git at tag `v0.9.0`).

So there are **three live behaviors for the same four method names**:

| Population | Where the code comes from | Family behavior |
|---|---|---|
| `pip install py7zip` users | PyPI 0.6.2 (2024-02-25; §1, item 2) | silent no-op (V20) |
| Direct-from-GitHub asset installs | Releases v0.8.0 / v0.9.0 assets | implemented, extended signatures (§12) |
| This line / future main-line release | `main` + hardening branches | silent no-op, removal planned (OVH-14) |

Which population a decision optimizes for is exactly what the un-taken
integration decision (§6, DG-2) governs.

### 3.4 Bottom line on intent

The repository's own recorded state is: *intent decided only as "not
release-qualified"; disposition (implement vs remove) explicitly deferred to
a decision that has not been taken* (§3.1, last two rows of the register).
The main-line plan (OVH-14) presumes removal; the
audit line shipped an implementation. Until gates DG-1/DG-2 (§6) are
recorded, **removal is the planned-but-ungated direction, not a verified
final contract, and the implemented variant is a published alternative, not
a superseding decision.** This handoff does not resolve that fork; it
equips the maintainer to.

## 4. Compatibility implications

1. **Upgrade path 0.6.2 → removal without deprecation breaks callers.**
   Every pip user is on 0.6.2, which ships the methods (V20). Direct removal
   converts silent success into `AttributeError`. This is the recorded
   reason OVH-14 is a two-commit, warning-first sequence
   (`2026-10-11-py7zip-overhaul.md:626–633`).
2. **The deprecation must be assertable.** `filterwarnings = ["error"]`
   (`pyproject.toml:45`, §2) means the moment commit 1 lands, every existing
   characterization test that *calls* the family (the no-op pin, §8) fails
   unless updated in the same commit to `pytest.warns` — exactly what OVH-14
   specifies (`:634–639`). The pins are updated to the new documented
   contract, never deleted or weakened (COMPATIBILITY rule 3, `:95–97`).
3. **Signature divergence already exists in the wild.** The audit line
   extended the pinned signature: `differential(…, *, diff_path=None)` and
   `snapshot(…, *, timestamp=None)` (`v0.9.0:py7zip/py7zip.py:269, 279`).
   Code written against v0.9.0 assets that passes those keyword arguments
   fails with `TypeError` against any main-line build — and against the
   pin `tests/test_characterization_wrapper.py:311–321`. Adoption (not
   removal) therefore requires updating that pin in the same commit.
4. **Behavioral deltas are not limited to signatures.** The implemented
   family prepends `-y` (unattended overwrite), `differential` **deletes a
   pre-existing** `<base>.diff.7z` before writing, `snapshot` derives a
   timestamped destination path instead of using `dst` verbatim, and
   `incremental`/`differential` require a new `"update"` operation that this
   line's `ArchiveRunner.run` rejects (`py7zip/safe.py:58–59` vs
   `v0.9.0:py7zip/safe.py:87–88`). Callers migrating between channels get
   different filesystem side effects from identical calls (§12).
5. **Removal scope discipline.** The audit's recorded exception permits
   removing exactly the four stubs plus `cd` — no other public surface
   (`PLATFORM_ARCHITECTURE_PY7ZIP_2026-10-10.md:37–43`); `AGENTS.md`
   otherwise requires preserving the public `Py7zip` API (`AGENTS.md:5–8`).
6. **Documentation is the only immediately user-facing surface — and PyPI
   visitors are one click away from it.** Until the gates resolve,
   `docs/FEATURES.md:5–6` keeps advertising non-existent functionality to
   every reader of the repo. The PyPI exposure is by link, not by syndicated
   content: `README.md:36` links `docs/FEATURES.md`, and `README.md` is the
   PyPI long description (`pyproject.toml:9`,
   `readme = {file = "README.md", …}`); the linked file is not rendered as
   long-description content, so the false claims do not appear on the
   package's PyPI page itself — a prospective `pip install py7zip` visitor
   can click the documentation link and land on them. Correcting
   `docs/FEATURES.md` therefore fixes the link target; the rendered text of
   the already-published 0.6.2 PyPI page changes only with a future release
   (no release is authorized by this handoff). Fixing the advertising does
   not prejudge implement-vs-remove and is already scoped as OVH-03
   ("Docs truth-pass … `docs/FEATURES` stub labeling",
   `2026-10-11-py7zip-overhaul.md:372, 464–466`).

## 5. Security implications

- **The no-ops are not an injection surface.** They spawn no process and
  never reach `wrapper`'s `shell=True` legacy path, so caller-supplied
  `options` in these methods is inert. (The injection hazard the suite
  characterizes lives in the legacy `wrapper`, pinned at
  `tests/test_characterization_wrapper.py:203–227` — out of scope here.)
- **Silent acceptance of rejected inputs.** The family accepts `options`
  strings the safe runtime rejects by design (§2; the alias pin in §8),
  masking caller bugs at the boundary where type strictness was introduced.
- **False-success on backup semantics is the substantive security-adjacent
  risk.** A caller integrating the wrapper for data protection gets no
  signal that no backup was made (§1). This is why this handoff treats the
  advertising (`docs/FEATURES.md:5–6`) as a defect to correct now rather
  than a cosmetic doc lag.
- **Adoption path carries new attack surface.** If the implemented variant
  is adopted, `incremental`/`differential` route through the `-u` update
  switch with a `!`-switch-derived archive path
  (`v0.9.0:py7zip/safe.py:310–317`); the differential path deletes a
  derived file and constructs switch syntax from a caller-controlled
  destination name. Porting must reuse the existing argv/NUL guards
  (`py7zip/safe.py:60–78`) and add traversal/overwrite tests before any
  support claim (per `AGENTS.md:24–26`, no claim without a receipt).

## 6. Decision gates (intent is genuinely unspecified until these are recorded)

Two decision records already exist as ledger gates in the current plan; a
third rule (their interaction) is not written anywhere and is recorded here.

- **DG-1 — removal version and window** (= ledger gate **OVH-30**, decision
  **D-OVH-7**; `2026-10-11-py7zip-overhaul.md:858–874, 938–939`). Owner:
  Maint. Deliverable: a decision record in `docs/planning/` naming the
  version the `DeprecationWarning`s announce and the window after which
  OVH-14 commit 2 may merge (strictly later than the deprecating release,
  which must be verifiably on PyPI first). State: **not recorded** — no
  removal version is recorded anywhere under `docs/planning/` (the
  directory does name other versions, e.g. the `py7zip-0.7.3` packaging
  baseline at `docs/planning/HANDOFF.md:27`, but none is a removal
  version); OVH-14 commit 1 is blocked without it (`:872–873`).
- **DG-2 — audit-line integration strategy** (= **OVH-06**, decision
  **D-OVH-1**; `:375, 490–499`). Owner: Maint. Deliverable: decision record
  choosing (a) merge the audit line, (b) cherry-pick slices (CLI, receipts),
  or (c) leave diverged and re-implement. State: **not recorded**. This
  gate determines whether the *implemented* family (§3.3) becomes the
  main-line contract.
- **DG-3 — interaction rule (recorded by this handoff; not in any prior
  doc).** OVH-14's text presumes removal and never mentions that a
  published implementation exists on the audit line (§3.3); conversely
  nothing in OVH-06 revises OVH-14 if the audit line is merged. The rule:
  **neither gate preempts the other; the family's disposition must be
  re-stated in the surviving record after both are taken.** Concretely:
  if DG-2 selects (a) merge or (b) cherry-pick that includes the backup
  family, then OVH-14's scope shrinks to `cd`-only, the characterization
  signature pin (`tests/test_characterization_wrapper.py:311–321`) is
  updated to the adopted signatures in the same commit, and
  `docs/planning/COMPATIBILITY.md:44–49, 84` plus `docs/FEATURES.md:5–6`
  are rewritten to describe the implemented contract instead of removal;
  if DG-2 selects (c), DG-1 proceeds as written. Until both records exist,
  the only authorized family work is Phase A (§7).

## 7. Phased actionable tasks

Execution order is Phase A → B → (C | C′) → D. Phase A needs no gate and
changes no code. Phases C/C′ are already-specified plan tasks; they are
listed here bound to their gates, not re-specified. **This handoff executes
none of them** — it is docs-only. ("Uncommitted by instruction" described
authoring time only; the handoff has since been committed on this branch —
see §11. That changes the filing, not the force: nothing below is executed
by this document.)

### Phase A — stop the false advertising (docs-only; no gate; maps to OVH-03)

- **A1.** Edit `docs/FEATURES.md:5–6`: either delete the two claims or mark
  them explicitly as not implemented in any released build, e.g. "planned;
  not implemented in 0.6.x (no-op) — see COMPATIBILITY.md". Do not claim a
  removal version (DG-1 unrecorded) and do not claim the audit-line
  behavior as current (DG-2 unrecorded).
- **A2.** Same commit: confirm `docs/PLANNING.md:13–14` annotation still
  matches reality (it does at HEAD) and leave `docs/USAGE.md` untouched —
  it never documents the family (`docs/USAGE.md:1–16` covers only
  compress/decompress).
- Acceptance (falsifiable):
  1. `git diff --stat` names docs files only (expected: just
     `docs/FEATURES.md`; A2 requires no edit at HEAD).
  2. The two claims at `docs/FEATURES.md:5–6` no longer appear:
     `grep -nF "point-in-time" docs/FEATURES.md` and
     `grep -nF "Simplifies lessor known features" docs/FEATURES.md` both
     return empty.
  3. **No assertion that the family works remains:**
     `grep -nEi "full|incremental|differential|snapshot" docs/FEATURES.md
     | grep -viE "not implemented|planned|no-op"` returns empty — every
     line still naming the family carries an explicit not-implemented
     qualifier.
- Rollback: revert the single docs commit. Risk: none at runtime.

### Phase B — record the decisions (gates; Maint)

- **B1.** Record DG-1 (OVH-30/D-OVH-7): removal version + window, per the
  OVH-30 spec (`2026-10-11-py7zip-overhaul.md:858–874`). Evidence to weigh
  is already assembled there (PyPI population on 0.6.2; window must span a
  published deprecation-carrying release).
- **B2.** Record DG-2 (OVH-06/D-OVH-1): integration strategy, with the
  conflict inventory OVH-06 specifies (`:490–499`) **extended with the
  family dimension**: the merge/cherry-pick options carry the implemented
  family (§3.3) and therefore collide with OVH-14 as written.
- **B3.** Write the DG-3 interaction rule (§6) into whichever record lands
  second, and add a one-line cross-reference to the first.
- Acceptance (falsifiable): `grep -rln "D-OVH-7" docs/planning/` returns
  the DG-1 record, which names a removal version and window;
  `grep -rln "D-OVH-1" docs/planning/` returns the DG-2 record, which names
  exactly one of merge / cherry-pick / leave-diverged; OVH-14's blocking
  condition is discharged only by B1.

### Phase C — removal path (only if DG-2 outcome (c), or DG-2 deferred and DG-1 taken)

Execute **OVH-14 exactly as specified** — the two-commit deprecate-then-
remove sequence already specified in §3.2
(`2026-10-11-py7zip-overhaul.md:621–655`, with commit 1 quoting the DG-1
version verbatim and only after the deprecating release is verifiably on
PyPI). Success criteria and acceptance commands are OVH-14's (`:650–655`);
§8 lists the test deltas. **No deviation is authorized by this handoff.**

### Phase C′ — adoption path (only if DG-2 outcome (a) or (b) includes the family)

Not specified by any prior task; requires a new recorded task before code
(reuse the OVH ledger convention). Minimum shape, derived from §3.3/§12:

- **C′1.** Extend `ArchiveRunner.run` operation set with `"update"`
  (mirror `v0.9.0:py7zip/safe.py:87–88, 103–…`), keeping the existing
  guards (`py7zip/safe.py:60–78`).
- **C′2.** Port `SafePy7zip.full/incremental/differential/snapshot` +
  `snapshot_name`/`differential_name` and the `Py7zip` delegating methods
  (including `diff_path`/`timestamp` kwargs) from `v0.9.0`.
- **C′3.** Update the signature pin
  (`tests/test_characterization_wrapper.py:311–321`) and the no-op pins
  (`:300–308`) to the adopted contract **in the same commit** (rule 3).
  **Test design — one choice, fixing an ambiguity in earlier revisions:**
  the audit line's `TestBackupModes` is **not** ported as a host-gated
  real-binary e2e lane. That suite (v0.9.0
  `tests/test_e2e_bundled.py::TestBackupModes`, introduced by `1bb3ea3`)
  runs the real `7za` checked into `bin/` and is gated on the bundled
  artifact for the detected platform — a design this line's offline suite
  (socket denial via `tests/conftest.py:43–52`; `filterwarnings =
  ["error"]`) does not carry. Port its behavioral assertions as **argv pins
  against the fake seam** (`tests/fakes.py`, `FakeSubprocess`), per §8
  (adoption cases 2–7), including the differential re-run pin from
  `13fe83e` as a two-call fake-seam pin. Do not check a real binary into
  `bin/` and do not add a host-gated lane in this phase; that would be a
  separate, unrecorded task.
- **C′4.** Rewrite `docs/FEATURES.md`, `docs/planning/COMPATIBILITY.md`
  family rows to the implemented contract; revise OVH-14 to `cd`-only
  (DG-3).
- Acceptance: full offline suite green with the updated pins; the ported
  backup-mode coverage (§8, adoption cases 2–7) runs entirely through the
  fake seam offline — falsifiably: no `tests/test_e2e_bundled.py` is added,
  `git status --short -- bin/` shows no new binary (only new additions are
  barred; existing tracked `7za` artifacts stay as-is), and every new
  backup-mode test goes through `FakeSubprocess`; no support claim without
  a receipt (`AGENTS.md:24–26`).

### Phase D — release and verification

The family disposition ships only with the release train already planned
(OVH-21 and its gates; `2026-10-11-py7zip-overhaul.md:705–762`). Release
notes must carry the migration callout (removal path) or the behavioral-
delta table (adoption path: `-y` prepend, diff replacement, timestamped
destination, update-op semantics — §12). Receipts per `AGENTS.md:24–26`.

## 8. Test cases

Existing pins that are load-bearing until the contract changes — all green
at HEAD and protected:

| Test | Pins | Location |
|---|---|---|
| `test_snapshot_family_methods_do_nothing` (×4) | returns `None`; `runner.commands == []` (no subprocess) | `tests/test_characterization_wrapper.py:300–308` |
| `test_snapshot_family_methods_accept_the_shared_signature` (×4) | parameter list exactly `["self","src","dst","options"]` | `tests/test_characterization_wrapper.py:311–321` |
| `test_default_aliases_require_individual_option_arguments` | safe-path `TypeError` on string options (the family violates-by-omission) | `tests/test_default_api.py:26–30` |

Phase-specific cases to add (offline; fake seam per `tests/conftest.py`,
`tests/fakes.py`):

- **Deprecation (Phase C commit 1):** parametrized
  `pytest.warns(DeprecationWarning, match="<DG-1 version>")` around each
  family call; unchanged assertions that result is `None` and
  `runner.commands == []`; `filterwarnings = ["error"]` (§2) guarantees an
  unasserted warning fails the suite.
- **Removal (Phase C commit 2):** replace the pins with absence —
  `all(not hasattr(Py7zip, m) for m in ("full","incremental","differential","snapshot"))`,
  mirroring OVH-14's acceptance one-liner
  (`2026-10-11-py7zip-overhaul.md:653–655`).
- **Adoption (Phase C′)** — design fixed to one choice: **fake-seam argv
  pins** (`FakeSubprocess`); the v0.9.0 `TestBackupModes` host-gated
  real-binary e2e (checked-in `bin/` artifact) is not ported as such
  (§7, C′3):
  1. signature pin updated to the adopted parameters (kwarg-only
     `diff_path`/`timestamp`);
  2. `full` argv = `[binary, "a", dst, src, "-y", *options]`;
  3. `incremental` argv uses the `update` operation and `-y`;
  4. `differential` deletes a pre-existing `<base>.diff.7z` first, rejects
     non-`.7z` diff paths with `ValueError`, and re-run replaces the stale
     diff (the `13fe83e` regression pin);
  5. `snapshot(timestamp=...)` is deterministic offline; without it the
     stamp is derived, never network-dependent;
  6. legacy-mode family calls resolve via PATH exactly like the audit
     line's `_backup_executor` (`v0.9.0:py7zip/py7zip.py:236–253`) or are
     refused with a typed error — pick one and pin it;
  7. NUL-byte / non-sequence options guards apply to the new operations
     (extend the existing matrix at `py7zip/safe.py:60–78`).
- **Docs (Phase A, optional):** a grep-style guard test or docs-lint step
  asserting `docs/FEATURES.md` contains no unimplemented-feature claim;
  keep it lightweight (string assertions, not a new framework).

## 9. Success criteria

- **Phase A:** the falsifiable Phase A checks hold — no line of
  `docs/FEATURES.md` names the family without a not-implemented/planned
  qualifier (the §7 Phase A grep guard returns empty), the two `:5–6`
  claims are gone, the diff touches docs only; characterization suite
  untouched and green.
- **Phase B:** DG-1 and DG-2 records exist under `docs/planning/`; the DG-3
  interaction rule is present in at least one of them; OVH-14's blocking
  condition references the actual record.
- **Phase C:** OVH-14 acceptance commands pass verbatim
  (`2026-10-11-py7zip-overhaul.md:650–655`); the characterization pins
  exist and assert the warning (commit 1) and the absence (commit 2); no
  pin was deleted or weakened outside the same-commit rule.
- **Phase C′:** full offline suite green with the adopted contract pinned;
  backup-mode coverage exists as offline fake-seam argv pins per §8
  (adoption cases 2–7) — falsifiably, no new host-gated real-binary e2e
  lane is added and no new checked-in `bin/` binary is added; existing
  tracked `7za` artifacts remain unchanged. COMPATIBILITY and FEATURES
  describe the implemented behavior; OVH-14 revised to
  `cd`-only.
- **Phase D:** the shipped release's notes contain the family callout
  (migration or deltas), and every support claim about backup modes has a
  receipt per `AGENTS.md:24–26`.

## 10. Non-goals

- No change to `Py7zip.wrapper`, the aliases, the legacy runtime, or the
  safe runtime's existing operations in this handoff.
- No weakening, deletion, or "temporary skip" of any characterization test;
  pins move only in the same commit as the documented contract change
  (COMPATIBILITY rule 3).
- No implementation of the family on the main line as a default outcome —
  that is DG-2's call, not this document's.
- No release, tag, or PyPI action; occupied versions
  (`v0.8.0`/`v0.9.0` assets and tags) remain untouchable per
  `2026-10-11-py7zip-overhaul.md:107–111, 964–967`.
- No platform-support claim about backup modes on any OS
  (`AGENTS.md:24–26`).
- No resolution of the legacy-runtime sunset (OVH-27/D1) or the options
  bridge (OVH-16/D5) — cited only where they interact.

## 11. Verification log (what was actually run for this handoff)

| # | Command (abbreviated) | Outcome |
|---|---|---|
| W1 | `git status`, `git log --oneline -5`, `git rev-parse main` | clean tree at `7f4f381`; branch = `origin/main` (`f6e9a1a`) + mypy commit; local `main` stale at `a7b396c` |
| W2 | Read `py7zip/py7zip.py`, `py7zip/safe.py`, `tests/test_characterization_wrapper.py`, `tests/conftest.py`, `tests/fakes.py`, `tests/test_default_api.py`, `pyproject.toml` | current behavior §2 confirmed; pins confirmed at `:300–321` |
| W3 | `git log --all -S "def snapshot" -- py7zip/py7zip.py` | single hit `767cb4d` (2024-02-24) — stubs introduced once, never restructured on this line |
| W4 | `git show 767cb4d:py7zip/py7zip.py` | one-line `pass` stubs for all four methods; `git merge-base --is-ancestor 767cb4d HEAD` → true |
| W5 | `git show 9ae26e5:py7zip/py7zip.py` (v0.3.0) | only `extract`/`backup` — family absent before v0.5.0 |
| W6 | `git grep -n` for the four method defs at `5a60a7c2` | implemented family + `SafePy7zip` bodies at v0.9.0 (§3.3, §12) |
| W7 | `git log audit/py7zip-qualification-20260909 -S "TestBackupModes" -- tests/` | implementation commit `1bb3ea3` (2026-09-29); `git cat-file -t 1bb3ea3` → commit |
| W8 | `git show 3252d39:py7zip/py7zip.py` (v0.8.0) | family already implemented at 0.8.0 |
| W9 | `git merge-base --is-ancestor 5a60a7c2 HEAD` → false; `git rev-parse audit/py7zip-qualification-20260909` → `7822d95`; `git rev-list --left-right --count origin/main...audit/…` → `6 22`; `git merge-base origin/main audit/…` → `4713a75` | audit line divergent (22 ahead / 6 behind at merge-base `4713a75`); published tags not in main line |
| W10 | `git show 5a60a7c2:docs/planning/QUALIFICATION_PLAN_2026-09-29.md` | "Backup family … implemented, no longer stubs" receipt at line 13; file reachable in local git at the tag (working copy also on the `audit/py7zip-qualification-20260909` worktree) |
| W11 | `git log --all --oneline -- "*QUALIFICATION*"` | plan file's commits (`3252d39`, `2e8c3df`, `5a60a7c`, `d6a6c5d`) are on the audit line only |
| W12 | Grep sweeps over `docs/` (`FEATURES`, `CHANGELOG`, `PLANNING`, `planning/HANDOFF`, `planning/COMPATIBILITY`, both handoffs) | every claim in §1–§3 cited with file:line |
| W13 | PyPI JSON API, `GET https://pypi.org/pypi/py7zip/json` (observed 2026-10-11) | latest version `0.6.2`; release keys end at `0.6.2` (§1, item 2) |
| W14 | `git rev-parse HEAD`; `git diff --stat f6e9a1a..HEAD`; re-read `py7zip/py7zip.py` at HEAD (observed 2026-10-12) | HEAD `b134d91` = `f6e9a1a` + docs-only handoff commits (`7f4f381` not in this history); code identical to `f6e9a1a`; anchors restated for this base: family `224–235` (docstring `234`), wrapper diagnostics `178–202`; README.md:36 links FEATURES.md; pyproject.toml:9 = readme field; v0.9.0 e2e confirmed host-gated real-binary |

No tests were executed and no source file was modified (docs-only task).
"Tree left uncommitted by instruction" (here and in §7) is a historical
statement about authoring time, not the current state: the handoff has
since been committed on `docs/py7zip-snapshot-family-handoff-20261012`
(`0899976` adds this document; `b134d91` corrects its date). The present
revision restates the `py7zip/py7zip.py` anchors for that committed
execution base (W14) and tightens Phase A/C′ acceptance wording; it changes
no classification, gate, or scope decision.

## 12. Appendix — the implemented contract as it exists at `v0.9.0` (`5a60a7c2`)

Reference for whoever executes Phase C′; verified by W6/W8, quoted from
`v0.9.0:py7zip/py7zip.py` and `v0.9.0:py7zip/safe.py`.

| Method | Delegates to | Operation | Behavior |
|---|---|---|---|
| `full(src, dst, options="")` | `SafePy7zip.full` | `compress` | complete archive; `-y` prepended before caller options (`safe.py:257–269`) |
| `incremental(src, dst, options="")` | `SafePy7zip.incremental` | `update` | 7-Zip default `u` semantics; newest file wins; **deleted files retained**; missing archive created (`safe.py:271–284`) |
| `differential(src, dst, options="", *, diff_path=None)` | `SafePy7zip.differential` | `update` with `-y -u- -up0q3r2x2y2z0w2!{diff}` | base untouched; diff gets new/changed files + anti (tombstone) entries; must be `.7z` (`ValueError` otherwise); pre-existing diff **deleted first** (`13fe83e`); default `<base-stem>.diff.7z` (`safe.py:286–317`) |
| `snapshot(src, dst, options="", *, timestamp=None)` | `SafePy7zip.snapshot` | `compress` to `<stem>.<YYYYmmddTHHMMSS>.7z` | original left intact; naive local-time stamp, overridable for determinism (`safe.py:319–341`) |

Supporting shape: `Py7zip._normalize_options` maps `""`/`None` → `()` and
passes non-empty strings through so the argv runtime raises the same
`TypeError` as the aliases (`v0.9.0:py7zip/py7zip.py:224–234`);
`Py7zip._backup_executor` returns `self._safe` on the default runtime and,
on legacy, resolves `7za` from PATH via `shutil.which` (typed
`ArchiveExecutionError` if absent) so both runtimes execute identically
(`:236–253`). `ArchiveRunner.run` accepts `{"compress", "decompress",
"update"}` (`v0.9.0:py7zip/safe.py:87–88`) — this line accepts only
`{"compress", "decompress"}` (`py7zip/safe.py:58–59`), which is the
minimal integration delta.
