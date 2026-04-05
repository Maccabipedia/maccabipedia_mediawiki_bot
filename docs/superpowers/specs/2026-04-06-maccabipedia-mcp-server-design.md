# Maccabipedia MCP Server — Design Spec

## 1. Purpose

A FastMCP server that provides read/write access to the Maccabipedia MediaWiki wiki. Consumers are both Claude Code (interactive exploration) and bot scripts (programmatic access).

The server is a **transport layer** — it moves data between consumers and the wiki's HTTP APIs. It does not parse wikitext, manipulate templates, or contain business logic. Parsing responsibility stays with the consumer (Claude understands wikitext natively; bots use `mwparserfromhell`).

## 2. Architecture

```
+-----------------+     +---------------------+     +--------------+
|  Claude Code    |     |  MCP Server         |     |  Maccabipedia|
|  or Bot script  |<--->|  (FastMCP, stdio)   |<--->|  MediaWiki   |
+-----------------+     |                     |     |  HTTP API    |
                        |  - No pywikibot     |     +--------------+
                        |  - requests only    |
                        |  - Stateless reads  |
                        |  - Session for writes|
                        +---------------------+
```

**Key decisions:**

- **Framework:** FastMCP (`fastmcp` package)
- **Transport:** stdio (standard for Claude Code MCP servers)
- **HTTP client:** `requests` — no pywikibot dependency
- **Auth:** Lazy — no login until a write tool is called. All reads are unauthenticated.
- **State:** A single `requests.Session` initialized on first write, holding login cookies + CSRF token
- **Package location:** `src/maccabipedia_mcp/` in this repo
- **Entry point:** `uv run python -m maccabipedia_mcp`

## 3. Tools (11 total)

### 3.1 Cargo Tools (3, no auth)

#### `list_cargo_tables`

Returns all Cargo tables available on the wiki.

- **Params:** none
- **Returns:** List of table names
- **Implementation:** `GET /api.php?action=cargotables&format=json` — returns `{"cargotables": ["Table1", "Table2", ...]}`

#### `describe_cargo_table`

Returns column names and types for a given Cargo table.

- **Params:**
  - `table` (str, required) — table name
- **Returns:** List of `{name, type}` objects
- **Implementation:** `GET /api.php?action=cargofields&table=...&format=json` — returns `{"cargofields": {"FieldName": "Type", ...}}`

#### `query_cargo`

Generic Cargo query, aligned with the MediaWiki `action=cargoquery` API.

- **Params:**
  - `tables` (str, required) — table(s) to query
  - `fields` (str, required) — fields to retrieve
  - `where` (str, optional) — SQL WHERE clause
  - `join_on` (str, optional) — JOIN ON conditions for multi-table queries
  - `group_by` (str, optional) — GROUP BY fields
  - `having` (str, optional) — HAVING conditions for grouped values
  - `order_by` (str, optional) — ORDER BY clause
  - `limit` (int, optional) — 1-500, default 50
  - `offset` (int, optional) — default 0
- **Returns:** JSON array of result objects
- **Implementation:** `GET /api.php?action=cargoquery&format=json&...`

### 3.2 Page Read Tools (4, no auth)

#### `get_page`

Returns raw wikitext and metadata for a page.

- **Params:**
  - `title` (str, required) — page title
- **Returns:** `{exists, title, wikitext, redirect_target}`
  - `exists` — boolean
  - `wikitext` — raw page text (empty string if page doesn't exist)
  - `redirect_target` — target page title if this is a redirect, null otherwise
- **Implementation:** `GET /api.php?action=parse&page=...&prop=wikitext` or `action=query&prop=revisions&rvprop=content`

#### `page_exists`

Lightweight existence check without fetching full content.

- **Params:**
  - `title` (str, required) — page title
- **Returns:** `{exists, redirect}` — boolean flags
- **Implementation:** `GET /api.php?action=query&titles=...`

#### `search_pages`

Full-text search across the wiki.

- **Params:**
  - `query` (str, required) — search text
  - `namespace` (int, optional) — restrict to namespace
  - `limit` (int, optional) — default 10, max 50
- **Returns:** List of `{title, snippet}` objects
- **Implementation:** `GET /api.php?action=query&list=search&srsearch=...`

#### `list_category_pages`

Lists pages in a given category.

- **Params:**
  - `category` (str, required) — category name (with or without `קטגוריה:` prefix)
  - `limit` (int, optional) — default 50, max 500
- **Returns:** List of page titles
- **Implementation:** `GET /api.php?action=query&list=categorymembers&cmtitle=...`

### 3.3 Page Write Tools (4, requires auth)

All write tools trigger lazy authentication on first call.

#### `create_page`

Creates a new wiki page. **Fails if the page already exists.**

- **Params:**
  - `title` (str, required) — page title
  - `text` (str, required) — full wikitext content
  - `summary` (str, required) — edit summary
- **Returns:** `{success, title, revid}` or error
- **Implementation:** `POST /api.php` with `action=edit&createonly=1&title=...&text=...&summary=...&token=...`

#### `edit_page`

Edits an existing wiki page. **Fails if the page does not exist.**

- **Params:**
  - `title` (str, required) — page title
  - `text` (str, required) — full wikitext content
  - `summary` (str, required) — edit summary
- **Returns:** `{success, title, revid}` or error
- **Implementation:** `POST /api.php` with `action=edit&nocreate=1&title=...&text=...&summary=...&token=...`

#### `upload_file`

Uploads a file (image, PDF, etc.) to the wiki.

- **Params:**
  - `filename` (str, required) — target filename on the wiki (e.g. `כרזת משחק כדורסל 01-01-2025.jpg`)
  - `file_path` (str, required) — local filesystem path to the file
  - `text` (str, required) — file page wikitext (typically a tagging template)
  - `comment` (str, required) — upload comment
- **Returns:** `{success, filename}` or error
- **Implementation:** `POST /api.php` with `action=upload&filename=...&token=...&ignorewarnings=1`, multipart form with file data. Uses `requests.post(..., files=...)` per the pattern in `upload_basketball_tickets.py`.

#### `purge_pages`

Purges one or more pages, forcing cache and Cargo data refresh.

- **Params:**
  - `titles` (list[str], required) — page titles to purge
- **Returns:** List of `{title, purged}` results
- **Implementation:** `POST /api.php` with `action=purge&titles=...|...|...&forcelinkupdate=1`. Batches in groups of 50 (API limit).

## 4. Authentication

### 4.1 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `MACCABIPEDIA_BOT_USERNAME` | For writes | Bot account username |
| `MACCABIPEDIA_BOT_PASSWORD` | For writes | Bot account password |
| `MACCABIPEDIA_URL` | No | Wiki base URL, default `https://www.maccabipedia.co.il` |

### 4.2 Login Flow (lazy, on first write)

1. `POST /api.php` with `action=login&lgname=...&lgpassword=...&format=json` — get login token
2. `POST /api.php` with `action=login&lgname=...&lgpassword=...&lgtoken=...&format=json` — confirm login
3. `GET /api.php?action=query&meta=tokens&type=csrf&format=json` — get CSRF token
4. Store session cookies + CSRF token on the `requests.Session`

### 4.3 Token Refresh

If a write fails with `badtoken` error, re-fetch the CSRF token once and retry. If it fails again, return the error.

## 5. Error Handling

| Scenario | Behavior |
|----------|----------|
| Cargo returns HTML instead of JSON | Check `Content-Type` header before parsing. Return clear error: "Cargo returned non-JSON response" |
| Auth failure (bad credentials) | Return error with message, do not retry |
| `create_page` on existing page | Return error: "Page already exists" (MediaWiki `articleexists` error) |
| `edit_page` on missing page | Return error: "Page does not exist" (MediaWiki `missingtitle` error) |
| CSRF token expired | Re-fetch token, retry once |
| Network error | Return error with details, do not retry |
| Upload fails | Return MediaWiki error message (e.g., file type not allowed) |

All errors return structured objects: `{error: true, code: "...", message: "..."}`.

## 6. File Structure

```
src/maccabipedia_mcp/
    __init__.py
    __main__.py          # Entry point: creates & runs FastMCP server
    server.py            # FastMCP app definition, tool registrations
    wiki_client.py       # WikiClient class: all HTTP calls to MediaWiki
    config.py            # Env var loading, defaults, constants
```

### Responsibilities

- **`config.py`** — reads env vars, provides `Config` dataclass with `url`, `username`, `password`
- **`wiki_client.py`** — `WikiClient` class with methods matching each tool. Holds the `requests.Session`. Handles auth, CSRF tokens, error checking. All MediaWiki API interaction is here.
- **`server.py`** — creates the `FastMCP` app, instantiates `WikiClient`, registers tools as thin functions that delegate to the client.
- **`__main__.py`** — `from .server import mcp; mcp.run()`

## 7. Configuration

### `.mcp.json` entry

```json
{
  "mcpServers": {
    "maccabipedia": {
      "command": "uv",
      "args": ["run", "python", "-m", "maccabipedia_mcp"],
      "env": {
        "MACCABIPEDIA_BOT_USERNAME": "...",
        "MACCABIPEDIA_BOT_PASSWORD": "..."
      }
    }
  }
}
```

### `settings.json` permissions

```json
{
  "permissions": {
    "allow": [
      "mcp__maccabipedia__list_cargo_tables",
      "mcp__maccabipedia__describe_cargo_table",
      "mcp__maccabipedia__query_cargo",
      "mcp__maccabipedia__get_page",
      "mcp__maccabipedia__page_exists",
      "mcp__maccabipedia__search_pages",
      "mcp__maccabipedia__list_category_pages"
    ]
  }
}
```

Write tools (`create_page`, `edit_page`, `upload_file`, `purge_pages`) are intentionally NOT auto-allowed — Claude Code will prompt the user for each write operation.

## 8. Dependencies

Added to the existing `pyproject.toml`:

- `fastmcp` — MCP server framework
- No new dependencies beyond what's already in the project (`requests`, `pydantic` are already present)

## 9. Testing Strategy

- **Unit tests** for `WikiClient` methods with mocked HTTP responses (using `responses` or `respx` library)
- **Test fixtures** with sample Cargo JSON responses, page wikitext, error responses
- **No integration tests against the live wiki** in CI — those are manual/opt-in

Tests live in `tests/mcp/`.

## 10. Out of Scope

- Wikitext parsing or template manipulation — consumer responsibility
- maccabistats integration — separate concern, can be added later
- External source scraping (LiveScore, IVA, etc.) — stays in bot code
- Monorepo restructuring — future work
- Skill/prompt layer on top of MCP — can be added later
