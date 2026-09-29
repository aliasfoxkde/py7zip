# Changelog

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

## Unreleased

- Added repository guidance and a root MIT license for the Python wrapper.
- Established `.github/` as the release-note location for future changes.
- Added bounded Python 3.9–3.13 CI and package metadata validation.
- Reworked publishing to run only for a published release whose tag matches
  the package version; publishing uses PyPI trusted publishing.
- Added a GitForge pipeline definition (`.gitforge.yml`) mirroring the CI
  lanes on the primary CI platform.

## 0.7.3

See [`../docs/CHANGELOG.md`](../docs/CHANGELOG.md) for the historical release
notes maintained by the project.
