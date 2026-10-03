# py7zip
An unofficial, cross platform, lightweight, and easy to use wrapper for 7zip command line binaries (7za) in Python. 
Unlike other libraries, this one fully supports 7zip natively, is easy to setup/install, and is "pythonic" with 
the intent to be used in code and scripts — and it now ships the same operations as a `py7zip` command-line
utility (plus `python -m py7zip`). Additionally, you CAN use the '7za' binaries
directly as the specific binaries for your system will be installed automatically and you can therefore use it from
the terminal/command line as you normally would. This also lends to making cross platform apps using this module.

Acquired binaries are verified against pinned SHA-256 digests before use, and all
archive operations run the binary through an argument-list boundary (no shell)
with member validation on extraction. See [docs/USAGE.md](docs/USAGE.md) and
[docs/planning/COMPATIBILITY.md](docs/planning/COMPATIBILITY.md).

## Quick start

```python
import py7zip

z = py7zip.Py7zip()  # detection only: no I/O at import or construction
z.ensure_binary()  # downloads a checksum-verified 7za on first call
result = z.compress("path/to/src", "backup.7z")
if result.success:
    print("ok:", result.command)
```

```console
$ py7zip compress src/ backup.7z
$ py7zip list backup.7z
$ py7zip extract backup.7z restore/
```

The CLI exposes `download`, `compress`, `full`, `incremental`, `extract`,
`list`, `differential`, and `snapshot` with shell-readable exit codes; the
full surface is documented in [docs/USAGE.md](docs/USAGE.md).

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
- [x] Linux x86-64 (64-bit)
- [ ] Linux x86 (32-bit)
- [ ] Linux arm64 (64-bit)
- [ ] Linux arm (32-bit)
- [ ] macOS (arm64 / x86-64)
- [x] Windows x64 (64-bit)
- [ ] Windows x86 (32-bit )
- [ ] Windows arm64 (64-bit)

Per the repository promotion rule, a checked box means the bundled 7za artifact
for that host was executed by the test suite on that platform; claims are
receipted in [docs/planning/PLATFORM_MATRIX.md](docs/planning/PLATFORM_MATRIX.md).
Every host above has a checksummed artifact in `bin/`; unchecked boxes mean no
execution receipt exists yet, not that the artifact is absent.

### Notes
- If you install this package using `git clone`, then all binary packages will be included. 
  This is not the case when using `pip install` as only the binary for the given system is 
  included; this allows for managing the various binaries easy through git versioning.
- Please also keep in mind, unless you are planning on bundling this module with your own
  custom package, or want to contribute to the project there is little other reason to use 
  git to install it, because your python environement will not be able to locate it and 
  pathing will not be inherited.