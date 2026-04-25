"""Fixtures for the local-wiki integration suite.

Hits the running docker stack (default http://localhost:8080) and exposes
anonymous / admin / Maccabipedia-skin HTML bodies of the Hebrew main page.
All fixtures are session-scoped so the suite makes minimal HTTP calls.

Shared constants (`MENU_LABELS`, `PHP_ERROR_RE`) live in
`skin_test_constants.py` (a uniquely-named module that doesn't collide
with the monorepo's other `conftest.py`s).
"""
from __future__ import annotations

import os
from urllib.parse import quote

import pytest
import requests

# "עמוד ראשי" — Hebrew main page title, used by the local stack's MW config.
# MediaWiki canonicalises spaces to underscores in titles before percent-encoding,
# so we mirror that here (otherwise the URL hits a 404 instead of the article).
_MAIN_PAGE_TITLE = "עמוד_ראשי"
_ADMIN_USERNAME = "admin"
_ADMIN_PASSWORD = "devadminpass"  # see infra/local-wiki/docker-compose.yml


@pytest.fixture(scope="session")
def base_url() -> str:
    """Base URL of the wiki under test; override via MACCABIPEDIA_LOCAL_URL."""
    return os.environ.get("MACCABIPEDIA_LOCAL_URL", "http://localhost:8080").rstrip("/")


@pytest.fixture(scope="session")
def main_url(base_url: str) -> str:
    """Percent-encoded URL of the Hebrew main page.

    Local stack now serves pretty URLs ($wgArticlePath = /$1) to match prod,
    so the /index.php/ segment is gone.
    """
    return f"{base_url}/{quote(_MAIN_PAGE_TITLE)}"


@pytest.fixture(scope="session")
def anon_html(main_url: str) -> str:
    """GET the main page with no cookies and return the response body."""
    response = requests.get(main_url, timeout=15)
    assert response.status_code == 200, (
        f"Anonymous GET {main_url} returned HTTP {response.status_code}"
    )
    return response.text


@pytest.fixture(scope="session")
def admin_session(base_url: str) -> requests.Session:
    """A requests.Session logged in as the local admin via action=login.

    Skips cleanly when the API is unreachable or the credentials are rejected,
    so the test suite stays useful even on a partially-up stack.
    """
    session = requests.Session()
    api_url = f"{base_url}/api.php"

    try:
        token_response = session.get(
            api_url,
            params={
                "action": "query",
                "meta": "tokens",
                "type": "login",
                "format": "json",
            },
            timeout=15,
        )
    except requests.RequestException as exc:
        pytest.skip(f"login token request failed: {exc}")

    login_token = token_response.json().get("query", {}).get("tokens", {}).get("logintoken")
    if not login_token:
        pytest.skip(f"couldn't fetch login token (response: {token_response.text})")

    login_response = session.post(
        api_url,
        data={
            "action": "login",
            "lgname": _ADMIN_USERNAME,
            "lgpassword": _ADMIN_PASSWORD,
            "lgtoken": login_token,
            "format": "json",
        },
        timeout=15,
    )
    result = login_response.json().get("login", {}).get("result")
    if result != "Success":
        pytest.skip(f"admin login failed (API result: {login_response.text})")

    return session


@pytest.fixture(scope="session")
def admin_html(admin_session: requests.Session, main_url: str) -> str:
    """GET the main page with the admin session cookie and return the body."""
    response = admin_session.get(main_url, timeout=15)
    assert response.status_code == 200, (
        f"Admin GET {main_url} returned HTTP {response.status_code}"
    )
    return response.text


@pytest.fixture(scope="session")
def maccabipedia_anon_html(anon_html: str) -> str:
    """Maccabipedia is now the default skin — alias of `anon_html`.
    Kept as a fixture so `test_maccabipedia_scaffold.py` stays self-documenting
    when read in isolation."""
    return anon_html
