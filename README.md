# py7zip
An unofficial, cross platform, lightweight, and easy to use port of 7zip command line binaries (7za) for Python. 
Unlike other libraries, this one fully supports 7zip natively, is easy to setup/install, and is "pythonic" with 
the intent to be used in code and scripts, not through the terminal.

## Why Choose py7zip?
- **Seamless Integration**: Unlike other libraries, py7zip seamlessly integrates 7zip functionality directly into Python, eliminating the need for external dependencies or cumbersome command-line executions.
- **Cross-Platform Compatibility**: Whether you're running Windows, Linux, or Mac, py7zip ensures consistent performance and reliability across all major operating systems.
- **Pythonic Design**: With a focus on adhering to Python's idiomatic principles, py7zip boasts an intuitive API that is easy to understand and use within your codebase.
- **Lightweight and Efficient**: Despite its robust feature set, py7zip remains remarkably lightweight, occupying less than 1MB of disk space.

## Features
- Simplified "point-in-time" backups and full/incremental schemas using snapshots
- Comprehensive documentation through online wiki pages (using standard markdown).
- Cross platform support for Windows, Linux, and Mac.
- Native "Pythonic" logic removes need for additional libraries or CLI executing.
- Uses '7za' compiled library for compatability, Performance, and Reliability.
- Lightweight, being under 1mb in size.

## Usage
### Install using Pip/PyPi (Default; most common)
- `pip install py7zip`

### Install using Git
- Browse to teh location to install and open terminal/cmd
- `git clone https://github.com/aliasfoxkde/py7zip.git`
- `python setup.py .`

### Install Using Pip+Git (Alternative)
- `pip install git+https://github.com/aliasfoxkde/py7zip.git`

## Tasks
- Detecting hardware, determine Platform and archetecture and download appropriate 7za CLI version:
- Create online repository to store ~8 possible CLI platform versions of '7za'.

## Platforms Supported and Tested:
- [ ] Linux x86-64 (64-bit)
- [ ] Linux x86 (32-bit)
- [ ] Linux arm64 (64-bit)
- [ ] Linux arm (32-bit)
- [ ] macOS (arm64 / x86-64)
- [ ] Windows x64 (64-bit)
- [ ] Windows x86 (32-bit )
- [ ] Windows arm64 (64-bit)

## CHANGELOG
- 0.1.0 - Initial Commit
  - Empty repo with base README created.
  - Initial planning and scope created.
  - PyPi package references created.
  - Versioing: Major.Minor.Bug
