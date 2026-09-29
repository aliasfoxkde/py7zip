# USAGE

## Example Python script:
```python
import py7zip

# Constructing Py7zip performs platform detection only: no download, no
# network, no process starts. The binary is acquired explicitly.
z = py7zip.Py7zip(cache_dir="~/.cache/py7zip")
binary = z.ensure_binary()  # downloads a checksum-verified 7za on first call

src = "path/to/file-or-folder"
archive = "path/to/backup.7z"  # for compress, the destination IS the archive
outdir = "path/to/output/directory"  # for decompress, the destination is a dir

# Compress source file or directory into an archive (a command)
result = z.compress(src, archive)

# Decompress an archive back into a directory (x command)
result = z.decompress(archive, outdir)

# Every operation returns an ArchiveResult; failures raise typed errors
# (ArchiveExecutionError, ArchiveTimeoutError, ArchiveTraversalError).
if result.success:
    print("ok:", result.command)
```

Options are individual switch arguments, never a free-text shell string:

```python
z.compress(src, archive, options=("-mx=9",))
z.decompress(archive, outdir, options=("-y",))
```

### Backup family
```python
z.full(src, archive)  # complete archive (a -y)
z.incremental(src, archive)  # update in place; deletions are kept
z.differential(src, archive)  # writes <archive-stem>.diff.7z next to it
z.snapshot(src, "backups/site.7z")  # stamps the name: site.20260928T221500.7z
```

Differential restore is two extractions, base first, then the diff with
overwrite enabled:

```python
z.decompress("site.7z", "restore", options=("-y",))
z.decompress("site.diff.7z", "restore", options=("-y",))
```

### Legacy mode
`Py7zip(legacy=True)` preserves the historical constructor: it probes this
repository over HTTPS for the version and downloads a binary into the package
directory on instantiation. New code should use the default (safe) mode, which
verifies digests, validates archive members on extraction, and never touches
the shell.

## 7zip Usage (Command Line Arguments; aka "Options")
	Usage: 7za <command> [<switches>...] <archive_name> [<file_names>...] [@listfile]

	<Commands>
	  a : Add files to archive
	  b : Benchmark
	  d : Delete files from archive
	  e : Extract files from archive (without using directory names)
	  h : Calculate hash values for files
	  i : Show information about supported formats
	  l : List contents of archive
	  rn : Rename files in archive
	  t : Test integrity of archive
	  u : Update files to archive
	  x : eXtract files with full paths

	<Switches>
	  -- : Stop switches and @listfile parsing
	  -ai[r[-|0]][m[-|2]][w[-]]{@listfile|!wildcard} : Include archives
	  -ax[r[-|0]][m[-|2]][w[-]]{@listfile|!wildcard} : eXclude archives
	  -ao{a|s|t|u} : set Overwrite mode
	  -an : disable archive_name field
	  -bb[0-3] : set output log level
	  -bd : disable progress indicator
	  -bs{o|e|p}{0|1|2} : set output stream for output/error/progress line
	  -bt : show execution time statistics
	  -i[r[-|0]][m[-|2]][w[-]]{@listfile|!wildcard} : Include filenames
	  -m{Parameters} : set compression Method
		-mmt[N] : set number of CPU threads
		-mx[N] : set compression level: -mx1 (fastest) ... -mx9 (ultra)
	  -o{Directory} : set Output directory
	  -p{Password} : set Password
	  -r[-|0] : Recurse subdirectories for name search
	  -sa{a|e|s} : set Archive name mode
	  -scc{UTF-8|WIN|DOS} : set charset for console input/output
	  -scs{UTF-8|UTF-16LE|UTF-16BE|WIN|DOS|{id}} : set charset for list files
	  -scrc[CRC32|CRC64|SHA1|SHA256|*] : set hash function for x, e, h commands
	  -sdel : delete files after compression
	  -seml[.] : send archive by email
	  -sfx[{name}] : Create SFX archive
	  -si[{name}] : read data from stdin
	  -slp : set Large Pages mode
	  -slt : show technical information for l (List) command
	  -snh : store hard links as links
	  -snl : store symbolic links as links
	  -sni : store NT security information
	  -sns[-] : store NTFS alternate streams
	  -so : write data to stdout
	  -spd : disable wildcard matching for file names
	  -spe : eliminate duplication of root folder for extract command
	  -spf[2] : use fully qualified file paths
	  -ssc[-] : set sensitive case mode
	  -sse : stop archive creating, if it can't open some input file
	  -ssp : do not change Last Access Time of source files while archiving
	  -ssw : compress shared files
	  -stl : set archive timestamp from the most recently modified file
	  -stm{HexMask} : set CPU thread affinity mask (hexadecimal number)
	  -stx{Type} : exclude archive type
	  -t{Type} : Set type of archive
	  -u[-][p#][q#][r#][x#][y#][z#][!newArchiveName] : Update options
	  -v{Size}[b|k|m|g] : Create volumes
	  -w[{path}] : assign Work directory. Empty path means a temporary directory
	  -x[r[-|0]][m[-|2]][w[-]]{@listfile|!wildcard} : eXclude filenames
	  -y : assume Yes on all queries