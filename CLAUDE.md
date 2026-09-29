# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

py7zip is a thin, cross-platform Python wrapper around 7-Zip's `7za` command-line binary. The entire runtime is one class, `Py7zip`, in `py7zip/py7zip.py`. It ships no binaries in the wheel: on first instantiation it detects the host platform and downloads a matching `7za` binary from this repo's `main` branch (raw.githubusercontent) into the package directory. Preserve the public `Py7zip` API and the MIT license (see `AGENTS.md`).

## Critical constraints (from AGENTS.md)

- **Never instantiate `Py7zip` in tests or scripts by default** — the constructor performs a network download and writes a file next to the module. Tests must use deterministic fixtures; network/download/extraction boundaries are only exercised by tests that explicitly opt in and record platform/arch.
- **Promotion rule:** do not claim platform support from source inspection. Any support claim needs a receipt naming commit, Python version, OS/arch, binary provenance, and test result. `docs/planning/HANDOFF.md` tracks the current qualification boundary (advisory 5/10 — not production-qualified).
- Release notes: historical notes live in `docs/CHANGELOG.md`; canonical **future** release notes go in `.github/CHANGELOG.md`.
- Never commit credentials, generated binaries, caches, or profiling output.

## Commands

```bash
pip install .                                  # install from checkout
python -m compileall py7zip                    # syntax check (no network, no side effects)
python -m build                                # build sdist+wheel
python setup.py sdist bdist_wheel              # legacy build (what SETUP.md/push.bat use)
```

- **Tests:** there is no test suite yet — `py7zip/tests/debugging.py` is a manual dev script that hits the network. New tests go under `py7zip/tests/` and must run offline; run one with `pytest py7zip/tests -k <name>`. No lint/type config exists for this repo.
- **Version bump:** edit the first `- X.Y.Z` line in `docs/CHANGELOG.md`. `setup.py:read_version()` parses it, and `.github/workflows/publish.yml` triggers on any push touching that file, publishing to PyPI only when the version is new. Local alternative: `push.bat -m "msg"` (Windows; auto-commits and conditionally publishes via `PYPI_API_KEY`).

## Architecture

`Py7zip.__init__` (`py7zip/py7zip.py`) does everything:

1. **Platform detection** — `platform.system()` → `win`/`lin`/`mac`; `platform.machine()` → `pc` (x86_64/AMD64) or `arm`; `platform.architecture()[0]` → `x86`/`x64`. Unsupported combos raise `NotImplementedError`.
2. **URL construction** — `{base}/{sys_platform}/{sys_type}/{arch_type}/7za{ext}`, mirroring the checked-in `bin/<os>/<machine>/<arch>/7za[.exe]` tree (note: arch dirs are named `x86`/`x64`, not `32bit`/`64bit`).
3. **Acquisition** — `setup()` → `download_binary()` streams the binary next to the module file (`os.path.dirname(__file__)`) and chmods 0o755. This runs on every instantiation when the file is absent.
4. **Execution** — all operations funnel through `wrapper()`, which formats a shell string and runs it with `subprocess.run(shell=True)`. `compress`/`archive`/`backup` and `decompress`/`extract` are thin aliases for `wrapper(method=...)`.

### Known sharp edges (documented, not yet fixed)

- `wrapper()` invokes bare `7za` from `PATH` — the binary downloaded to the package dir in step 3 is never actually executed.
- `decompress`/`extract`/`compress`/`archive`/`backup` accept `options` but pass `options=''` to `wrapper`, silently dropping caller switches.
- `full`, `incremental`, `differential`, `snapshot` are unimplemented stubs; HANDOFF.md lists "implement or remove" as required work.
- `py7zip/__init__.py` is empty, so the documented `import py7zip; py7zip.Py7zip()` doesn't work — the working path is `from py7zip import py7zip; py7zip.py7zip.Py7zip()` (see `py7zip/tests/debugging.py`).

Planned/reported work items (tests, arg-list subprocess boundary, stub resolution, per-platform qualification) are enumerated in `docs/planning/HANDOFF.md` under "Required next work" — check there and `docs/PLANNING.md` before scoping changes.
