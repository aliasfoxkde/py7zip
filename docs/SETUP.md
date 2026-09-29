# SETUP
This document outlines the steps needed to contribute to this project.

## Prerequisites
- Python 3.9+ (3.13 used for the current qualification receipts)
- A checkout of this repository

## Development workflow

```sh
# Install in editable form with test tooling
python -m pip install -e . pytest coverage ruff

# Run the offline test suite (no binary download, no network; the suite
# fails on any socket use). The e2e lane runs the bundled bin/ artifact
# for the detected host and skips cleanly where none exists.
python -m pytest tests/ --cov=py7zip

# Lint and format (zero-findings gate)
ruff check .
ruff format --check .
```

The test suite must stay offline: `tests/conftest.py` installs an autouse
fixture that turns any address resolution or socket connection into a test
failure. Never commit credentials, generated binaries, caches, or profiling
output.

## Building and checking the package

```sh
python -m pip install build twine
python -m build
python -m twine check dist/*
```

Packaging is PEP 621: package metadata and the version live in
`pyproject.toml`.

## Versioning and release

1. Bump `version` in `pyproject.toml`.
2. Add the matching entry at the top of `docs/CHANGELOG.md` (historical) and
   a release note under `.github/CHANGELOG.md` (canonical for future
   releases).
3. Tag the commit with the matching `vX.Y.Z` tag and publish a GitHub/GitForge
   release.

The publish workflow runs only for a published release whose tag matches the
package version and authenticates to PyPI through trusted publishing — there
is no API key to configure.

## Legacy publishing (Windows)

`push.bat` predates the PEP 621 migration and still references
`setup.py`/twine; treat it as unmaintained until it is either updated or
replaced by a cross-platform script (see `docs/PLANNING.md`).
