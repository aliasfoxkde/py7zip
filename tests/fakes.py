"""Deterministic stand-ins for the boundaries the wrapper reaches across.

The current implementation exposes no injection points, so these fakes are
installed at the module seams the wrapper actually uses: ``platform`` for
host facts, ``requests`` for the version probe, ``urllib`` for the binary
download, ``subprocess`` for archive execution and ``os.path`` for existence
checks.  Each fake is scoped to the ``py7zip.py7zip`` module namespace where
that is possible, so the rest of the interpreter keeps its real standard
library.

Nothing here fabricates behaviour the wrapper does not already have: each
fake records what it was asked and either replays a canned response or raises
a real standard-library exception, which is what the wrapper is being
characterised against.
"""

from __future__ import annotations

import subprocess
from collections import namedtuple
from types import SimpleNamespace

import py7zip.py7zip as py7zip_module

#: ``platform.uname()`` returns a namedtuple and the wrapper stores it
#: verbatim as ``Py7zip.debug_info``, so the fake reproduces the same fields.
UnameResult = namedtuple("uname_result", "system node release version machine")


class FakePlatform:
    """Replace the host-fact seam with values supplied by a test."""

    def __init__(
        self,
        monkeypatch,
        system="Linux",
        machine="x86_64",
        architecture=("64bit", "ELF"),
    ):
        self.system = system
        self.machine = machine
        self.architecture = architecture
        self.uname = UnameResult(
            system=system,
            node="characterization-host",
            release="6.0.0-characterization",
            version="#1 SMP characterization",
            machine=machine,
        )
        fake = SimpleNamespace(
            system=lambda: self.system,
            machine=lambda: self.machine,
            architecture=lambda: self.architecture,
            uname=lambda: self.uname,
        )
        monkeypatch.setattr(py7zip_module, "platform", fake)

    def __repr__(self):
        return (
            f"FakePlatform(system={self.system!r}, machine={self.machine!r}, "
            f"architecture={self.architecture!r})"
        )


def make_response(
    body,
    status=200,
    url="https://raw.githubusercontent.invalid/aliasfoxkde/py7zip/main/docs/CHANGELOG.md",
):
    """Build a genuine :class:`requests.Response` carrying ``body``.

    Using the real response type keeps the characterisation honest: the
    wrapper's ``raise_for_status()`` and ``response.text`` calls run through
    the actual requests implementation rather than a hand-rolled shim.
    """
    import requests

    response = requests.Response()
    response.status_code = status
    response.url = url
    response.headers["Content-Type"] = "text/plain; charset=utf-8"
    response._content = body.encode("utf-8")
    return response


class FakeRequests:
    """Replace the ``requests`` seam used by the runtime version probe.

    ``responder`` is called with the requested URL and returns a response or
    raises.  It defaults to a connection failure, which is the state this
    suite guarantees: no network.

    The wrapper's ``except requests.RequestException`` clause resolves against
    whatever object occupies the ``requests`` name, so the fake re-exports the
    real exception classes rather than inventing substitutes.
    """

    def __getattr__(self, name):
        import requests

        return getattr(requests, name)

    def __init__(self, responder=None):
        self.responder = responder or self.offline
        self.calls = []
        self.options = []

    @staticmethod
    def offline(url):
        import requests

        raise requests.ConnectionError(
            f"offline characterization run: refusing to fetch {url}"
        )

    def get(self, url, *args, **kwargs):
        self.calls.append(url)
        self.options.append(kwargs)
        return self.responder(url, *args, **kwargs)

    def install(self, monkeypatch):
        monkeypatch.setattr(py7zip_module, "requests", self)
        return self


class FakeUrllibRequest:
    """Replace the ``urllib.request`` seam used by ``download_binary``.

    ``payload`` is the byte string the download returns, or an exception
    instance to raise instead.
    """

    def __init__(self, payload=b""):
        self.payload = payload
        self.opened = []

    def urlopen(self, url, *args, **kwargs):
        import urllib.error

        self.opened.append(url)
        if isinstance(self.payload, Exception):
            raise self.payload

        class _Context:
            status = 200

            def __init__(self, data):
                self._data = data

            def read(self):
                return self._data

            def __enter__(self):
                return self

            def __exit__(self, *_exc_info):
                return False

        return _Context(self.payload)

    def install(self, monkeypatch):
        monkeypatch.setattr(py7zip_module, "urllib", SimpleNamespace(request=self))
        return self


class FakeSubprocess:
    """Replace the ``subprocess`` seam used by ``Py7zip.wrapper``.

    Records the exact command string and keyword arguments handed to the
    process boundary and either returns a real
    :class:`subprocess.CompletedProcess` or raises the real
    :class:`subprocess.CalledProcessError`, so callers can assert on the
    shell string without launching anything.
    """

    CalledProcessError = subprocess.CalledProcessError

    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.calls = []

    def run(self, command, **kwargs):
        self.calls.append((command, kwargs))
        if self.returncode != 0:
            raise self.CalledProcessError(
                self.returncode, command, output=self.stdout, stderr=self.stderr
            )
        return subprocess.CompletedProcess(
            command, self.returncode, stdout=self.stdout, stderr=self.stderr
        )

    @property
    def commands(self):
        return [command for command, _kwargs in self.calls]

    @property
    def kwargs(self):
        return [kwargs for _command, kwargs in self.calls]

    def install(self, monkeypatch):
        monkeypatch.setattr(py7zip_module, "subprocess", self)
        return self


class _ForwardingPath:
    """Delegate to the real ``os.path`` but answer ``exists`` from the fake."""

    def __init__(self, real_path, exists_fn):
        self._real_path = real_path
        self._exists_fn = exists_fn

    def exists(self, path):
        return self._exists_fn(path)

    def __getattr__(self, name):
        return getattr(self._real_path, name)


class _ForwardingOS:
    """Delegate to the real ``os`` but expose the overridden ``path``."""

    def __init__(self, real_os, path_proxy):
        self._real_os = real_os
        self.path = path_proxy

    def __getattr__(self, name):
        return getattr(self._real_os, name)


class FakeFileSystem:
    """Pin ``os.path.exists`` as seen from the wrapper's module namespace.

    ``setup()`` probes the filesystem and downloads a binary when the answer
    is no.  Tests use this to answer "already present" without writing
    anything, or to force the download branch on purpose.

    The override is installed on the wrapper's ``os`` binding only, so
    ``Path.exists()`` and everything outside ``py7zip.py7zip`` keep consulting
    the real filesystem.
    """

    def __init__(self, exists=True):
        self.exists_answer = exists
        self.probed = []

    def exists(self, path):
        self.probed.append(str(path))
        return self.exists_answer

    def install(self, monkeypatch):
        proxy = _ForwardingOS(
            py7zip_module.os, _ForwardingPath(py7zip_module.os.path, self.exists)
        )
        monkeypatch.setattr(py7zip_module, "os", proxy)
        return self
