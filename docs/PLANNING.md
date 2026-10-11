# PLANNING
This document is intended to plan out steps, tasks, and features of this module. 
Implimented tasks and changes are moved to the CHANGELOG as new versions are commited.

> **Current execution plan (2026-10-10):** the Platform Architecture modernization handoff lives at
> [`docs/handoffs/PLATFORM_ARCHITECTURE_PY7ZIP_2026-10-10.md`](handoffs/PLATFORM_ARCHITECTURE_PY7ZIP_2026-10-10.md)
> and takes precedence for sequencing; items below are annotated where that handoff resolves or
> supersedes them. This file remains the canonical task ledger.

## Tasks
- Add and test github actions to automate building wheel and updating PyPi package
  (2026-10-10: workflows exist (`.github/workflows/`), but PyPI still shows 0.7.3 unpublished — see Bugs; handoff P0.5)
- Add simplified functions for various commands (full, incremental, differential, snapshot)
  (2026-10-10: still unimplemented stubs in `py7zip/py7zip.py`; handoff P1.2 decides remove-vs-implement)
- Setup GitHub Wiki in Repo (include navigation, header and footers; update HOME.md)
- Refactor py7zip library to be more straight forward.
  (2026-10-10: in progress — safe runtime is the default since commits 7661132..9d428da (2026-09-01); remaining migration tasks in handoff P1)
- Improve docstrings to include "usage", etc.
- Add declarators to handle pass-through logic to 7za (make more dynamic)
- Complete general python library and test
- Ongoing cleanup

### Improvements
- Add Localizations/Language support
- Create wrapper to allow standard commands to be passed through 7za binary,
  which extends functionality without adding complexity (if not desired; WIP)
- Need to compile/build binaries for Mac for 'arm' and 'pc' binaries (to replace generic one).
- After initial testing and development, move general library to main (py7zip class)?
- Add custom parameters, flags, and functions to simplify usage and features of 7za libs.
- Add auto-commit logic and flags to setup.py file (or dedicated "push.py" file)
- Replace batch files with cross-platform equivilant python scripts
- Replace 'CURL', 'Findstr' for more cross platform (python) and compatible options
- Dynamically load metadata from JSON or config files for setting parameters
- Build out and test initial functionality:
  - [ ] Compress
  - [ ] Decompress
  - [ ] Snapshot
  - [ ] Backup

### Documentation
- Create graphics (logo, icon, info), charts, benchmarks, and the like for docs
- Create extensive documentation for repo (7za docs, usage, etc)
- Improve markdown documentation for Wiki, PyPi, GitHub, etc.
  - Use images, add references, and formatted tables
  - Use ```pycon ``` and ```shell ``` tags
- Add navigation to all docs.

### Future Scope
- Build Unit, Sanity, Performance, etc. Tests
- Benchmark & document issues of different Python compression libraries.
- Add language support

### Bugs
- "Project Page" Link on PyPi site is broken and needs to be setup.
  (2026-10-10: reconfirmed — `https://py7zip.cyopsys.com` returns an empty response; handoff P2.5)
- Fix GitHub actions not automatically updating PyPi package (action/keys deleted?)
  (2026-10-10: confirmed live — PyPI latest published version is 0.6.2 while `pyproject.toml` is 0.7.3; publishing is now trusted-publishing based; handoff P0.5)
- Fix Python package version check error (package.__version__ returns AttributeError)
  (2026-10-10: fixed on the default (safe) runtime — `__version__` now comes from package metadata (`py7zip/py7zip.py`); the legacy `legacy=True` path still probes the network and can return "0.0.0")

### Testing
- Test whether "aliases" or direct methods perform better (or neglegable difference)
- One-to-one comparision between 7za and this python package.
- Test the tool in production code (other projects requiring 'zip') and refactor as needed.
- Is using CURL on Windows reliable across versions (or consider using different method)
- Development Testing (ongoing)

### Notes
- Docs, '7za' Binaries, and scripts (setup.py & push.py) are excluded from PyPi/Pip package
  and are instead only referenced by README.md and used to by py7zip to dynamically load as
  needed (but still kept in an easy to access place and simple to update, using Git).