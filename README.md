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
- Simplifies lessor known features of 7zip. Such as full, differential, incremental backups, etc.
- Comprehensive documentation through online wiki pages (using standard markdown).
- Cross platform support for Windows, Linux, and Mac.
- Native "Pythonic" logic removes need for additional libraries or CLI executing.
- Uses '7za' compiled library for compatability, Performance, and Reliability.
- Lightweight, being under 1mb in size.

## Usage
### Install using Pip/PyPi (Default; most common)
- `pip install py7zip`

### Install using Git Clone
- Browse to the location to install and open terminal/cmd
- `git clone https://github.com/aliasfoxkde/py7zip.git`
- `pip install .`

### Install Using Pip+Git (Alternative)
- `pip install git+https://github.com/aliasfoxkde/py7zip.git`

### Documentation
- [**USAGE.md**](./docs/USAGE.md): includes detailed instructions on how to use this module.
- [**PLANNING.md**](./docs/PLANNING.md): includes Tasks, Improvements, and General planning stages.
- [**CHANGELOG.md**](./docs/CHANGELOG.md): includes versioning and a list of changes made between them.
- [**LICENSE.md**](./docs/LICENSE.md): includes all licensing information for use of this module.
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

## 7-zip Features (Source: https://www.7-zip.org):
- **License**: "You can use 7-Zip on any computer, including a computer in a commercial organization. 
  You don't need to register or pay for 7-Zip" (Source: 7-zip.org/license.txt). So the 7za binaries 
  are compatible with this module's (py7zip) MIT permissive and non-restrictive license.
- ***Compatibility**: 7-Zip works in Windows 11, 10, 8, 7, Vista, XP, 2022, 2019, 2016, 2012, 2008, 2003, and 2000.
- **Supported formats**:
  - Packing / unpacking: 7z, XZ, BZIP2, GZIP, TAR, ZIP and WIM
  - Unpacking only: APFS, AR, ARJ, CAB, CHM, CPIO, CramFS, DMG, EXT, FAT, GPT, HFS, IHEX, ISO, LZH, LZMA, MBR, MSI, NSIS, NTFS, QCOW2, RAR, RPM, SquashFS, UDF, UEFI, VDI, VHD, VHDX, VMDK, XAR and Z.
- High compression ratio in 7z format with LZMA and LZMA2 compression
- For ZIP and GZIP formats, 7-Zip provides a compression ratio that is 2-10 % better than the ratio provided by PKZip and WinZip
- Strong AES-256 encryption in 7z and ZIP formats
- Self-extracting capability for 7z format
- Integration with Windows Shell
- Powerful File Manager
- Powerful command line version
- Plugin for FAR Manager
- Localizations for 87 languages
