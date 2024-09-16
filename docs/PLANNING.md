# PLANNING
This document is intended to plan out steps, tasks, and features of this module. 
Implimented tasks and changes are moved to the CHANGELOG as new versions are commited.

## Tasks
- Add simplified functions for various commands (full, incremental, differential, snapshot)
- Refactor py7zip library to be more straight forward.
- Improve docstrings to include "usage", etc.
- Add declarators to handle pass-through logic to 7za (make more dynamic)
- Complete general python library and test
- Ongoing cleanup

### Improvements
- Create wrapper to allow standard commands to be passed through 7za binary,
  which extends functionality without adding complexity (if not desired)
- Need to compile/build binaries for Mac for 'arm' and 'pc' binaries (to replace generic one).
- After initial testing and development, move general library to main
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
- "Project Page" Link is broken and needs to be setup.

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