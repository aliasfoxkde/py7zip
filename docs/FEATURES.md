# FEATURES
Reference documentation that details the features of this module as well as 7zip.

## Py7zip
- Backup helper methods are planned but not implemented: `full` is a no-op,
  `incremental` is a no-op, `differential` is a no-op, and `snapshot` is a
  no-op in PyPI 0.6.2 and on the current main line (see
  `docs/planning/COMPATIBILITY.md`).
- Documentation under `docs/` (a GitHub wiki is planned).
- Binaries are cataloged for Linux, Windows, and macOS hosts; other hosts
  are refused with a typed error. Qualified platform-support claims require
  receipts per `AGENTS.md`; see the platform checklist in `README.md` and
  `bin/PROVENANCE.md`.
- Wraps a 7-Zip command-line binary from Python: the default runtime builds
  an argument vector and runs it without a shell.
- Uses 7-Zip console binaries (`7za`) rather than reimplementing archive
  formats in Python.
- Lightweight, being under a few megabytes in size (varies by platform).

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
- Powerful command line version
- Localizations for 87 languages  (not currently implemented)