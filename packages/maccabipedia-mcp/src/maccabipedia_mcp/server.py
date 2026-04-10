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
def search_pages(query: str, namespace: int | None = 0, limit: int = 500) -> dict:
    """Search for an exact phrase across wiki page text.

    Wraps the query in quotes for exact-phrase match across full page text
    (not just titles). Any double-quote characters in *query* are stripped
    before wrapping, so callers don't need to escape them. Automatically
    pages through results until *limit* entries are collected.

    Namespace control:
    - namespace=0 (default): main content namespace only
    - namespace=N: a specific namespace (e.g. 6=File, 10=Template, 14=Category)
    - namespace=None: ALL namespaces (main + talk + file + template + category
      + custom Maccabipedia namespaces like ns=3000 songs)

    Returns a dict with:
    - total_hits: full wiki-wide match count (may exceed limit)
    - results: list of {pageid, title, snippet}, capped at *limit*
    On API error, returns {"error": True, "code": ..., "message": ...}.

    Examples:
        search_pages("אבי כהן")
        → {"total_hits": 312, "results": [
               {"pageid": 1523, "title": "אבי כהן", "snippet": "..."},
               {"pageid": 8891, "title": "גמר גביע 1976/77", "snippet": "..."},
               ...
           ]}

        search_pages("ערן זהבי", namespace=None, limit=50)
        → search every namespace (catches file descriptions, categories,
          song pages, etc.) for the phrase, cap at 50 hits.
    """
    return _client.search_pages(query, namespace=namespace, limit=limit)


@mcp.tool
def list_category_pages(category: str, limit: int = 50) -> list[dict]:
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
