# USAGE

## Example Python script:
	from py7zip.py7zip import Py7zip

	# Constructing the wrapper detects the host platform. It downloads
	# nothing and starts no process until you request an archive operation.
	z = Py7zip()

	src = "path/to/source"                # file or directory to archive
	archive = "path/to/output/archive.7z"
	outdir = "path/to/output/directory"

	# Optional and explicit: acquire the checksum-verified binary for this
	# platform into the cache now. If skipped, the first archive operation
	# acquires it on demand.
	z.download_binary()

	# Compress source file or directory into the destination archive.
	# Returns an ArchiveResult; check .success / .returncode.
	result = z.compress(src, archive)

	# Decompress an archive back into the destination directory.
	result = z.decompress(archive, outdir)

	# Options are individual arguments, not a shell string; passing a
	# plain string raises TypeError on the default runtime.
	result = z.compress(src, archive, ("-mx9",))

The default runtime is the safe runtime: it executes 7-Zip with an
argument list (never a shell), verifies the downloaded binary's sha256
digest against pinned values, and rejects archive members that would
escape the extraction directory.
	

## 7zip Usage (Command Line Arguments; aka "Options")
	Usage: 7zz <command> [<switches>...] <archive_name> [<file_names>...] [@listfile]

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