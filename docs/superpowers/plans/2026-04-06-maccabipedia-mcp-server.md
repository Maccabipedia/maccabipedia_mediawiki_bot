# Maccabipedia MCP Server Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a FastMCP server that provides 11 tools for reading/writing Maccabipedia wiki data via the MediaWiki HTTP API.

**Architecture:** A single FastMCP server (`src/maccabipedia_mcp/`) with 4 files: config, wiki HTTP client, server/tools, and entry point. Reads are unauthenticated. Writes use lazy login via MediaWiki bot API. All HTTP via `requests`.

**Tech Stack:** Python 3.11+, FastMCP, requests, pydantic

---

## File Map

| File | Responsibility |
|------|---------------|
| `src/maccabipedia_mcp/__init__.py` | Package marker |
| `src/maccabipedia_mcp/__main__.py` | Entry point: `mcp.run()` |
| `src/maccabipedia_mcp/config.py` | `Config` dataclass from env vars |
| `src/maccabipedia_mcp/wiki_client.py` | `WikiClient` class — all MediaWiki HTTP calls |
| `src/maccabipedia_mcp/server.py` | FastMCP app + 11 tool definitions |
| `tests/mcp/__init__.py` | Test package marker |
| `tests/mcp/conftest.py` | Shared fixtures (mock responses, WikiClient with mocked HTTP) |
| `tests/mcp/test_config.py` | Config loading tests |
| `tests/mcp/test_cargo.py` | Cargo tools tests |
| `tests/mcp/test_page_read.py` | Page read tools tests |
| `tests/mcp/test_page_write.py` | Page write tools tests |

---

### Task 1: Project setup — dependencies and package skeleton

**Files:**
- Modify: `pyproject.toml`
- Create: `src/maccabipedia_mcp/__init__.py`
- Create: `src/maccabipedia_mcp/__main__.py`

- [ ] **Step 1: Add fastmcp dependency to pyproject.toml**

Add `fastmcp` to the `dependencies` list in `pyproject.toml`:

```toml
dependencies = [
    "pydantic>=2.0",
    "mwparserfromhell==0.6.6",
    "pywikibot==9.6.0",
    "requests==2.32.3",
    "pandas==2.2.3",
    "lxml>=4.9.1,<5",
    "maccabistats>=2.50",
    "html5lib==1.1",
    "google-api-python-client==1.12.8",
    "google-auth-oauthlib==0.4.2",
    "beautifulsoup4>=4.9.3",
    "python-dotenv==0.15.0",
    "tldextract==5.3.0",
    "fastmcp>=2.0",
]
```

Also add `responses` to the dev dependencies for HTTP mocking:

```toml
[project.optional-dependencies]
dev = ["pytest>=8.0", "responses>=0.25"]
```

- [ ] **Step 2: Install dependencies**

Run: `uv sync --all-extras`
Expected: All dependencies install successfully, including `fastmcp` and `responses`.

- [ ] **Step 3: Create package skeleton**

Create `src/maccabipedia_mcp/__init__.py`:

```python
"""Maccabipedia MCP Server — MediaWiki API transport layer."""
```

Create `src/maccabipedia_mcp/__main__.py`:

```python
from maccabipedia_mcp.server import mcp

mcp.run()
```

- [ ] **Step 4: Create test package**

Create `tests/mcp/__init__.py`:

```python
```

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml src/maccabipedia_mcp/__init__.py src/maccabipedia_mcp/__main__.py tests/mcp/__init__.py
git commit -m "feat(mcp): add package skeleton and fastmcp dependency"
```

---

### Task 2: Config module

**Files:**
- Create: `src/maccabipedia_mcp/config.py`
- Create: `tests/mcp/test_config.py`

- [ ] **Step 1: Write the failing test**

Create `tests/mcp/test_config.py`:

```python
import os
from maccabipedia_mcp.config import Config


def test_config_from_env_defaults(monkeypatch):
    monkeypatch.delenv("MACCABIPEDIA_URL", raising=False)
    monkeypatch.delenv("MACCABIPEDIA_BOT_USERNAME", raising=False)
    monkeypatch.delenv("MACCABIPEDIA_BOT_PASSWORD", raising=False)
    cfg = Config.from_env()
    assert cfg.url == "https://www.maccabipedia.co.il"
    assert cfg.api_url == "https://www.maccabipedia.co.il/api.php"
    assert cfg.username is None
    assert cfg.password is None


def test_config_from_env_custom(monkeypatch):
    monkeypatch.setenv("MACCABIPEDIA_URL", "https://test.wiki.co.il")
    monkeypatch.setenv("MACCABIPEDIA_BOT_USERNAME", "bot_user")
    monkeypatch.setenv("MACCABIPEDIA_BOT_PASSWORD", "bot_pass")
    cfg = Config.from_env()
    assert cfg.url == "https://test.wiki.co.il"
    assert cfg.api_url == "https://test.wiki.co.il/api.php"
    assert cfg.username == "bot_user"
    assert cfg.password == "bot_pass"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/mcp/test_config.py -v`
Expected: FAIL — `ModuleNotFoundError` or `ImportError`

- [ ] **Step 3: Write the implementation**

Create `src/maccabipedia_mcp/config.py`:

```python
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    url: str
    username: str | None
    password: str | None

    @classmethod
    def from_env(cls) -> Config:
        return cls(
            url=os.environ.get("MACCABIPEDIA_URL", "https://www.maccabipedia.co.il"),
            username=os.environ.get("MACCABIPEDIA_BOT_USERNAME"),
            password=os.environ.get("MACCABIPEDIA_BOT_PASSWORD"),
        )

    @property
    def api_url(self) -> str:
        return f"{self.url}/api.php"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/mcp/test_config.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add src/maccabipedia_mcp/config.py tests/mcp/test_config.py
git commit -m "feat(mcp): add config module with env var loading"
```

---

### Task 3: WikiClient — Cargo tools

**Files:**
- Create: `src/maccabipedia_mcp/wiki_client.py`
- Create: `tests/mcp/conftest.py`
- Create: `tests/mcp/test_cargo.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/mcp/conftest.py`:

```python
import pytest
import responses

from maccabipedia_mcp.config import Config
from maccabipedia_mcp.wiki_client import WikiClient

WIKI_URL = "https://test.wiki.co.il"
API_URL = f"{WIKI_URL}/api.php"


@pytest.fixture
def config():
    return Config(url=WIKI_URL, username=None, password=None)


@pytest.fixture
def client(config):
    return WikiClient(config)
```

Create `tests/mcp/test_cargo.py`:

```python
import json
import responses

from tests.mcp.conftest import API_URL


@responses.activate
def test_list_cargo_tables(client):
    responses.get(
        API_URL,
        json={"cargotables": ["Football_Games", "Basketball_Games"]},
    )
    result = client.list_cargo_tables()
    assert result == ["Football_Games", "Basketball_Games"]


@responses.activate
def test_describe_cargo_table(client):
    responses.get(
        API_URL,
        json={"cargofields": {"Date": "Date", "Opponent": "String", "ResultMaccabi": "Integer"}},
    )
    result = client.describe_cargo_table("Football_Games")
    assert result == [
        {"name": "Date", "type": "Date"},
        {"name": "Opponent", "type": "String"},
        {"name": "ResultMaccabi", "type": "Integer"},
    ]


@responses.activate
def test_query_cargo(client):
    cargo_response = {
        "cargoquery": [
            {"title": {"_pageName": "Game1", "Date": "2025-01-01"}},
            {"title": {"_pageName": "Game2", "Date": "2025-01-02"}},
        ]
    }
    responses.get(API_URL, json=cargo_response)
    result = client.query_cargo(tables="Football_Games", fields="_pageName,Date")
    assert result == [
        {"_pageName": "Game1", "Date": "2025-01-01"},
        {"_pageName": "Game2", "Date": "2025-01-02"},
    ]


@responses.activate
def test_query_cargo_with_all_params(client):
    responses.get(API_URL, json={"cargoquery": []})
    client.query_cargo(
        tables="Football_Games",
        fields="_pageName",
        where="Date='2025-01-01'",
        join_on="",
        group_by="Season",
        having="COUNT(*)>1",
        order_by="Date ASC",
        limit=10,
        offset=5,
    )
    params = responses.calls[0].request.params
    assert params["tables"] == "Football_Games"
    assert params["fields"] == "_pageName"
    assert params["where"] == "Date='2025-01-01'"
    assert params["group_by"] == "Season"
    assert params["having"] == "COUNT(*)>1"
    assert params["order_by"] == "Date ASC"
    assert params["limit"] == "10"
    assert params["offset"] == "5"


@responses.activate
def test_query_cargo_html_error(client):
    responses.get(
        API_URL,
        body="<html>Internal Server Error</html>",
        content_type="text/html",
    )
    result = client.query_cargo(tables="Football_Games", fields="_pageName")
    assert result["error"] is True
    assert "non-JSON" in result["message"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/mcp/test_cargo.py -v`
Expected: FAIL — `ImportError` for `WikiClient`

- [ ] **Step 3: Write the WikiClient with Cargo methods**

Create `src/maccabipedia_mcp/wiki_client.py`:

```python
from __future__ import annotations

from typing import Any

import requests

from maccabipedia_mcp.config import Config


class WikiClient:
    def __init__(self, config: Config) -> None:
        self._config = config
        self._session = requests.Session()
        self._csrf_token: str | None = None

    @property
    def _api(self) -> str:
        return self._config.api_url

    def _get(self, params: dict[str, Any]) -> requests.Response:
        params.setdefault("format", "json")
        return self._session.get(self._api, params=params)

    def _check_json(self, resp: requests.Response) -> dict | None:
        content_type = resp.headers.get("Content-Type", "")
        if "application/json" not in content_type and "text/json" not in content_type:
            return {"error": True, "code": "non_json", "message": f"Cargo returned non-JSON response (Content-Type: {content_type})"}
        return None

    # -- Cargo tools --

    def list_cargo_tables(self) -> list[str] | dict:
        resp = self._get({"action": "cargotables"})
        err = self._check_json(resp)
        if err:
            return err
        return resp.json()["cargotables"]

    def describe_cargo_table(self, table: str) -> list[dict[str, str]] | dict:
        resp = self._get({"action": "cargofields", "table": table})
        err = self._check_json(resp)
        if err:
            return err
        fields = resp.json()["cargofields"]
        return [{"name": name, "type": ftype} for name, ftype in fields.items()]

    def query_cargo(
        self,
        tables: str,
        fields: str,
        where: str | None = None,
        join_on: str | None = None,
        group_by: str | None = None,
        having: str | None = None,
        order_by: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict] | dict:
        params: dict[str, Any] = {
            "action": "cargoquery",
            "tables": tables,
            "fields": fields,
            "limit": limit,
            "offset": offset,
        }
        if where:
            params["where"] = where
        if join_on:
            params["join_on"] = join_on
        if group_by:
            params["group_by"] = group_by
        if having:
            params["having"] = having
        if order_by:
            params["order_by"] = order_by

        resp = self._get(params)
        err = self._check_json(resp)
        if err:
            return err

        data = resp.json()
        return [row["title"] for row in data.get("cargoquery", [])]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/mcp/test_cargo.py -v`
Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add src/maccabipedia_mcp/wiki_client.py tests/mcp/conftest.py tests/mcp/test_cargo.py
git commit -m "feat(mcp): add WikiClient with Cargo query methods"
```

---

### Task 4: WikiClient — Page read tools

**Files:**
- Modify: `src/maccabipedia_mcp/wiki_client.py`
- Create: `tests/mcp/test_page_read.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/mcp/test_page_read.py`:

```python
import responses

from tests.mcp.conftest import API_URL


@responses.activate
def test_get_page_exists(client):
    responses.get(
        API_URL,
        json={
            "query": {
                "pages": {
                    "123": {
                        "pageid": 123,
                        "title": "Test Page",
                        "revisions": [{"*": "== Hello ==\nContent here"}],
                    }
                }
            }
        },
    )
    result = client.get_page("Test Page")
    assert result["exists"] is True
    assert result["title"] == "Test Page"
    assert result["wikitext"] == "== Hello ==\nContent here"
    assert result["redirect_target"] is None


@responses.activate
def test_get_page_missing(client):
    responses.get(
        API_URL,
        json={
            "query": {
                "pages": {
                    "-1": {
                        "title": "No Such Page",
                        "missing": "",
                    }
                }
            }
        },
    )
    result = client.get_page("No Such Page")
    assert result["exists"] is False
    assert result["wikitext"] == ""


@responses.activate
def test_get_page_redirect(client):
    responses.get(
        API_URL,
        json={
            "query": {
                "pages": {
                    "456": {
                        "pageid": 456,
                        "title": "Redirect Page",
                        "revisions": [{"*": "#הפניה [[Target Page]]"}],
                    }
                },
                "redirects": [{"from": "Redirect Page", "to": "Target Page"}],
            }
        },
    )
    result = client.get_page("Redirect Page")
    assert result["exists"] is True
    assert result["redirect_target"] == "Target Page"


@responses.activate
def test_page_exists_true(client):
    responses.get(
        API_URL,
        json={"query": {"pages": {"123": {"pageid": 123, "title": "X"}}}},
    )
    result = client.page_exists("X")
    assert result["exists"] is True


@responses.activate
def test_page_exists_false(client):
    responses.get(
        API_URL,
        json={"query": {"pages": {"-1": {"title": "X", "missing": ""}}}},
    )
    result = client.page_exists("X")
    assert result["exists"] is False


@responses.activate
def test_search_pages(client):
    responses.get(
        API_URL,
        json={
            "query": {
                "search": [
                    {"title": "Page A", "snippet": "found <span>here</span>"},
                    {"title": "Page B", "snippet": "also <span>here</span>"},
                ]
            }
        },
    )
    result = client.search_pages("test query")
    assert len(result) == 2
    assert result[0]["title"] == "Page A"


@responses.activate
def test_search_pages_with_namespace(client):
    responses.get(API_URL, json={"query": {"search": []}})
    client.search_pages("test", namespace=3003)
    params = responses.calls[0].request.params
    assert params["srnamespace"] == "3003"


@responses.activate
def test_list_category_pages(client):
    responses.get(
        API_URL,
        json={
            "query": {
                "categorymembers": [
                    {"title": "Game 1"},
                    {"title": "Game 2"},
                ]
            }
        },
    )
    result = client.list_category_pages("משחקים")
    assert result == ["Game 1", "Game 2"]


@responses.activate
def test_list_category_pages_adds_prefix(client):
    responses.get(API_URL, json={"query": {"categorymembers": []}})
    client.list_category_pages("משחקים")
    params = responses.calls[0].request.params
    assert params["cmtitle"] == "קטגוריה:משחקים"


@responses.activate
def test_list_category_pages_keeps_existing_prefix(client):
    responses.get(API_URL, json={"query": {"categorymembers": []}})
    client.list_category_pages("קטגוריה:משחקים")
    params = responses.calls[0].request.params
    assert params["cmtitle"] == "קטגוריה:משחקים"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/mcp/test_page_read.py -v`
Expected: FAIL — `AttributeError` for missing methods

- [ ] **Step 3: Add page read methods to WikiClient**

Add the following methods to `WikiClient` in `src/maccabipedia_mcp/wiki_client.py`:

```python
    # -- Page read tools --

    def get_page(self, title: str) -> dict:
        resp = self._get({
            "action": "query",
            "titles": title,
            "prop": "revisions",
            "rvprop": "content",
            "redirects": "1",
        })
        data = resp.json()
        pages = data["query"]["pages"]
        page = next(iter(pages.values()))

        if "missing" in page:
            return {"exists": False, "title": title, "wikitext": "", "redirect_target": None}

        redirect_target = None
        redirects = data["query"].get("redirects", [])
        for r in redirects:
            if r["from"] == title:
                redirect_target = r["to"]
                break

        wikitext = page.get("revisions", [{}])[0].get("*", "")
        return {
            "exists": True,
            "title": page["title"],
            "wikitext": wikitext,
            "redirect_target": redirect_target,
        }

    def page_exists(self, title: str) -> dict:
        resp = self._get({"action": "query", "titles": title})
        pages = resp.json()["query"]["pages"]
        page = next(iter(pages.values()))
        exists = "missing" not in page
        redirect = "redirect" in page
        return {"exists": exists, "redirect": redirect}

    def search_pages(self, query: str, namespace: int | None = None, limit: int = 10) -> list[dict]:
        params: dict[str, Any] = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srlimit": limit,
        }
        if namespace is not None:
            params["srnamespace"] = namespace
        resp = self._get(params)
        return [
            {"title": r["title"], "snippet": r["snippet"]}
            for r in resp.json()["query"]["search"]
        ]

    def list_category_pages(self, category: str, limit: int = 50) -> list[str]:
        if not category.startswith("קטגוריה:"):
            category = f"קטגוריה:{category}"
        resp = self._get({
            "action": "query",
            "list": "categorymembers",
            "cmtitle": category,
            "cmlimit": limit,
        })
        return [m["title"] for m in resp.json()["query"]["categorymembers"]]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/mcp/test_page_read.py -v`
Expected: 10 passed

- [ ] **Step 5: Commit**

```bash
git add src/maccabipedia_mcp/wiki_client.py tests/mcp/test_page_read.py
git commit -m "feat(mcp): add page read methods to WikiClient"
```

---

### Task 5: WikiClient — Auth and page write tools

**Files:**
- Modify: `src/maccabipedia_mcp/wiki_client.py`
- Create: `tests/mcp/test_page_write.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/mcp/test_page_write.py`:

```python
import pytest
import responses

from maccabipedia_mcp.config import Config
from maccabipedia_mcp.wiki_client import WikiClient

WIKI_URL = "https://test.wiki.co.il"
API_URL = f"{WIKI_URL}/api.php"


@pytest.fixture
def auth_config():
    return Config(url=WIKI_URL, username="bot_user", password="bot_pass")


@pytest.fixture
def auth_client(auth_config):
    return WikiClient(auth_config)


def _mock_login():
    """Register responses for the 3-step login flow."""
    # Step 1: get login token
    responses.get(
        API_URL,
        json={"query": {"tokens": {"logintoken": "abc123+\\"}}},
    )
    # Step 2: login with token
    responses.post(
        API_URL,
        json={"login": {"result": "Success", "lgusername": "bot_user"}},
    )
    # Step 3: get CSRF token
    responses.get(
        API_URL,
        json={"query": {"tokens": {"csrftoken": "csrf789+\\"}}},
    )


@responses.activate
def test_login_flow(auth_client):
    _mock_login()
    auth_client._ensure_authenticated()
    assert auth_client._csrf_token == "csrf789+\\"
    assert len(responses.calls) == 3


@responses.activate
def test_login_missing_credentials(client):
    """client fixture has no username/password."""
    result = client._ensure_authenticated()
    assert result["error"] is True
    assert "credentials" in result["message"].lower()


@responses.activate
def test_create_page_success(auth_client):
    _mock_login()
    responses.post(
        API_URL,
        json={"edit": {"result": "Success", "title": "New Page", "newrevid": 42}},
    )
    result = auth_client.create_page("New Page", "Page content", "Created page")
    assert result["success"] is True
    assert result["revid"] == 42

    # Verify createonly was sent
    body = responses.calls[-1].request.body
    assert "createonly" in body


@responses.activate
def test_create_page_already_exists(auth_client):
    _mock_login()
    responses.post(
        API_URL,
        json={"error": {"code": "articleexists", "info": "The article already exists"}},
    )
    result = auth_client.create_page("Existing Page", "text", "summary")
    assert result["error"] is True
    assert result["code"] == "articleexists"


@responses.activate
def test_edit_page_success(auth_client):
    _mock_login()
    responses.post(
        API_URL,
        json={"edit": {"result": "Success", "title": "Page", "newrevid": 43}},
    )
    result = auth_client.edit_page("Page", "New content", "Updated page")
    assert result["success"] is True

    body = responses.calls[-1].request.body
    assert "nocreate" in body


@responses.activate
def test_edit_page_missing(auth_client):
    _mock_login()
    responses.post(
        API_URL,
        json={"error": {"code": "missingtitle", "info": "The page does not exist"}},
    )
    result = auth_client.edit_page("Missing", "text", "summary")
    assert result["error"] is True
    assert result["code"] == "missingtitle"


@responses.activate
def test_purge_pages(client):
    """Purge does not require auth — uses client fixture (no credentials)."""
    responses.post(
        API_URL,
        json={"purge": [{"title": "A", "purged": ""}, {"title": "B", "purged": ""}]},
    )
    result = client.purge_pages(["A", "B"])
    assert len(result) == 2
    assert result[0]["title"] == "A"
    assert result[0]["purged"] is True


@responses.activate
def test_upload_file_success(auth_client, tmp_path):
    _mock_login()
    responses.post(
        API_URL,
        json={"upload": {"result": "Success", "filename": "test.jpg"}},
    )
    test_file = tmp_path / "test.jpg"
    test_file.write_bytes(b"\xff\xd8\xff\xe0fake jpeg")

    result = auth_client.upload_file("test.jpg", str(test_file), "{{template}}", "Upload comment")
    assert result["success"] is True
    assert result["filename"] == "test.jpg"


@responses.activate
def test_csrf_token_refresh_on_badtoken(auth_client):
    _mock_login()
    # First attempt: badtoken
    responses.post(
        API_URL,
        json={"error": {"code": "badtoken", "info": "Invalid CSRF token"}},
    )
    # Token refresh
    responses.get(
        API_URL,
        json={"query": {"tokens": {"csrftoken": "newtoken+\\"}}},
    )
    # Retry succeeds
    responses.post(
        API_URL,
        json={"edit": {"result": "Success", "title": "Page", "newrevid": 99}},
    )
    result = auth_client.create_page("Page", "text", "summary")
    assert result["success"] is True
    assert auth_client._csrf_token == "newtoken+\\"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/mcp/test_page_write.py -v`
Expected: FAIL — missing methods

- [ ] **Step 3: Add auth and write methods to WikiClient**

Add the following methods to `WikiClient` in `src/maccabipedia_mcp/wiki_client.py`:

```python
    def _post(self, data: dict[str, Any]) -> requests.Response:
        data.setdefault("format", "json")
        return self._session.post(self._api, data=data)

    # -- Auth --

    def _ensure_authenticated(self) -> dict | None:
        if self._csrf_token:
            return None
        if not self._config.username or not self._config.password:
            return {"error": True, "code": "no_credentials", "message": "No credentials configured — set MACCABIPEDIA_BOT_USERNAME and MACCABIPEDIA_BOT_PASSWORD"}

        # Step 1: get login token
        resp = self._get({"action": "query", "meta": "tokens", "type": "login"})
        login_token = resp.json()["query"]["tokens"]["logintoken"]

        # Step 2: login
        resp = self._post({
            "action": "login",
            "lgname": self._config.username,
            "lgpassword": self._config.password,
            "lgtoken": login_token,
        })
        login_result = resp.json().get("login", {})
        if login_result.get("result") != "Success":
            return {"error": True, "code": "login_failed", "message": f"Login failed: {login_result.get('reason', 'unknown')}"}

        # Step 3: get CSRF token
        self._fetch_csrf_token()
        return None

    def _fetch_csrf_token(self) -> None:
        resp = self._get({"action": "query", "meta": "tokens", "type": "csrf"})
        self._csrf_token = resp.json()["query"]["tokens"]["csrftoken"]

    def _do_edit(self, params: dict[str, Any], retry: bool = True) -> dict:
        auth_err = self._ensure_authenticated()
        if auth_err:
            return auth_err

        params["token"] = self._csrf_token
        params["action"] = "edit"
        resp = self._post(params)
        data = resp.json()

        if "error" in data:
            if data["error"]["code"] == "badtoken" and retry:
                self._fetch_csrf_token()
                return self._do_edit(params, retry=False)
            return {"error": True, "code": data["error"]["code"], "message": data["error"]["info"]}

        edit = data["edit"]
        return {"success": True, "title": edit["title"], "revid": edit.get("newrevid")}

    # -- Page write tools --

    def create_page(self, title: str, text: str, summary: str) -> dict:
        return self._do_edit({"title": title, "text": text, "summary": summary, "createonly": "1"})

    def edit_page(self, title: str, text: str, summary: str) -> dict:
        return self._do_edit({"title": title, "text": text, "summary": summary, "nocreate": "1"})

    def upload_file(self, filename: str, file_path: str, text: str, comment: str) -> dict:
        auth_err = self._ensure_authenticated()
        if auth_err:
            return auth_err

        with open(file_path, "rb") as f:
            file_data = f.read()

        resp = self._session.post(
            self._api,
            data={
                "action": "upload",
                "filename": filename,
                "comment": comment,
                "text": text,
                "token": self._csrf_token,
                "ignorewarnings": "1",
                "format": "json",
            },
            files={"file": (filename, file_data)},
        )
        data = resp.json()
        if "error" in data:
            return {"error": True, "code": data["error"]["code"], "message": data["error"]["info"]}
        upload = data["upload"]
        if upload.get("result") != "Success":
            return {"error": True, "code": "upload_failed", "message": f"Upload failed: {upload.get('result')}"}
        return {"success": True, "filename": upload["filename"]}

    def purge_pages(self, titles: list[str]) -> list[dict]:
        results = []
        # Batch in groups of 50
        for i in range(0, len(titles), 50):
            batch = titles[i:i + 50]
            resp = self._post({
                "action": "purge",
                "titles": "|".join(batch),
                "forcelinkupdate": "1",
            })
            for item in resp.json().get("purge", []):
                results.append({"title": item["title"], "purged": "purged" in item})
        return results
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/mcp/test_page_write.py -v`
Expected: 9 passed

- [ ] **Step 5: Run all tests**

Run: `uv run pytest tests/mcp/ -v`
Expected: All passed (config + cargo + page read + page write)

- [ ] **Step 6: Commit**

```bash
git add src/maccabipedia_mcp/wiki_client.py tests/mcp/test_page_write.py
git commit -m "feat(mcp): add auth flow and page write methods to WikiClient"
```

---

### Task 6: FastMCP server with all 11 tools

**Files:**
- Create: `src/maccabipedia_mcp/server.py`
- Modify: `src/maccabipedia_mcp/__main__.py` (already created in Task 1, verify it works)

- [ ] **Step 1: Write the server module**

Create `src/maccabipedia_mcp/server.py`:

```python
from __future__ import annotations

from fastmcp import FastMCP

from maccabipedia_mcp.config import Config
from maccabipedia_mcp.wiki_client import WikiClient

mcp = FastMCP("Maccabipedia")

_config = Config.from_env()
_client = WikiClient(_config)


# -- Cargo tools --


@mcp.tool
def list_cargo_tables() -> list[str] | dict:
    """List all Cargo tables available on Maccabipedia."""
    return _client.list_cargo_tables()


@mcp.tool
def describe_cargo_table(table: str) -> list[dict[str, str]] | dict:
    """Describe columns and types for a Cargo table."""
    return _client.describe_cargo_table(table)


@mcp.tool
def query_cargo(
    tables: str,
    fields: str,
    where: str | None = None,
    join_on: str | None = None,
    group_by: str | None = None,
    having: str | None = None,
    order_by: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[dict] | dict:
    """Query Cargo data. Params mirror the MediaWiki cargoquery API."""
    return _client.query_cargo(
        tables=tables, fields=fields, where=where, join_on=join_on,
        group_by=group_by, having=having, order_by=order_by,
        limit=limit, offset=offset,
    )


# -- Page read tools --


@mcp.tool
def get_page(title: str) -> dict:
    """Get raw wikitext and metadata for a page."""
    return _client.get_page(title)


@mcp.tool
def page_exists(title: str) -> dict:
    """Check if a page exists (lightweight, no content fetched)."""
    return _client.page_exists(title)


@mcp.tool
def search_pages(query: str, namespace: int | None = None, limit: int = 10) -> list[dict]:
    """Full-text search across the wiki."""
    return _client.search_pages(query, namespace=namespace, limit=limit)


@mcp.tool
def list_category_pages(category: str, limit: int = 50) -> list[str]:
    """List pages in a category. Prefix 'קטגוריה:' is added automatically if missing."""
    return _client.list_category_pages(category, limit=limit)


# -- Page write tools --


@mcp.tool
def create_page(title: str, text: str, summary: str) -> dict:
    """Create a new wiki page. Fails if page already exists."""
    return _client.create_page(title, text, summary)


@mcp.tool
def edit_page(title: str, text: str, summary: str) -> dict:
    """Edit an existing wiki page. Fails if page does not exist."""
    return _client.edit_page(title, text, summary)


@mcp.tool
def upload_file(filename: str, file_path: str, text: str, comment: str) -> dict:
    """Upload a file to the wiki."""
    return _client.upload_file(filename, file_path, text, comment)


@mcp.tool
def purge_pages(titles: list[str]) -> list[dict]:
    """Purge pages to refresh cache and Cargo data."""
    return _client.purge_pages(titles)
```

- [ ] **Step 2: Verify the module imports cleanly**

Run: `uv run python -c "from maccabipedia_mcp.server import mcp; print(f'Server: {mcp.name}, Tools: {len(mcp._tool_manager._tools)}')"`
Expected: `Server: Maccabipedia, Tools: 11`

Note: The exact attribute path for counting tools may differ — the important thing is no import errors. If the count check fails, just verify the import works.

- [ ] **Step 3: Verify __main__ entry point**

Run: `timeout 3 uv run python -m maccabipedia_mcp 2>&1 || true`
Expected: The server starts and either waits for stdio input or prints a startup message. It should not crash with an import error.

- [ ] **Step 4: Run all tests**

Run: `uv run pytest tests/mcp/ -v`
Expected: All tests pass

- [ ] **Step 5: Commit**

```bash
git add src/maccabipedia_mcp/server.py
git commit -m "feat(mcp): add FastMCP server with all 11 tools"
```

---

### Task 7: Configuration — .mcp.json and settings.json

**Files:**
- Modify: `.mcp.json`
- Modify: `.claude/settings.json`

- [ ] **Step 1: Read current .mcp.json**

Read `.mcp.json` to see current MCP server entries.

- [ ] **Step 2: Add maccabipedia server to .mcp.json**

Add the `maccabipedia` entry to the existing `mcpServers` object in `.mcp.json`:

```json
{
  "mcpServers": {
    "maccabipedia": {
      "command": "uv",
      "args": ["run", "python", "-m", "maccabipedia_mcp"],
      "env": {
        "MACCABIPEDIA_BOT_USERNAME": "",
        "MACCABIPEDIA_BOT_PASSWORD": ""
      }
    }
  }
}
```

Keep existing YouTube and Trello entries. Leave username/password empty — they'll be filled in by the user (or sourced from existing secrets).

- [ ] **Step 3: Read current settings.json**

Read `.claude/settings.json` to see current permissions.

- [ ] **Step 4: Add read tool permissions to settings.json**

Add the 7 read-only MCP tool permissions to the existing `allow` list:

```json
"mcp__maccabipedia__list_cargo_tables",
"mcp__maccabipedia__describe_cargo_table",
"mcp__maccabipedia__query_cargo",
"mcp__maccabipedia__get_page",
"mcp__maccabipedia__page_exists",
"mcp__maccabipedia__search_pages",
"mcp__maccabipedia__list_category_pages",
"mcp__maccabipedia__purge_pages"
```

Note: `purge_pages` is also auto-allowed since it doesn't require auth.

- [ ] **Step 5: Commit**

```bash
git add .mcp.json .claude/settings.json
git commit -m "chore(mcp): configure maccabipedia MCP server and permissions"
```

---

### Task 8: Smoke test against live wiki

This task is manual verification — run the MCP server tools against the real Maccabipedia wiki to confirm everything works end-to-end.

- [ ] **Step 1: Start Claude Code with the new MCP server**

Restart Claude Code so it picks up the new `.mcp.json` entry. Verify the server starts without errors.

- [ ] **Step 2: Test Cargo tools**

Use the MCP tools from Claude Code:
1. Call `list_cargo_tables` — verify it returns ~57 table names
2. Call `describe_cargo_table` with `Football_Games` — verify it returns fields like `Date`, `Opponent`, `ResultMaccabi`
3. Call `query_cargo` with `tables=Football_Games`, `fields=_pageName,Date,Opponent`, `limit=3` — verify it returns 3 game records

- [ ] **Step 3: Test page read tools**

1. Call `get_page` with a known page (e.g. `עונת 2024/25`) — verify wikitext is returned
2. Call `page_exists` with a real and a fake page title
3. Call `search_pages` with `מכבי` — verify results
4. Call `list_category_pages` with `משחקים` — verify game pages listed

- [ ] **Step 4: Test write tools (with auth configured)**

1. Call `purge_pages` with `["עונת 2024/25"]` — verify purge succeeds (no auth needed)
2. If auth is configured: call `create_page` with a test page in a sandbox namespace, then `edit_page` to modify it

- [ ] **Step 5: Commit any fixes**

If any issues were found and fixed, commit the fixes.
