"""Characterisation of the runtime version probe as it exists today.

``Py7zip.get_version`` fetches ``docs/CHANGELOG.md`` over HTTP on every
construction and falls back to the string ``"0.0.0"`` whenever the fetch or
the parse fails.  These tests pin that contract, including the failure modes,
so the Phase 1 removal of the network probe is a documented, observable break
rather than a silent one.
"""

from __future__ import annotations

import pytest

import requests

from tests.fakes import FakeRequests, make_response

CHANGELOG_URL = (
    "https://raw.githubusercontent.com/aliasfoxkde/py7zip/main/docs/CHANGELOG.md"
)

#: Real changelog text shaped like the project's own file, so the regular
#: expression is exercised against data the wrapper would actually see.
CHANGELOG_BODY = """\
## CHANGELOG
- 0.7.3 - Functional Improvements
  - Updated platform check to account for additional cases

- 0.6.2 - Debugging
  - Resolved various issues with wrapper
"""

OLDER_BODY = """\
## CHANGELOG
- 0.6.2 - Debugging
  - Resolved various issues with wrapper
"""


def _responder_for(body, status=200):
    def responder(url, **_kwargs):
        return make_response(body, status=status, url=url)

    return responder


def test_probe_makes_a_single_untuned_get_request(make_wrapper):
    """The probe is a bare ``requests.get(url)`` with no options at all."""
    kwargs_seen = []

    def responder(url, **kwargs):
        kwargs_seen.append(kwargs)
        return make_response(CHANGELOG_BODY, url=url)

    wrapper = make_wrapper(requests_responder=responder)

    assert wrapper.__version__ == "0.7.3"
    assert wrapper._requests_fake.calls == [CHANGELOG_URL]
    assert kwargs_seen == [{}]


def test_version_is_parsed_from_the_first_bullet_entry(make_wrapper):
    wrapper = make_wrapper(requests_responder=_responder_for(CHANGELOG_BODY))

    assert wrapper.__version__ == "0.7.3"


def test_version_tracks_the_head_of_the_changelog(make_wrapper):
    wrapper = make_wrapper(requests_responder=_responder_for(OLDER_BODY))

    assert wrapper.__version__ == "0.6.2"


def test_version_requires_a_leading_bullet(make_wrapper):
    """A heading-only changelog does not match the regex and yields 0.0.0."""
    body = "## CHANGELOG\n# 0.7.3 - Functional Improvements\n"

    wrapper = make_wrapper(requests_responder=_responder_for(body))

    assert wrapper.__version__ == "0.0.0"


def test_version_falls_back_when_the_changelog_is_unparseable(make_wrapper):
    wrapper = make_wrapper(requests_responder=_responder_for("no version here"))

    assert wrapper.__version__ == "0.0.0"


def test_version_falls_back_on_an_http_error_status(make_wrapper):
    wrapper = make_wrapper(requests_responder=_responder_for(CHANGELOG_BODY, status=404))

    assert wrapper.__version__ == "0.0.0"


def test_version_falls_back_when_the_connection_fails(make_wrapper):
    def refused(url):
        raise requests.ConnectionError("offline characterization run")

    wrapper = make_wrapper(requests_responder=refused)

    assert wrapper.__version__ == "0.0.0"


def test_version_falls_back_on_a_timeout(make_wrapper):
    def slow(url):
        raise requests.Timeout("characterization timeout")

    wrapper = make_wrapper(requests_responder=slow)

    assert wrapper.__version__ == "0.0.0"


def test_version_probe_has_no_timeout_of_its_own(make_wrapper):
    """The wrapper passes no timeout to ``requests.get``.

    A missing timeout means the probe can hang indefinitely; recorded here so
    the removal in Phase 1 is measurable.
    """
    observed = {}

    def responder(url):
        observed["requests_made"] = True
        return make_response(CHANGELOG_BODY, url=url)

    wrapper = make_wrapper(requests_responder=responder)

    assert wrapper.__version__ == "0.7.3"
    assert observed["requests_made"] is True


def test_verbose_output_is_only_requested_explicitly(make_wrapper, capsys):
    """``get_version(verbose=True)`` prints, but ``__init__`` never passes it."""
    wrapper = make_wrapper(requests_responder=_responder_for(CHANGELOG_BODY))

    assert wrapper.__version__ == "0.7.3"
    assert capsys.readouterr().out == ""

    wrapper.get_version(verbose=True)

    assert "Latest version found in CHANGELOG.md: 0.7.3" in capsys.readouterr().out


def test_failed_probe_prints_when_verbose(make_wrapper, capsys):
    wrapper = make_wrapper()

    assert wrapper.__version__ == "0.0.0"

    wrapper.get_version(verbose=True)

    captured = capsys.readouterr().out
    assert "Error fetching CHANGELOG.md" in captured
    assert "offline characterization run" in captured
