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
