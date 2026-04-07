import responses

WIKI_URL = "https://test.wiki.co.il"
API_URL = f"{WIKI_URL}/api.php"


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
    assert result["pageid"] == 123
    assert result["ns"] is None  # not in mock response
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
    assert result["pageid"] is None
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
    assert result["pageid"] == 123


@responses.activate
def test_page_exists_false(client):
    responses.get(
        API_URL,
        json={"query": {"pages": {"-1": {"title": "X", "missing": ""}}}},
    )
    result = client.page_exists("X")
    assert result["exists"] is False
    assert result["pageid"] is None


@responses.activate
def test_search_pages(client):
    responses.get(
        API_URL,
        json={
            "query": {
                "search": [
                    {"pageid": 10, "title": "Page A", "snippet": "found <span>here</span>"},
                    {"pageid": 20, "title": "Page B", "snippet": "also <span>here</span>"},
                ]
            }
        },
    )
    result = client.search_pages("test query")
    assert len(result) == 2
    assert result[0]["pageid"] == 10
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
                    {"pageid": 1, "ns": 0, "title": "Game 1", "type": "page"},
                    {"pageid": 2, "ns": 0, "title": "Game 2", "type": "page"},
                ]
            }
        },
    )
    result = client.list_category_pages("משחקים")
    assert len(result) == 2
    assert result[0] == {"pageid": 1, "ns": 0, "title": "Game 1", "type": "page"}
    assert result[1]["title"] == "Game 2"


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
