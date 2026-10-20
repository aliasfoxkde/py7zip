# py7zip
An unofficial, cross platform, lightweight, and easy to use wrapper for 7zip command line binaries (7za) in Python. 
Unlike other libraries, this one fully supports 7zip natively, is easy to setup/install, and is "pythonic" with 
the intent to be used in code and scripts, not through the terminal. Additionally, you CAN use the '7za' binaries
directly as the specific binaries for your system will be installed automatically and you can therefor use it from
the terminal/command line as you normally would. This also lends to making cross platform apps using this module.

## Why Choose py7zip?
- **Seamless Integration**: Unlike other libraries, py7zip seamlessly integrates 7zip functionality directly into Python, 
  eliminating the need for external dependencies or cumbersome command-line executions.
- **Cross-Platform Compatibility**: Whether you're running Windows, Linux, or Mac, py7zip ensures consistent performance 
  and reliability across all major operating systems.
- **Pythonic Design**: With a focus on adhering to Python's idiomatic principles, py7zip boasts an intuitive API that is 
  easy to understand and use within your codebase.
- **Lightweight and Efficient**: Despite its robust feature set, py7zip remains remarkably lightweight, occupying less 
  than a few megabytes of disk space (and only specifically for the detected system).
- **Licensing**: This Python Module's MIT License is compatible with the "7-Zip" License and can be "used" without 
  restriction, including for commercial purposes (see LICENSE.md).

## Installation

### Install using Pip/PyPi (Default; most common)
- `pip install py7zip`

### Install using Git Clone
- Browse to the location to install and open terminal/cmd
- `git clone https://github.com/aliasfoxkde/py7zip.git`
- `pip install .`

### Install Using Pip+Git (Alternative)
- `pip install git+https://github.com/aliasfoxkde/py7zip.git`

### Documentation
- [**CHANGELOG.md**](https://github.com/aliasfoxkde/py7zip/blob/main/docs/CHANGELOG.md): includes versioning and a 
  list of changes made between them.
- [**FEATURES.md**](https://github.com/aliasfoxkde/py7zip/blob/main/docs/FEATURES.md): reference documentation that 
  details the features of this module as well as 7zip.
- [**LICENSE.md**](https://github.com/aliasfoxkde/py7zip/blob/main/docs/LICENSE.md): includes all licensing 
  information for use of this module.
- [**PLANNING.md**](https://github.com/aliasfoxkde/py7zip/blob/main/docs/PLANNING.md): includes Tasks, Improvements, 
  and General planning stages.
- [**SETUP.md**](https://github.com/aliasfoxkde/py7zip/blob/main/docs/SETUP.md): includes instructions on technical
  setup of the repository for use with updating and publishing best practices.
- [**TERMS.md**](https://github.com/aliasfoxkde/py7zip/blob/main/docs/TERMS.md): defines terms used throughout repo.
- [**USAGE.md**](https://github.com/aliasfoxkde/py7zip/blob/main/docs/USAGE.md): includes detailed instructions on 
  how to use this module.
- **NOTE**: Documentation is broken down into parts and can be found in ./docs

## Platforms Supported and Tested:
- [ ] Linux x86-64 (64-bit)
- [ ] Linux x86 (32-bit)
- [ ] Linux arm64 (64-bit)
- [ ] Linux arm (32-bit)
- [ ] macOS (arm64 / x86-64)
- [ ] Windows x64 (64-bit)
- [ ] Windows x86 (32-bit )
- [ ] Windows arm64 (64-bit)

No platform row is currently receipt-backed. Per the promotion rule in
`AGENTS.md`, a row may be checked only with a qualification receipt
(exact Python version, OS/architecture, binary provenance, commands, and
test result). The Windows x64 row was unchecked on 2026-10-20 after the
receipt audit in
[`docs/planning/DECISION_WINDOWS_RECEIPTS_2026-10-20.md`](docs/planning/DECISION_WINDOWS_RECEIPTS_2026-10-20.md);
binary provenance states are tracked in
[`bin/PROVENANCE.md`](bin/PROVENANCE.md).

### Notes
- The PyPI wheel ships no binaries. On the default (safe) runtime, the
  matching 7-Zip artifact is downloaded into a cache directory
  (`~/.cache/py7zip` by default) and its sha256 is verified against
  pinned digests before use; acquisition is explicit via
  `download_binary()` or the first archive operation.
- A `git clone` of this repository includes the `bin/` tree itself
  (see [`bin/INFO.md`](bin/INFO.md) and
  [`bin/PROVENANCE.md`](bin/PROVENANCE.md)); the placeholder slots in
  that tree are empty files and are not distributed.