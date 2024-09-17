## CHANGELOG
- 0.7.3 - Functional Improvements
  - Updated platform check to account for additional cases
  - Setup cloud storage for binaries by platform (system and archetecture).
  - Added support for detecting hardware, determine Platform, and archetecture and download 
    the appropriate 7za CLI version (dynamically)
  - Added platform checks and support for Windows, Linux, and Mac.
  - Added crossplatform binaries (CLI) versions of '7za' to github repository
  - Added action (through github or 'push' script) to update PyPi project on version change.
  - Tested py7zip and 7za library on Linux (Ubunutu through Windows Subsystem for Linux (WSL))
  - Resolved: Links are broken on PyPi Project Page: https://pypi.org/project/py7zip/
    and without reference to GitHub repository directly.
  - Resolved: Publishing bug in YML causing actions to fail.

- 0.6.2 - Debugging
  - Resolved various issues with wrapper
  - Tested 7za wrapper for Windows x64 platform
  - Refactored compress/decompress logic into wrapper call
    and created aliases for "backup", "archive", and "extract"
  - Put in various placeholders for future logic.
  - Updated "setup.py" and created entry_point script
  - Added "debugging.py" script to tests.

- 0.6.0 - Implimented Platform Binaries
  - Built directory tree for platform binaries (initial, requires testing)
  - Created 'img' folder to organize and store images (graphics, icons, etc)
  - Created INFO.md file for 'bin' folder with reference details
  - Basic Testing of py7zip wrapper function and logic
  - Updated py7zip library and logic

- 0.5.0 - Improved Pipeline and Workflow
  - Updated 'push.bat' script to automatically update Pip package, publish PyPi package on version change, etc.
  - Infastructure: Setup workflow, pipeline and documentation
  - Documentation:
    - Include github page in README (for PyPi).
    - Consider moving all features (7zip and Project) to FEATURES.md doc.
    - Make path the documentation use URL of Repo (so it works everywhere).
    - Create Initial USAGE.md document.

- 0.4.2 - Minor Bug Fixes
  - Worked on pipeline changes (aka. "Push")
  - Updated setup.py to reflect updates
  - Formatting bug caused invalid link

- 0.4.0 - Module Testing & Published to PyPi
  - Added FEATURE.md file and update docs & structure
  - Added general.py module for development and pipeline.
  - Updated setup.py and py7zip.py scripts.
  - Finished testing & fine tuning of setup
  - Published wheels to PyPi (will add auto-action later)

- 0.3.0 - Deployment Testing & PyPi Prep
  - Improved setup.py, setup.cfg, and the like
  - Cloned the deployment and tested installing it.
  - Restructured repository.
  - Debugging as needed.
  - Updated docs.

- 0.2.0 - Crude Implimentation
  - Implimented crude wrapper around 7za cli util for testing.
  - Moved documentation to ./docs
  - Updated Documentation.

- 0.1.0 - Initial Commit
  - Empty repo with base README.md created.
  - Initial planning and scope created.
  - PyPi package references created.
  - Versioing: Major.Minor.Bug