# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

py7zip is a cross-platform Python wrapper around 7-Zip's `7za` command-line binary. The default (safe) runtime detects the host platform on construction but performs **no I/O**: acquiring the binary (`ensure_binary()`) and running archives are explicit operations. The legacy runtime — HTTP version probe on construction, download into the package directory, `shell=True` execution — survives only behind the explicit `legacy=True` flag. Preserve the public `Py7zip` API and the MIT license (see `AGENTS.md`).

## Critical constraints (from AGENTS.md)

- **Tests must stay offline.** `tests/conftest.py` installs an autouse fixture that turns any address resolution or socket connection into a failure. Never instantiate `Py7zip(legacy=True)` in tests — it performs a network download. The e2e lane runs the bundled `bin/` artifact for the detected host and skips cleanly elsewhere.
- **Promotion rule:** do not claim platform support from source inspection. Any support claim needs a receipt naming commit, Python version, OS/arch, binary provenance, and test result. `docs/planning/PLATFORM_MATRIX.md` holds the receipts; `docs/planning/HANDOFF.md` tracks the qualification boundary.
- **Contract discipline:** `docs/planning/COMPATIBILITY.md` is the contract ledger. A behaviour change ships together with the test pinning the new behaviour, and the change is recorded there.
- Release notes: historical notes live in `docs/CHANGELOG.md`; canonical **future** release notes go in `.github/CHANGELOG.md`.
- Never commit credentials, generated binaries, caches, or profiling output.

## Commands

```bash
python -m pytest tests/ --cov=py7zip   # offline suite + 99% coverage gate (branch measured)
python -m pytest tests/ -k name        # single test
ruff check .                           # strict lint, zero findings
ruff format .                          # formatter
python -m build && python -m twine check dist/*   # package build
```

Tool configuration lives in `pyproject.toml` (PEP 621 — package version included).

- **Version bump:** edit `version` in `pyproject.toml`, add the entry to `docs/CHANGELOG.md` and `.github/CHANGELOG.md`. `.github/workflows/publish.yml` publishes only for a release whose tag matches the package version, via PyPI trusted publishing.

## Architecture

Two runtimes share one module layout:

- `py7zip/platforms.py` — `PlatformInfo.detect()` normalizes the host; `ArtifactCatalog` maps it to a `bin/` artifact with a pinned SHA-256 digest and size. No I/O, side-effect free.
- `py7zip/acquisition.py` — `ArtifactManager` downloads a catalog artifact into a caller cache dir: checksum + size verification, atomic replace, stale-lock-aware cache lock.
- `py7zip/safe.py` — `ArchiveRunner`/`SafePy7zip`: argument-list subprocess (no shell), timeout, NUL/bytes argv guards, `ArchiveResult` (argv, returncode, stdout/stderr), typed errors (`ArchiveExecutionError`, `ArchiveTimeoutError`, `ArchiveTraversalError`), and `validate_archive_members` (zip-slip guard on extraction). Backup modes: `full` (`a -y`), `incremental` (`u -y`; deletions retained), `differential` (`-up0q3r2x2y2z0w2!diff.7z -u-`; restore = extract base then diff with `-y`), `snapshot` (timestamped name).
- `py7zip/py7zip.py` — `Py7zip` compatibility façade. Safe mode delegates every operation to `SafePy7zip`; the five aliases (`compress`/`archive`/`backup`, `decompress`/`extract`) funnel through `wrapper()`, which returns `ArchiveResult` in safe mode. Legacy mode keeps the historical behaviour.
- `py7zip/__init__.py` — pure re-export of the public API plus `__version__`; importing the package performs no I/O (pinned by `tests/test_import_hygiene.py`).

### Known sharp edges

- **Legacy mode is characterised, not fixed**: shell-string execution, unvalidated paths, and `None` returns are pinned by `tests/test_characterization_wrapper.py` as the documented migration contract. Fix bugs in safe mode; change legacy behaviour only with a COMPATIBILITY.md entry.
- The `-u` update grammar letters are offset from most documentation (`y` = disk-newer); the differential switch `-up0q3r2x2y2z0w2!name` is verified against 7-Zip 24.00 and pinned by e2e tests.
- 7-Zip stores the source directory itself when compressing a directory path — restored trees appear under `<outdir>/<source-name>/`.

Planning status and open work: `docs/planning/HANDOFF.md` and `docs/PLANNING.md`.
