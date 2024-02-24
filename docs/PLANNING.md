# PLANNING
This document is intended to plan out steps, tasks, and features of this module. 
Implimented tasks and changes are moved to the CHANGELOG as new versions are commited.

## Tasks

### CODE
- Detecting hardware, determine Platform, and archetecture and download appropriate 7za CLI version (dynamically)
- Add platform check and support for Windows, Linux, and Mac.
- Build out and test initial functionality:
  - [ ] Compress
  - [ ] Decompress
  - [ ] Snapshot
  - [ ] Backup

### Infrastructure
- Create online repository/webpage to store ~8 possible CLI platform versions of '7za' and reference docs.
- Add action (through github or 'push' script) to update PyPi project on version change.

### Documentation
- Include github page in README (for PyPi).
- Consider moving all features (7zip and Project) to FEATURES.md doc.
- Make path the documentation use URL of Repo (so it works everywhere).
- Improve markdown documentation for Wiki, PyPi, GitHub, etc.
  - Use images, add references, and formatted tables
  - Use ```pycon ``` and ```shell ``` tags
- Create Initial USAGE.md document.
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
- Development Testing (ongoing)