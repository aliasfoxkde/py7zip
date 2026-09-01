"""Characterisation of archive execution as it exists today.

``Py7zip.wrapper`` interpolates the binary name, source, destination and
caller-supplied options into a single string and hands it to
``subprocess.run(..., shell=True)``.  These tests pin that behaviour from both
directions:

* against a recording process seam, to capture the exact shell string and the
  ``subprocess.run`` keyword arguments; and
* against a real ``/bin/sh`` running a harmless stand-in script, to prove what
  the shell actually does with the string it receives.

The stand-in script only writes its own argv to a file in the test's
temporary directory.  Nothing outside that directory is created or modified,
and no network access takes place.
"""

from __future__ import annotations

import inspect
import os

import pytest

import py7zip.py7zip as py7zip_module
from tests.fakes import FakeSubprocess

POSIX = pytest.mark.skipif(
    os.name != "posix",
    reason="characterises the /bin/sh -c behaviour of shell=True on POSIX hosts",
)

RECORDING_SCRIPT = """\
#!/bin/sh
printf '%s\\n' "$@" >> "$PY7ZIP_ARGV_FILE"
"""


@pytest.fixture
def recording_7za(tmp_path, monkeypatch):
    """Put a stand-in ``7za`` on PATH that records the argv the shell gave it."""
    bindir = tmp_path / "bin"
    bindir.mkdir()
    script = bindir / "7za"
    script.write_text(RECORDING_SCRIPT, encoding="utf-8")
    script.chmod(0o755)
    argv_file = tmp_path / "argv.txt"
    monkeypatch.setenv("PY7ZIP_ARGV_FILE", str(argv_file))
    monkeypatch.setenv("PATH", f"{bindir}{os.pathsep}{os.environ.get('PATH', '')}")
    return argv_file


@pytest.fixture
def argv_seen(recording_7za):
    def read():
        if not recording_7za.exists():
            return []
        return recording_7za.read_text(encoding="utf-8").splitlines()

    return read


def test_decompress_builds_the_extract_command_string(make_wrapper, monkeypatch):
    runner = FakeSubprocess().install(monkeypatch)

    wrapper = make_wrapper()
    wrapper.wrapper("/data/input.7z", "/data/out", options="", method="decompress")

    assert runner.commands == ['"7za" x "/data/input.7z" -o"/data/out" ']
    assert runner.kwargs == [
        {"shell": True, "check": True, "capture_output": True, "text": True}
    ]


def test_compress_builds_the_add_command_string(make_wrapper, monkeypatch):
    runner = FakeSubprocess().install(monkeypatch)

    wrapper = make_wrapper()
    wrapper.wrapper("/data/input.7z", "/data/out.7z", options="", method="compress")

    assert runner.commands == ['"7za" a "/data/out.7z" "/data/input.7z" ']
    assert runner.kwargs[0]["shell"] is True


def test_compress_puts_the_destination_before_the_source(make_wrapper, monkeypatch):
    runner = FakeSubprocess().install(monkeypatch)

    wrapper = make_wrapper()
    wrapper.wrapper("SRC", "DST", options="", method="compress")

    assert runner.commands == ['"7za" a "DST" "SRC" ']


def test_options_are_appended_verbatim_to_the_command_string(make_wrapper, monkeypatch):
    runner = FakeSubprocess().install(monkeypatch)

    wrapper = make_wrapper()
    wrapper.wrapper("src", "dst", options="-y -aoa", method="decompress")

    assert runner.commands == ['"7za" x "src" -o"dst" -y -aoa']


def test_windows_command_uses_the_executable_suffix(make_wrapper, monkeypatch):
    runner = FakeSubprocess().install(monkeypatch)

    wrapper = make_wrapper(
        system="Windows", machine="AMD64", architecture=("64bit", "WindowsPE")
    )
    wrapper.wrapper("src", "dst", options="", method="compress")

    assert runner.commands == ['"7za.exe" a "dst" "src" ']


def test_wrapper_returns_none_on_success(make_wrapper, monkeypatch):
    FakeSubprocess().install(monkeypatch)

    wrapper = make_wrapper()

    assert wrapper.wrapper("src", "dst", method="decompress") is None


def test_wrapper_returns_none_on_failure(make_wrapper, monkeypatch):
    FakeSubprocess(returncode=2, stderr="cannot open file").install(monkeypatch)

    wrapper = make_wrapper()

    assert wrapper.wrapper("src", "dst", method="decompress") is None


def test_wrapper_swallows_the_nonzero_exit_instead_of_raising(
    make_wrapper, monkeypatch
):
    """A failing archive operation is indistinguishable from a successful one."""
    FakeSubprocess(returncode=2, stderr="Cannot open the file as archive").install(
        monkeypatch
    )

    wrapper = make_wrapper()

    try:
        wrapper.wrapper("missing.7z", "dst", method="decompress")
    except Exception as exc:
        raise AssertionError(f"wrapper raised {exc!r} instead of returning") from exc


def test_stdout_is_printed_only_in_debug_and_verbose_modes(
    make_wrapper, monkeypatch, capsys
):
    runner = FakeSubprocess(stdout="Everything is Ok").install(monkeypatch)

    wrapper = make_wrapper()
    wrapper.wrapper("src", "dst", method="decompress")

    assert capsys.readouterr().out == ""

    wrapper.debug = True
    wrapper.wrapper("src", "dst", method="decompress")
    assert "Everything is Ok" in capsys.readouterr().out

    wrapper.verbose = True
    wrapper.wrapper("src", "dst", method="decompress")
    assert "Extracted archive from 'src' to 'dst'" in capsys.readouterr().out
    assert runner.commands != []


def test_stderr_is_printed_only_in_debug_and_verbose_modes(
    make_wrapper, monkeypatch, capsys
):
    FakeSubprocess(returncode=2, stderr="Broken archive").install(monkeypatch)

    wrapper = make_wrapper()
    wrapper.wrapper("src", "dst", method="decompress")

    assert capsys.readouterr().out == ""

    wrapper.debug = True
    wrapper.wrapper("src", "dst", method="decompress")
    assert "Broken archive" in capsys.readouterr().out

    wrapper.verbose = True
    wrapper.wrapper("src", "dst", method="decompress")
    assert "Failed to create backup from 'src' to 'dst'." in capsys.readouterr().out


@POSIX
def test_the_shell_word_splits_the_options_string(make_wrapper, argv_seen):
    """Options are not passed as one argument: the shell tokenises them."""
    wrapper = make_wrapper()
    wrapper.wrapper("src.7z", "out", options="m0=on m1=off", method="decompress")

    assert argv_seen() == ["x", "src.7z", "-oout", "m0=on", "m1=off"]


@POSIX
def test_quoted_paths_survive_spaces_in_the_destination(make_wrapper, argv_seen):
    wrapper = make_wrapper()
    wrapper.wrapper("src.7z", "out put dir", options="-y", method="decompress")

    assert argv_seen() == ["x", "src.7z", "-oout put dir", "-y"]


@POSIX
def test_options_are_evaluated_by_the_shell(make_wrapper, argv_seen):
    """Command substitution inside ``options`` is executed, not escaped."""
    wrapper = make_wrapper()
    wrapper.wrapper(
        "src.7z", "out", options="m0=$(printf INJECTED)", method="decompress"
    )

    assert argv_seen() == ["x", "src.7z", "-oout", "m0=INJECTED"]


@POSIX
def test_options_can_run_additional_commands(make_wrapper, monkeypatch, tmp_path):
    """A semicolon in ``options`` reaches the shell and starts a new command."""
    side_effect = tmp_path / "arbitrary-command-ran"
    monkeypatch.setenv("PY7ZIP_SIDE_EFFECT", str(side_effect))

    wrapper = make_wrapper()
    wrapper.wrapper(
        "src.7z",
        "out",
        options='m0=on; : > "$PY7ZIP_SIDE_EFFECT"',
        method="decompress",
    )

    assert side_effect.exists(), "the shell executed a second command from options"


@POSIX
def test_compress_argv_order_seen_by_the_shell(make_wrapper, argv_seen):
    wrapper = make_wrapper()
    wrapper.wrapper("my data", "backup.7z", options="-mx=9", method="compress")

    assert argv_seen() == ["a", "backup.7z", "my data", "-mx=9"]


def test_aliases_forward_to_the_wrapper_as_decompress(make_wrapper, monkeypatch):
    runner = FakeSubprocess().install(monkeypatch)

    wrapper = make_wrapper()
    wrapper.decompress("src.7z", "out")
    wrapper.extract("src.7z", "out")

    assert runner.commands == [
        '"7za" x "src.7z" -o"out" ',
        '"7za" x "src.7z" -o"out" ',
    ]


def test_aliases_forward_to_the_wrapper_as_compress(make_wrapper, monkeypatch):
    runner = FakeSubprocess().install(monkeypatch)

    wrapper = make_wrapper()
    wrapper.compress("src", "dst.7z")
    wrapper.archive("src", "dst.7z")
    wrapper.backup("src", "dst.7z")

    assert runner.commands == [
        '"7za" a "dst.7z" "src" ',
        '"7za" a "dst.7z" "src" ',
        '"7za" a "dst.7z" "src" ',
    ]


def test_legacy_aliases_forward_the_callers_options(make_wrapper, monkeypatch):
    """Compatibility aliases preserve options instead of silently dropping them."""
    runner = FakeSubprocess().install(monkeypatch)

    wrapper = make_wrapper()
    wrapper.extract("src.7z", "out", options="-y")
    wrapper.compress("src", "dst.7z", options="-mx=9")

    assert runner.commands == [
        '"7za" x "src.7z" -o"out" -y',
        '"7za" a "dst.7z" "src" -mx=9',
    ]


def test_only_wrapper_honours_options(make_wrapper, monkeypatch):
    runner = FakeSubprocess().install(monkeypatch)

    wrapper = make_wrapper()
    wrapper.wrapper("src.7z", "out", options="-y", method="decompress")

    assert runner.commands == ['"7za" x "src.7z" -o"out" -y']


def test_paths_are_not_validated_before_execution(make_wrapper, monkeypatch):
    runner = FakeSubprocess().install(monkeypatch)

    wrapper = make_wrapper()
    wrapper.wrapper("/no/such/archive.7z", "/no/such/../destination", options="")

    assert runner.commands == [
        '"7za" x "/no/such/archive.7z" -o"/no/such/../destination" '
    ]


@pytest.mark.parametrize("name", ["full", "incremental", "differential", "snapshot"])
def test_snapshot_family_methods_do_nothing(make_wrapper, monkeypatch, name):
    runner = FakeSubprocess().install(monkeypatch)

    wrapper = make_wrapper()
    result = getattr(wrapper, name)("src", "dst", options="-y")

    assert result is None
    assert runner.commands == []


@pytest.mark.parametrize("name", ["full", "incremental", "differential", "snapshot"])
def test_snapshot_family_methods_accept_the_shared_signature(name):
    """All four are public-looking methods with the wrapper's signature."""
    method = getattr(py7zip_module.Py7zip, name)

    assert list(inspect.signature(method).parameters) == [
        "self",
        "src",
        "dst",
        "options",
    ]


def test_every_public_alias_funnels_through_wrapper(make_wrapper, monkeypatch):
    """``wrapper`` is the single execution path behind the five aliases."""
    runner = FakeSubprocess().install(monkeypatch)

    wrapper = make_wrapper()
    public = ["decompress", "extract", "compress", "archive", "backup"]
    for name in public:
        getattr(wrapper, name)("SRC", "DST")

    assert len(runner.commands) == len(public)
    expected = {"shell": True, "check": True, "capture_output": True, "text": True}
    assert all(kwargs == expected for kwargs in runner.kwargs)


def test_cd_is_a_process_global_side_effect(monkeypatch, tmp_path, clean_cwd):
    target = tmp_path / "elsewhere"
    target.mkdir()

    py7zip_module.Py7zip.cd(str(target))

    assert os.getcwd() == str(target)


def test_cd_is_callable_on_the_class_without_an_instance(tmp_path, clean_cwd):
    original = os.getcwd()
    target = tmp_path / "static-target"
    target.mkdir()

    try:
        py7zip_module.Py7zip.cd(str(target))
        assert os.getcwd() == str(target)
    finally:
        os.chdir(original)
