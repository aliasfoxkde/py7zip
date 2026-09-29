# PLANNING
This document is intended to plan out steps, tasks, and features of this module. 
Implimented tasks and changes are moved to the CHANGELOG as new versions are commited.

Detailed planning records live in [`docs/planning/`](planning/): the public
contract and migration map ([COMPATIBILITY.md](planning/COMPATIBILITY.md)), the
receipted platform matrix ([PLATFORM_MATRIX.md](planning/PLATFORM_MATRIX.md)),
and the current qualification boundary ([HANDOFF.md](planning/HANDOFF.md)).

## Tasks
- Setup GitHub Wiki in Repo (include navigation, header and footers; update HOME.md)
- Add declarators to handle pass-through logic to 7za (make more dynamic)
- Add custom parameters, flags, and functions to simplify usage and features of 7za libs.
- Add Localizations/Language support
- Compile/build binaries for Mac for 'arm' and 'pc' binaries (to replace generic one).
- Add type annotations and a type-checking gate (pyright/mypy) to CI.
- Benchmark & document compression performance against other Python archive libraries.

### Completed
- [x] Add simplified functions for various commands (full, incremental, differential, snapshot)
- [x] Build out and test initial functionality: compress, decompress, snapshot, backup
- [x] Argument-list subprocess boundary with explicit error propagation (replaces shell strings)
- [x] Deterministic offline test suite (183 tests, 100% line and branch coverage)
- [x] Strict ruff lint and format configuration, zero findings
- [x] Offline import guarantee (`import py7zip` performs no I/O and re-exports the public API)
- [x] PEP 621 packaging; version sourced from `pyproject.toml`

### Improvements
- Create wrapper to allow standard commands to be passed through 7za binary,
  which extends functionality without adding complexity (if not desired; WIP)
- Dynamically load metadata from JSON or config files for setting parameters
- Replace batch files with cross-platform equivilant python scripts

### Documentation
- Create graphics (logo, icon, info), charts, benchmarks, and the like for docs
- Improve markdown documentation for Wiki, PyPi, GitHub, etc.
  - Use images, add references, and formatted tables
- Add navigation to all docs.

### Future Scope
- Test the tool in production code (other projects requiring 'zip') and refactor as needed.
- One-to-one comparision between 7za and this python package.

### Bugs (resolved)
- "Project Page" Link on PyPi site is broken and needs to be setup.
- Fix GitHub actions not automatically updating PyPi package (action/keys deleted?)
- Fix Python package version check error (package.__version__ returns AttributeError)

### Notes
- Docs, '7za' Binaries, and scripts (setup.py & push.py) are excluded from PyPi/Pip package
  and are instead only referenced by README.md and used to by py7zip to dynamically load as
  needed (but still kept in an easy to access place and simple to update, using Git).
