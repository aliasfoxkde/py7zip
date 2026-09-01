# Repository guidance

## Scope

py7zip is a Python wrapper that downloads and invokes a platform-specific
7-Zip binary. Preserve the public `Py7zip` API and the documented MIT license
for this wrapper; keep 7-Zip’s upstream license notices with distributed
binary assets.

## Validation

- Run syntax/import checks on a clean Python environment before packaging.
- Do not download binaries during tests unless a test explicitly opts into an
  integration probe and records the platform/architecture.
- Treat network access, executable installation, and archive extraction as
  failure-prone boundaries; test them with deterministic fixtures where
  possible.
- Never commit credentials, generated binaries, caches, or profiling output.
- Keep release notes under `.github/CHANGELOG.md`; keep reference documents
  under `docs/`.

## Promotion rule

Do not claim platform support from source inspection alone. Record the exact
Python version, operating system, architecture, binary provenance, and test
result for each supported platform.
