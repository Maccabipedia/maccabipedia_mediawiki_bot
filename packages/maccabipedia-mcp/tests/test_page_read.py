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
                "searchinfo": {"totalhits": 42},
                "search": [
                    {"pageid": 10, "title": "מכבי תל אביב", "snippet": "found <span>here</span>"},
                    {"pageid": 20, "title": "מכבי חיפה", "snippet": "also <span>here</span>"},
                ],
            }
        },
    )
    result = client.search_pages("מכבי")
    assert result["total_hits"] == 42
    assert len(result["results"]) == 2
    assert result["results"][0]["pageid"] == 10
    assert result["results"][0]["title"] == "מכבי תל אביב"


@responses.activate
def test_search_pages_wraps_query_in_quotes(client):
    responses.get(API_URL, json={"query": {"searchinfo": {"totalhits": 0}, "search": []}})
    client.search_pages("שחקן מכבי")
    params = responses.calls[0].request.params
    assert params["srsearch"] == '"שחקן מכבי"'


@responses.activate
def test_search_pages_default_namespace_zero(client):
    responses.get(API_URL, json={"query": {"searchinfo": {"totalhits": 0}, "search": []}})
    client.search_pages("מכבי")
    params = responses.calls[0].request.params
    assert params["srnamespace"] == "0"


@responses.activate
def test_search_pages_with_namespace(client):
    responses.get(API_URL, json={"query": {"searchinfo": {"totalhits": 0}, "search": []}})
    client.search_pages("מכבי", namespace=3003)
    params = responses.calls[0].request.params
    assert params["srnamespace"] == "3003"


@responses.activate
def test_search_pages_namespace_none_searches_all(client):
    # namespace=None must send srnamespace=* (the MediaWiki wildcard that
    # spans every namespace, including custom ones like Maccabipedia's
    # ns=3000 songs). Verified against the live API before shipping.
    responses.get(API_URL, json={"query": {"searchinfo": {"totalhits": 0}, "search": []}})
    client.search_pages("מכבי", namespace=None)
    params = responses.calls[0].request.params
    assert params["srnamespace"] == "*"


@responses.activate
def test_search_pages_uses_srwhat_text(client):
    responses.get(API_URL, json={"query": {"searchinfo": {"totalhits": 0}, "search": []}})
    client.search_pages("אלי דרייגור")
    params = responses.calls[0].request.params
    assert params["srwhat"] == "text"


@responses.activate
def test_search_pages_autopaging(client):
    responses.get(
        API_URL,
        json={
            "query": {
                "searchinfo": {"totalhits": 3},
                "search": [
                    {"pageid": 1, "title": "מכבי תל אביב א", "snippet": ""},
                    {"pageid": 2, "title": "מכבי תל אביב ב", "snippet": ""},
                ],
            },
            "continue": {"sroffset": 2, "continue": "-||"},
        },
    )
    responses.get(
        API_URL,
        json={
            "query": {
                "searchinfo": {"totalhits": 3},
                "search": [{"pageid": 3, "title": "מכבי תל אביב ג", "snippet": ""}],
            }
        },
    )
    result = client.search_pages("מכבי תל אביב", limit=500)
    assert result["total_hits"] == 3
    assert len(result["results"]) == 3
    assert result["results"][2]["title"] == "מכבי תל אביב ג"
    assert responses.calls[1].request.params["sroffset"] == "2"


@responses.activate
def test_search_pages_limit_caps_results(client):
    responses.get(
        API_URL,
        json={
            "query": {
                "searchinfo": {"totalhits": 100},
                "search": [
                    {"pageid": i, "title": f"מכבי {i}", "snippet": ""} for i in range(10)
                ],
            },
            "continue": {"sroffset": 10, "continue": "-||"},
        },
    )
    result = client.search_pages("מכבי", limit=5)
    assert len(result["results"]) == 5
    assert len(responses.calls) == 1


@responses.activate
def test_search_pages_returns_error_on_api_error(client):
    responses.get(
        API_URL,
        json={"error": {"code": "srsearch-invalid", "info": "Invalid search term"}},
    )
    result = client.search_pages("מכבי")
    assert result["error"] is True
    assert result["code"] == "srsearch-invalid"
    assert result["message"] == "Invalid search term"


@responses.activate
def test_search_pages_returns_error_on_non_json(client):
    responses.get(
        API_URL,
        body="<html>Internal Server Error</html>",
        content_type="text/html",
    )
    result = client.search_pages("מכבי")
    assert result["error"] is True
    assert result["code"] == "non_json"
    assert "non-JSON" in result["message"]


@responses.activate
def test_search_pages_strips_embedded_quotes(client):
    responses.get(API_URL, json={"query": {"searchinfo": {"totalhits": 0}, "search": []}})
    client.search_pages('אבי כהן "קפטן"')
    params = responses.calls[0].request.params
    assert params["srsearch"] == '"אבי כהן קפטן"'


@responses.activate
def test_search_pages_breaks_on_stale_sroffset(client):
    # Pathological case: API keeps echoing the same sroffset without advancing.
    # The loop must break rather than spin forever.
    responses.get(
        API_URL,
        json={
            "query": {
                "searchinfo": {"totalhits": 999},
                "search": [{"pageid": 1, "title": "מכבי תל אביב", "snippet": ""}],
            },
            "continue": {"sroffset": 5, "continue": "-||"},
        },
    )
    responses.get(
        API_URL,
        json={
            "query": {
                "searchinfo": {"totalhits": 999},
                "search": [{"pageid": 2, "title": "מכבי חיפה", "snippet": ""}],
            },
            "continue": {"sroffset": 5, "continue": "-||"},
        },
    )
    result = client.search_pages("מכבי", limit=500)
    assert len(responses.calls) == 2
    assert len(result["results"]) == 2


@responses.activate
def test_search_pages_uses_formatversion_2(client):
    responses.get(API_URL, json={"query": {"searchinfo": {"totalhits": 0}, "search": []}})
    client.search_pages("מכבי")
    params = responses.calls[0].request.params
    assert params["formatversion"] == "2"


@responses.activate
def test_search_pages_missing_snippet_defaults_empty(client):
    responses.get(
        API_URL,
        json={
            "query": {
                "searchinfo": {"totalhits": 1},
                "search": [{"pageid": 1, "title": "מכבי תל אביב"}],
            }
        },
    )
    result = client.search_pages("מכבי")
    assert result["results"][0]["snippet"] == ""


@responses.activate
def test_search_pages_limit_over_500_caps_per_page_request(client):
    # MediaWiki's srlimit max is 500 — a limit of 1000 must fetch in two pages
    # of 500 each, not attempt a single srlimit=1000 call.
    responses.get(
        API_URL,
        json={
            "query": {
                "searchinfo": {"totalhits": 1000},
                "search": [{"pageid": i, "title": f"מכבי {i}", "snippet": ""} for i in range(500)],
            },
            "continue": {"sroffset": 500, "continue": "-||"},
        },
    )
    responses.get(
        API_URL,
        json={
            "query": {
                "searchinfo": {"totalhits": 1000},
                "search": [
                    {"pageid": 500 + i, "title": f"מכבי {500 + i}", "snippet": ""}
                    for i in range(500)
                ],
            }
        },
    )
    result = client.search_pages("מכבי", limit=1000)
    assert len(result["results"]) == 1000
    assert responses.calls[0].request.params["srlimit"] == "500"
    assert responses.calls[1].request.params["srlimit"] == "500"


@responses.activate
def test_search_pages_limit_zero_short_circuits(client):
    result = client.search_pages("מכבי", limit=0)
    assert result == {"total_hits": 0, "results": []}
    assert len(responses.calls) == 0


@responses.activate
def test_search_pages_breaks_on_empty_page(client):
    # API returns a continue block but an empty search array — should break.
    responses.get(
        API_URL,
        json={
            "query": {
                "searchinfo": {"totalhits": 10},
                "search": [{"pageid": 1, "title": "מכבי", "snippet": ""}],
            },
            "continue": {"sroffset": 1, "continue": "-||"},
        },
    )
    responses.get(
        API_URL,
        json={
            "query": {
                "searchinfo": {"totalhits": 10},
                "search": [],
            },
            "continue": {"sroffset": 2, "continue": "-||"},
        },
    )
    result = client.search_pages("מכבי", limit=500)
    assert len(responses.calls) == 2
    assert len(result["results"]) == 1


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
