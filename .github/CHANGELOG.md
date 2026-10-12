# Changelog

## Unreleased

- Added repository guidance and a root MIT license for the Python wrapper.
- Established `.github/` as the release-note location for future changes.
- Added bounded Python 3.9–3.13 CI and package metadata validation.
- Reworked publishing to run only for a published release whose tag matches
  the package version; publishing uses PyPI trusted publishing.
- Made the safe runtime the default while retaining the legacy runtime only
  behind an explicit migration flag.
- Changed the safe runtime's `Py7zip.get_binary_url()` to raise
  `NotImplementedError` directing callers to the public `download_binary()`
  entry point instead of returning a fabricated cache-relative path
  (OVH-05).
- Added a strict `mypy` gate (`strict = true`, Python 3.9 target) over the
  `py7zip` runtime package with a matching CI lane, and annotated the
  wrapper's public methods without changing runtime behavior.
- Landed the options contract (audit decision D5 / OVH-16): the safe
  runtime accepts only `""` or a sequence of individual arguments and
  raises `TypeError` for any non-empty options string; the legacy
  runtime forwards a sequence as a `shell=False` argument vector while
  keeping the historical `shell=True` string interpolation.
- Fixed the safe runtime's `wrapper()`/`decompress()`/`extract()`
  dispatch to route decompression through `SafePy7zip.decompress()`,
  whose archive-member validation raises `ArchiveTraversalError`
  before extraction begins; the dispatch previously called
  `SafePy7zip.run()` directly and bypassed that guard. Compression
  behaviour and the options contract are unchanged.

## 0.7.3

See [`../docs/CHANGELOG.md`](../docs/CHANGELOG.md) for the historical release
notes maintained by the project.
