# FEATURES
Reference documentation that details the features of this module as well as 7zip.

## Py7zip
- Safe runtime by default: platform detection on construction, with binary
  acquisition, verification, and execution as explicit operations.
- Checksum-verified binary acquisition: every downloaded artifact is checked
  against a pinned SHA-256 digest and size before it is used.
- Argument-list execution boundary (no shell), with timeouts and typed errors:
  `ArchiveExecutionError`, `ArchiveTimeoutError`, `ArchiveTraversalError`,
  `ArtifactAcquisitionError`, `ArtifactIntegrityError`,
  `ArtifactLockTimeoutError`, `UnsupportedPlatformError`.
- Extraction validates archive members and refuses paths that would escape the
  destination directory (zip-slip protection).
- Full / incremental / differential / snapshot backup modes over the same
  runtime, with the differential restore procedure documented in USAGE.md.
- Structured `ArchiveResult` carrying the exact argv, exit code, and captured
  output, so failures are observable instead of silent.
- Cross platform support for Windows, Linux, and Mac.
- Lightweight, being under a few megabytes in size (varies by platform).
- In-repo reference documentation under `docs/` (usage, compatibility, platform
  matrix, planning).

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
