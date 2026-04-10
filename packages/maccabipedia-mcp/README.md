# maccabipedia-mcp

FastMCP server that exposes the Maccabipedia MediaWiki to LLM clients. Each tool wraps a single MediaWiki API operation (Cargo query, page read, page write, search).

## Tools

| Tool | Purpose |
|---|---|
| `list_cargo_tables` | List all Cargo tables available on the wiki |
| `describe_cargo_table` | Get columns and types for a Cargo table |
| `query_cargo` | Run a Cargo query (mirrors the `cargoquery` API) |
| `get_page` | Fetch raw wikitext + metadata for a page |
| `page_exists` | Lightweight existence check |
| `search_pages` | Exact-phrase full-text search with auto-paging |
| `list_category_pages` | List pages in a category |
| `create_page` / `edit_page` | Write a page (fails-if-exists / fails-if-missing) |
| `upload_file` | Upload a file via the MediaWiki API |
| `purge_pages` | Batch-purge pages to refresh cache and Cargo |

## Running

```bash
uv run python -m maccabipedia_mcp
```

Config is read from environment variables; see `config.py`.

## Notes on `search_pages` behavior

Live-verified against the maccabipedia API (2026-04-10). These are MediaWiki quirks the tool surfaces, not bugs in the wrapper:

- **`srnamespace=*` is the only way to search all namespaces.** Omitting the param defaults to ns=0 only. Passing `namespace=None` to `search_pages` sends the wildcard, which catches custom namespaces too (e.g. `ns=3000` for `שיר:` songs).
- **Phrase search accepts `{{` and `}}` as literal characters.** You can search for template markup verbatim — `search_pages("{{משחק")` returns ~24K hits.
- **`:` inside a phrase does NOT match prefixed template names.** `search_pages("תבנית:משחק")` returns 0 hits even though hundreds of pages reference `{{תבנית:משחק}}`. This is MediaWiki tokenization around the colon. To find template *usages*, search for the template body terms in ns=0; to find the template source itself, use `namespace=10` (Template) or `namespace=None`.
- **Main-namespace search indexes rendered output**, not source wikitext. Template namespace (ns=10) search indexes raw template source. Example: `search_pages("מארחת")` in ns=0 finds game pages where the rendered text says "הקבוצה המארחת", not pages whose wikitext has the template arg `|מארחת=`.
- **srlimit max is 500 per API request.** The tool handles paging automatically via `continue.sroffset` up to the caller's `limit`.
- **Embedded `"` in the query are stripped** before the outer phrase wrapping, so callers never need to escape them.
- **Common Maccabipedia namespace IDs**: `0` Main · `6` File · `10` Template · `14` Category · `3000` שיר (songs).

## Tests

```bash
uv run pytest packages/maccabipedia-mcp/tests/
```
