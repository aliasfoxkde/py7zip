# TERMS

Definitions for terms used throughout this repository.

- **7za** — the standalone command-line 7-Zip binary this package wraps. It is
  a reduced version of 7-Zip that handles the 7z, ZIP, GZIP, BZIP2, XZ, TAR and
  WIM formats. The upstream CLI is `7za`; `7zz` is the full-featured console
  build and is not used here.
- **Safe runtime** — the default execution mode: argument-list invocation (no
  shell), digest-verified binary acquisition, timeouts, structured results, and
  typed errors. Selected by `Py7zip(...)` with no arguments.
- **Legacy mode** — the historical runtime, enabled only by the explicit
  `Py7zip(legacy=True)` flag: HTTP version probe on construction, download into
  the package directory, and `shell=True` invocation kept for migration.
- **Artifact catalog** — the table in `py7zip/platforms.py` mapping each
  normalized host to the published `bin/` artifact, its SHA-256 digest, and its
  size in bytes.
- **PlatformInfo** — the normalized host identity (system, machine, pointer
  width, family, architecture) the catalog resolves against.
- **Acquisition** — downloading a catalog artifact into a caller-supplied cache
  directory, with atomic replace and a stale-lock-aware cache lock.
- **ArchiveResult** — the structured return value of every archive operation:
  the exact argv, return code, and captured stdout/stderr.
- **zip-slip** — an extraction attack where an archive member such as
  `../outside` writes outside the destination directory. py7zip refuses such
  members before running the binary.
- **Full backup** — a complete archive of the source tree (`a` command).
- **Incremental backup** — an in-place `u` (update) so every file matches its
  newest copy. Files deleted from the source keep their archived copies.
- **Differential backup** — an archive containing only what differs from a base
  archive, written to a separate `<base>.diff.7z` file; the base is untouched.
- **Snapshot** — a timestamped full archive; the stamp is added to the archive
  name, so an existing archive is never overwritten.
- **Promotion rule** — this repository's policy that a platform-support claim
  must be backed by a receipt naming commit, Python version, OS/architecture,
  binary provenance, and test result (see AGENTS.md).
