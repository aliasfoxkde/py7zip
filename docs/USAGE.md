# USAGE

## Example Python script:
	from py7zip.py7zip import Py7zip

	# Constructs the wrapper (offline: nothing is downloaded at
	# construction). The verified binary is acquired automatically on
	# first use if it is not already installed.
	z = Py7zip()
	src = "path/to/zipfile"
	dst = "path/to/output/directory"  # Usually contains a .zip extension

	# Compress source file or directory to destination.
	# options is "" (no options) or a sequence of individual arguments.
	z.compress(src, dst, options=["-y", "-mx=9"])

	# Decompress source archive back to destination directory
	z.decompress(dst, src, options="")


## The `options` argument

Every execution method — `wrapper`, the compress aliases
(`compress`/`archive`/`backup`) and the extract aliases
(`decompress`/`extract`) — forwards `options` unchanged to the same code
path. What `options` accepts depends on the runtime chosen at
construction.

### Safe runtime (default)

`Py7zip()` never invokes a shell. `options` must be one of:

- `""` — the default. No options are forwarded to 7-Zip.
- A sequence (list, tuple, ...) of individual arguments, each forwarded
  to 7-Zip as exactly one argument: `options=["-y", "-mx=9"]`. Elements
  are never split, quoted, or re-interpreted; an element containing
  spaces stays a single argument.

Any non-empty string — `"-y -mx=9"`, `"-oC:\Temp"`, even `" "` — raises
`TypeError` ("options must be a sequence of individual arguments") before
any 7-Zip process is started. Shell-style option text is never parsed or
tokenized: there is deliberately no `shlex`-based bridge on the safe
runtime (audit decision D5 / OVH-16). Split the text into a sequence of
individual arguments instead.

### Legacy runtime (`Py7zip(legacy=True)`)

The legacy runtime exists for backward compatibility with the historical
0.6.x behaviour and is planned for deprecation and removal.

- A string is interpolated verbatim into one shell command that runs with
  `shell=True`. The shell interprets the text: quotes, `$()`, `;` and
  pipes are all live. Only ever pass fully trusted, caller-controlled
  text.
- A sequence is forwarded element by element as an argument vector with
  `shell=False`: no element is re-interpreted by a shell, and an element
  containing spaces or shell metacharacters stays a single argument.


## 7zip Usage (Command Line Arguments; aka "Options")

	The switches listed below are the values a sequence element carries;
	pass each switch as its own element, e.g. `options=["-y", "-mx=9"]`.

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