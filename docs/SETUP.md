# SETUP
This document outlines the steps needed to contribute to this project.

## Prerequisites
- Python within the supported range (`requires-python` in `pyproject.toml`)
  with `pip`
- A local clone of this repository

## Build and test locally
```shell
    # Run the offline test suite
    python -m pytest tests -p no:cacheprovider

    # Build a wheel into a local scratch directory
    python -m pip wheel . --no-deps -w dist/

    # Inspect the installed package version
    pip show py7zip
```
The test suite must pass with no network access; it fails loudly if any
test attempts to open a socket.

## Publishing changes (maintainers)
Publishing is automated through GitHub Actions
(`.github/workflows/publish.yml`):

- A publish run is triggered by publishing a GitHub **release**. The
  workflow builds the package with `python -m build`, validates it with
  `twine check`, verifies that the release tag matches the `version` in
  `pyproject.toml`, and uploads to PyPI using **trusted publishing**
  (OIDC). No API token is stored in the repository.
- `workflow_dispatch` runs exist for rehearsal only: they build and run
  `twine check` but never publish.
- To cut a release: update `version` in `pyproject.toml` and the release
  notes under `.github/CHANGELOG.md`, then create the matching release
  tag and publish the GitHub release. Never reuse a version or tag that
  has already been published anywhere; the version-selection rules live
  in `docs/handoffs/2026-10-11-py7zip-overhaul.md` (OVH-21).

## Versioning
Versioning changes are based on {Major}.{Minor}.{Bug}.
