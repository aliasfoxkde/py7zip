# PLANNING
This document is intended to plan out steps, tasks, and features of this module. 
Implimented tasks and changes are moved to the CHANGELOG as new versions are commited.

## Tasks

### CODE
- Download and setup cloud storage for binaries by platform (system and archetecture).
- Detecting hardware, determine Platform, and archetecture and download appropriate 7za CLI version (dynamically)
- Add platform checks and support for Windows, Linux, and Mac.
- After initial testing and development, move general library to main
- Add custom parameters, flags, and functions to simplify usage and features of 7za libs.
- Add auto-commit logic and flags to setup.py file (or dedicated "push.py" file)
- Replace 'CURL', 'Findstr' for more cross platform (python) and compatible options
- Dynamically load metadata from JSON or config files for setting parameters
- Build out and test initial functionality:
  - [ ] Compress
  - [ ] Decompress
  - [ ] Snapshot
  - [ ] Backup

### Infrastructure
- Create online repository/webpage to store ~8 possible CLI platform versions of '7za' and reference docs.
- Add action (through github or 'push' script) to update PyPi project on version change.

### Documentation
- Create graphics (logo, icon, info), charts, benchmarks, and the like for docs
- Improve markdown documentation for Wiki, PyPi, GitHub, etc.
  - Use images, add references, and formatted tables
  - Use ```pycon ``` and ```shell ``` tags
- Add navigation to all docs.

### Future Scope
- Build Unit, Sanity, Performance, etc. Tests
- Benchmark & document issues of different Python compression libraries.
- Add language support

### Bugs
- Links are broken on PyPi Project Page: https://pypi.org/project/py7zip/
  and without reference to GitHub repository directly.

### Testing
- One-to-one comparision between 7za and this python package.
- Test the tool in production code (other projects requiring 'zip') and refactor as needed.
- Is using CURL on Windows reliable across versions (or consider using different method)
- Development Testing (ongoing)

### Notes
- Docs, '7za' Binaries, and scripts (setup.py & push.py) are excluded from PyPi/Pip package
  and are instead only referenced by README.md and used to by py7zip to dynamically load as
  needed (but still kept in an easy to access place and simple to update, using Git).