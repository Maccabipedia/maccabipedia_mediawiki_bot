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
