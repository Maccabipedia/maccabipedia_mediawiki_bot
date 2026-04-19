from unittest.mock import MagicMock, patch

import pytest
import requests

from maccabistats.parse.maccabi_tlv_site import game_pages_provider
from maccabistats.parse.maccabi_tlv_site.game_pages_provider import (
    GamePageUnavailableError,
    _fetch_ok,
)


def _fake_response(status_code: int, content: bytes = b"<html></html>"):
    response = MagicMock()
    response.status_code = status_code
    response.content = content
    return response


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    """Make the retry backoff instant so tests stay fast."""
    monkeypatch.setattr(game_pages_provider.time, "sleep", lambda _seconds: None)


def test_fetch_ok_returns_content_on_200():
    with patch.object(game_pages_provider.requests, "get",
                      return_value=_fake_response(200, b"hello")) as mock_get:
        assert _fetch_ok("https://example.com/x") == b"hello"
    assert mock_get.call_count == 1


def test_fetch_ok_retries_on_500_then_succeeds():
    """The CI failure (24640051609) was a transient 500 — we must retry, not drop the game."""
    responses = [_fake_response(500), _fake_response(500), _fake_response(200, b"ok")]
    with patch.object(game_pages_provider.requests, "get",
                      side_effect=responses) as mock_get:
        assert _fetch_ok("https://example.com/flaky") == b"ok"
    assert mock_get.call_count == 3


def test_fetch_ok_raises_when_all_attempts_return_5xx():
    """If the page is still 5xx after retries we must fail loudly, not silently skip."""
    with patch.object(game_pages_provider.requests, "get",
                      return_value=_fake_response(500)) as mock_get:
        with pytest.raises(GamePageUnavailableError, match=r"HTTP 500 after \d+ attempts"):
            _fetch_ok("https://example.com/broken")
    assert mock_get.call_count == game_pages_provider._MAX_FETCH_ATTEMPTS


def test_fetch_ok_does_not_retry_on_4xx():
    """4xx is a client/URL error — no point retrying, raise immediately."""
    with patch.object(game_pages_provider.requests, "get",
                      return_value=_fake_response(404)) as mock_get:
        with pytest.raises(GamePageUnavailableError, match=r"HTTP 404 for"):
            _fetch_ok("https://example.com/missing")
    assert mock_get.call_count == 1


def test_fetch_ok_retries_on_connection_error_then_succeeds():
    side_effects = [
        requests.exceptions.ConnectionError("boom"),
        _fake_response(200, b"recovered"),
    ]
    with patch.object(game_pages_provider.requests, "get",
                      side_effect=side_effects) as mock_get:
        assert _fetch_ok("https://example.com/net-flap") == b"recovered"
    assert mock_get.call_count == 2
