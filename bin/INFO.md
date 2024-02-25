# INFO
This directory contains the various platform specific binaries for the `py7zip` module.

## Structure
- The directory tree for binaries are broken down with the following convention:
  - ./bin/{platform}/{type}/7za.{extension}
  - ./bin/lin|mac|win/pc|arm/x86|x64
  - Examples:
    - Windows: ./bin/win/pc/x64/7za.exe
    - Linux:   ./bin/lin/arm/x86/7za
    - Mac:     ./bin/mac/any/7za
  - Notes: 
    - Platforms consist of Lin/Mac/Win
	- Extensions consist of .exe or None
	- Types consist of PC/arm

## Windows Binaries
- bin/win/arm/x64/7za.exe
- bin/win/arm/x86/7za.exe
- bin/win/pc/x64/7za.exe
- bin/win/pc/x86/7za.exe

## Linux Binaries
- bin/lin/arm/x32/7za
- bin/lin/arm/x64/7za
- bin/lin/pc/x64/7za
- bin/lin/pc/x86/7za

## Mac OS Binaries
- bin/mac/any/7za
- bin/mac/arm/x32/7za
- bin/mac/arm/x64/7za
- bin/mac/pc/x64/7za
- bin/mac/pc/x86/7za

### Notes
- TBD: Unix, Dos, Pocket PC, etc. 