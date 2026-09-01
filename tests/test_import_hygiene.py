"""Prove that importing the package is offline and free of side effects.

The Phase 0 exit criterion is that no network access and no executable
download happens during import, metadata discovery or test setup.  These
tests check that in a clean interpreter rather than in the pytest process,
so a module-level import side effect cannot hide behind fixture ordering.
"""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap

from tests.conftest import PACKAGE_DIR, REPO_ROOT

PROBE = textwrap.dedent(
    """\
    import socket
    import sys
    from pathlib import Path

    def deny(*_args, **_kwargs):
        raise AssertionError("network access during import")

    socket.create_connection = deny
    socket.getaddrinfo = deny
    socket.gethostbyname = deny
    socket.socket.connect = deny
    socket.socket.connect_ex = deny

    package_dir = Path(sys.argv[1])
    before = sorted(
        str(p.relative_to(package_dir))
        for p in package_dir.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts
    )

    import py7zip

    top_public = sorted(n for n in vars(py7zip) if not n.startswith("_"))
    has_wrapper_class = hasattr(py7zip, "Py7zip")
    has_all = hasattr(py7zip, "__all__")
    print("TOP_PUBLIC:" + repr(top_public))
    print("HAS_WRAPPER_CLASS:" + repr(has_wrapper_class))
    print("HAS_ALL:" + repr(has_all))

    import py7zip.py7zip as module

    after_public = sorted(n for n in vars(py7zip) if not n.startswith("_"))
    after = sorted(
        str(p.relative_to(package_dir))
        for p in package_dir.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts
    )

    print("AFTER_PUBLIC:" + repr(after_public))
    print("PACKAGE_FILE:" + module.__file__)
    print("NEW_FILES:" + repr(sorted(set(after) - set(before))))
    print("PROBE_OK")
    """
)


def _run_probe(*, cwd):
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = str(REPO_ROOT)
    return subprocess.run(
        [sys.executable, "-c", PROBE, str(PACKAGE_DIR)],
        capture_output=True,
        text=True,
        cwd=str(cwd),
        env=env,
        timeout=180,
        check=False,
    )


def test_import_needs_no_network_and_writes_no_files(tmp_path):
    result = _run_probe(cwd=tmp_path)

    assert result.returncode == 0, result.stderr
    assert "PROBE_OK" in result.stdout, result.stdout + result.stderr
    assert "NEW_FILES:[]" in result.stdout, result.stdout + result.stderr


def test_import_does_not_install_a_binary_beside_the_source(tmp_path):
    result = _run_probe(cwd=tmp_path)

    assert result.returncode == 0, result.stderr
    for line in result.stdout.splitlines():
        if line.startswith("PACKAGE_FILE:"):
            assert line[len("PACKAGE_FILE:") :] == str(PACKAGE_DIR / "py7zip.py")
            break
    else:
        raise AssertionError(f"probe produced no PACKAGE_FILE line: {result.stdout}")

    assert not (PACKAGE_DIR / "7za").exists()
    assert not (PACKAGE_DIR / "7za.exe").exists()


def test_the_top_level_package_defines_no_public_api_of_its_own(tmp_path):
    """``import py7zip`` declares no public API of its own.

    Two distinct facts are pinned here because they are easy to conflate.
    Before the submodule is imported, the package root exposes no public
    names at all: the empty ``__init__.py`` adds nothing, defines no
    ``Py7zip`` re-export and sets no ``__all__``.  Afterwards exactly one
    public name appears, ``py7zip``, and that one comes from the import
    system binding an imported submodule onto its parent package rather than
    from anything the package declares.
    """
    result = _run_probe(cwd=tmp_path)

    assert result.returncode == 0, result.stderr
    assert "TOP_PUBLIC:[]" in result.stdout, result.stdout + result.stderr
    assert "HAS_WRAPPER_CLASS:False" in result.stdout, result.stdout + result.stderr
    assert "HAS_ALL:False" in result.stdout, result.stdout + result.stderr
    assert "AFTER_PUBLIC:['py7zip']" in result.stdout, result.stdout + result.stderr


def test_the_shipped_package_directory_contains_no_binaries():
    """Nothing executable sits beside the source in a clean checkout."""
    binaries = [
        entry.name
        for entry in PACKAGE_DIR.iterdir()
        if entry.is_file() and entry.name.startswith("7za")
    ]

    assert binaries == []
