# Changelog

## 0.9.0 - Command-Line Interface

- Added a `py7zip` console script and `python -m py7zip` entrypoint exposing
  the safe runtime as eight subcommands: `download`, `compress`, `full`,
  `incremental`, `extract`, `list`, `differential`, and `snapshot`.
- Defined a shell-readable exit-code contract: 0 success, 1 execution or
  acquisition failure, 2 usage, 3 timeout, 4 refused unsafe archive members,
  5 unsupported platform.
- Added `SafePy7zip.list_entries()` and the shared naming helpers
  `snapshot_name()` / `differential_name()` so the CLI and the runtime derive
  identical archive names.
- Common flags: `--binary-path`, `--cache-dir`, `--timeout`, and repeatable
  `-o/--option` for extra 7-Zip switches.
- Offline suite: 200 tests at 100% line and branch coverage; strict ruff
  lint/format at zero findings.
- Infrastructure accumulated since 0.8.0: bounded Python 3.9–3.13 CI and
  package metadata validation; publishing runs only for a release whose tag
  matches the package version via PyPI trusted publishing; a GitForge
  pipeline definition (`.gitforge.yml`) mirrors the CI lanes on the primary
  CI platform.

## 0.8.0 - Safe Runtime Qualification

- Made the safe runtime the default: no I/O at import or construction;
  digest-verified binary acquisition and archive execution are explicit
  operations. The legacy runtime remains behind the explicit `legacy=True`
  migration flag.
- Implemented `full`, `incremental`, `differential`, and `snapshot` over the
  argument-list runtime; the differential restore procedure is documented.
- Replaced shell-string subprocess execution with argument lists, timeouts,
  structured `ArchiveResult` values, and typed errors.
- Added archive-member validation on extraction (zip-slip protection).
- Re-exported the public API at the package root with an offline import
  guarantee.
- Offline test suite: 183 tests, 100% line and branch coverage under a
  fail-under-99 gate; strict ruff lint/format at zero findings.
- Added a checksummed artifact catalog (SHA-256 and size per platform) and a
  stale-lock-aware cache lock for acquisition.
- Receipted platform qualification for Linux x86-64; see
  `docs/planning/PLATFORM_MATRIX.md`.

## 0.7.3

See [`../docs/CHANGELOG.md`](../docs/CHANGELOG.md) for the historical release
notes maintained by the project.
