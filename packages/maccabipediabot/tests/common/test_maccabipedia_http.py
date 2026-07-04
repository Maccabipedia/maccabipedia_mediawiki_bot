"""The maccabipedia Imunify360 WAF 415s the default wildcard ``Accept: */*``, so every
request to the wiki must carry a concrete Accept. Guard that the shared session sets it."""
from maccabipediabot.common.maccabipedia_http import (
    MACCABIPEDIA_JSON_HEADERS,
    build_maccabipedia_session,
)


def test_json_headers_are_not_wildcard():
    assert MACCABIPEDIA_JSON_HEADERS == {"Accept": "application/json"}


def test_session_sends_concrete_accept_header():
    session = build_maccabipedia_session()
    accept = session.headers.get("Accept")
    assert accept == "application/json"
    assert accept != "*/*"


def test_session_retries_on_edge_415():
    session = build_maccabipedia_session()
    adapter = session.get_adapter("https://www.maccabipedia.co.il")
    assert 415 in adapter.max_retries.status_forcelist
