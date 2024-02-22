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

### Documentation
- Create Initial USAGE.md document.
- Add navigation to all docs.

### Future Scope
- Build Unit, Sanity, Performance, etc. Tests
- Add language support

### Testing
- One-to-one comparision between 7za and this python package.
- Development Testing (ongoing)