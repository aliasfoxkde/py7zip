# PLANNING
This document is intended to plan out steps, tasks, and features of this module. 
Implimented tasks and changes are moved to the CHANGELOG as new versions are commited.

## Tasks

### CODE
- Detecting hardware, determine Platform, and archetecture and download appropriate 7za CLI version (dynamically)
- Download and setup cloud storage for binaries by platform (system and archetecture).
- Add platform check and support for Windows, Linux, and Mac.
- After initial testing and development, move general library to main
- Add custom parameters, flags and functions to simplify usage of 7za libs.
- Build out and test initial functionality:
  - [ ] Compress
  - [ ] Decompress
  - [ ] Snapshot
  - [ ] Backup

### Infrastructure
- Create online repository/webpage to store ~8 possible CLI platform versions of '7za' and reference docs.
- Add action (through github or 'push' script) to update PyPi project on version change.

### Documentation
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
- Development Testing (ongoing)