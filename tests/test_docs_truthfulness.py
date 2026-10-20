"""Docs guard for the OVH-03 truth-pass and Phase A of the snapshot-family
handoff.

Pins three properties of the user-facing docs:

1. No unqualified backup-family claim survives in ``docs/FEATURES.md``
   (the per-occurrence qualifier rule from the snapshot-family handoff:
   a qualifier in one clause does not excuse an unqualified claim in
   another).
2. The ``docs/USAGE.md`` import line executes in a clean interpreter
   with no network access, and the constructed wrapper is the safe
   runtime.
3. ``docs/USAGE.md``, ``docs/FEATURES.md``, ``docs/SETUP.md``, and
   ``README.md`` never present ``setup.py`` or ``push.bat`` as the
   current process. Historical changelogs are deliberately not policed:
   they are records of past releases.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import textwrap

from tests.conftest import REPO_ROOT

FEATURES = REPO_ROOT / "docs" / "FEATURES.md"
USAGE = REPO_ROOT / "docs" / "USAGE.md"
SETUP = REPO_ROOT / "docs" / "SETUP.md"
README = REPO_ROOT / "README.md"

FAMILY = re.compile(r"\b(?:full|incremental|differential|snapshot)s?\b", re.I)
QUALIFIER = re.compile(r"\b(?:not[- ]implemented|planned|no-op)\b", re.I)
DELIMITER = re.compile("[;.]")


def _unqualified_family_claims(text: str) -> list[str]:
    occurrences = list(FAMILY.finditer(text))
    failures = []
    for index, occurrence in enumerate(occurrences):
        end = len(text)
        if index + 1 < len(occurrences):
            end = min(end, occurrences[index + 1].start())
        punctuation = DELIMITER.search(text, occurrence.end(), end)
        if punctuation:
            end = min(end, punctuation.start())
        if not QUALIFIER.search(text, occurrence.end(), end):
            failures.append(occurrence.group(0))
    return failures


def test_features_backup_family_claims_are_all_qualified():
    text = FEATURES.read_text()
    failures = _unqualified_family_claims(text)
    assert failures == [], (
        "unqualified backup-family claims in docs/FEATURES.md: "
        f"{failures}"
    )


PROBE = textwrap.dedent(
    """\
    import socket

    def deny(*_args, **_kwargs):
        raise AssertionError("network access during docs snippet run")

    socket.create_connection = deny
    socket.getaddrinfo = deny
    socket.gethostbyname = deny
    socket.socket.connect = deny
    socket.socket.connect_ex = deny

    from py7zip.py7zip import Py7zip

    z = Py7zip()
    assert z.legacy is False
    assert callable(z.compress) and callable(z.decompress)
    assert callable(z.download_binary)
    print("DOCS_SNIPPET_OK")
    """
)


def _run_docs_snippet(*, cwd):
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = str(REPO_ROOT)
    return subprocess.run(
        [sys.executable, "-c", PROBE],
        capture_output=True,
        text=True,
        cwd=str(cwd),
        env=env,
        timeout=180,
        check=False,
    )


def test_usage_import_and_construction_execute_offline(tmp_path):
    result = _run_docs_snippet(cwd=tmp_path)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "DOCS_SNIPPET_OK" in result.stdout


def test_usage_documents_the_submodule_import():
    text = USAGE.read_text()
    assert "from py7zip.py7zip import Py7zip" in text
    assert not re.search(r"^\s*import py7zip\s*$", text, re.M), (
        "docs/USAGE.md must not re-introduce the bare root import; the "
        "root package defines no public API of its own"
    )


def test_user_docs_do_not_present_legacy_publish_flow_as_current():
    for path in (USAGE, FEATURES, SETUP, README):
        text = path.read_text()
        assert "push.bat" not in text, f"{path.name} references push.bat"
        assert "setup.py" not in text, f"{path.name} references setup.py"
        assert "PYPI_API_KEY" not in text, f"{path.name} references PYPI_API_KEY"
