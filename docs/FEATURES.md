# Features
Reference documentation that details the features of this module as well as 7zip.

## Py7zip
- Simplified "point-in-time" backups and full/incremental schemas using snapshots
- Simplifies lessor known features of 7zip. Such as full, differential, incremental backups, etc.
- Comprehensive documentation through online wiki pages (using standard markdown).
- Cross platform support for Windows, Linux, and Mac.
- Native "Pythonic" logic removes need for additional libraries or CLI executing.
- Uses '7za' compiled library for compatability, Performance, and Reliability.
- Lightweight, being under 1mb in size.

## 7-zip Features (Source: https://www.7-zip.org):
- **License**: "You can use 7-Zip on any computer, including a computer in a commercial organization. 
  You don't need to register or pay for 7-Zip" (Source: 7-zip.org/license.txt). So the 7za binaries 
  are compatible with this module's (py7zip) MIT permissive and non-restrictive license.
- ***Compatibility**: 7-Zip works in Windows 11, 10, 8, 7, Vista, XP, 2022, 2019, 2016, 2012, 2008, 2003, and 2000.
- **Supported formats**:
  - Packing / unpacking: 7z, XZ, BZIP2, GZIP, TAR, ZIP and WIM
  - Unpacking only: APFS, AR, ARJ, CAB, CHM, CPIO, CramFS, DMG, EXT, FAT, GPT, HFS, IHEX, ISO, LZH, LZMA, MBR, MSI, 
    NSIS, NTFS, QCOW2, RAR, RPM, SquashFS, UDF, UEFI, VDI, VHD, VHDX, VMDK, XAR and Z.
- High compression ratio in 7z format with LZMA and LZMA2 compression
- For ZIP and GZIP formats, 7-Zip provides a compression ratio that is 2-10 % better than the ratio provided by 
  PKZip and WinZip
- Strong AES-256 encryption in 7z and ZIP formats
- Self-extracting capability for 7z format
- Integration with Windows Shell
- Powerful File Manager
- Powerful command line version
- Plugin for FAR Manager
- Localizations for 87 languages