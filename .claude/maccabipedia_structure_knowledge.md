# MaccabiPedia Structure & Knowledge Base

## 1. Namespaces and Page Prefixes

| Sport | Game Format | Player/Coach Pages | Opponent Pages | Season Pages |
|-------|-------------|-------------------|----------------|--------------|
| **Football** | `משחק: DD-MM-YYYY [Home] נגד [Away] - [Competition]` | `Name` (main namespace) | `Name` (main namespace) | `עונת YYYY/YY` (main namespace) |
| **Basketball** | `כדורסל:DD-MM-YYYY [Home] נגד [Away] - [Competition]` | `כדורסל:Name` | `כדורסל:Name` | `כדורסל:עונת YYYY/YY` |
| **Volleyball** | `כדורעף:DD-MM-YYYY [Home] נגד [Away] - [Competition]` | `כדורעף:Name` | `כדורעף:Name` | `כדורעף:עונת YYYY/YY` |

> **Note:** Football game pages use `משחק: ` with a space after the colon (confirmed via Cargo API). Football player pages, coaches, referees, and stadiums all live in the **main namespace** with no prefix — e.g. `שגיב יחזקאל`, not `שחקן:שגיב יחזקאל`.

> **Warning:** Some team names (e.g. `הפועל ירושלים`, `מכבי רחובות`) exist in **both** main namespace (as football pages) and `כדורעף:`/`כדורסל:` namespace. Always use the sport-specific prefix for volleyball/basketball operations.

Competition pages use the sport prefix (e.g. `כדורסל:ליגת העל`, `כדורעף:ליגת העל`).

## 2. Core Templates

| Sport | Template |
|-------|----------|
| Football | `קטלוג משחקים` |
| Basketball | `משחק כדורסל` (quarter points, optional overtime) |
| Volleyball | `משחק כדורעף` (set-by-set results) |

## 3. Page Purging
After uploading/updating a game, purge all related pages using a **batch purge** (collect a `set[str]`, one `purge(forcelinkupdate=True)` at the end).

**Football** (all pages in main namespace):
1. Opponent page — `Name`
2. Season page — `עונת YYYY/YY`
3. Competition page — `Name`
4. Stadium page — `Name`
5. Maccabi players — `Name` (no `שחקן:` prefix; confirmed `שחקן:Name` does not exist)
6. Maccabi coach + Opponent coach — `Name`
7. Referee — `Name`

**Volleyball** (all pages under `כדורעף:` prefix, confirmed via GH Actions logs + wiki API):
1. Opponent page — `כדורעף:Name`
2. Season page — `כדורעף:עונת YYYY/YY`
3. Competition page — `כדורעף:Name`
4. Stadium page — main namespace (stadium pages do **not** exist on the wiki yet; all purges are skipped)
5. Players, coaches, referees — `כדורעף:Name` (not yet implemented; `VolleyballGame` model does not carry these fields)

Filter maccabistats sentinel values before purging: skip `"Cant found coach"`, `"Cant found referee"`, etc.
Only purge related pages if the game page was actually saved (not skipped).

## 4. Date & Naming Conventions
- Date format: `DD-MM-YYYY` (dashes) in page titles.
- `בית חוץ` parameter: strictly `"בית"`, `"חוץ"`, or `"נייטרלי"`.
- Unknown time (`00:00`) → upload as empty string `''`.
- URLs: `https://www.maccabipedia.co.il/Page_Title_With_Underscores` — no `index.php?title=...`.

## 5. Querying Data (Cargo API)
Prefer Cargo over scraping wiki text.
- **Endpoint**: `https://www.maccabipedia.co.il/index.php?title=Special:CargoExport&format=json`
- **Main tables**: `Football_Games`, `Basketball_Games`, `Volleyball_Games`
- **Explore all tables**: `https://www.maccabipedia.co.il/Special:CargoTables`
- Find game page names by querying Cargo by date and extracting `_pageName`.
- **Two Cargo endpoints exist:**
  - `Special:CargoExport` — allows `_pageName` directly, returns flat JSON arrays
  - `action=cargoquery` (API) — rejects field aliases starting with `_`. Must alias: `_pageName=pageName`. The MCP server handles this automatically.
- **MCP server:** Use `mcp__maccabipedia__query_cargo` — it uses `action=cargoquery` and auto-aliases underscore fields so callers can just write `_pageName`.

## 6. Redirects
Hebrew redirect syntax: `#הפניה [[Target_Page_Name]]`
- Basketball seasons: canonical = `כדורסל:עונת YYYY/YY`, redirect from `כדורסל:YYYY/YY`.

## 7. Game Media Files

**Tickets** (`File:` pages):
- Basketball: `{{תיוג כרטיס משחק כדורסל|משחק=PAGE_NAME}}`

**Posters** (`File:` pages):
- Basketball: `{{תיוג כרזת כדורסל|משחק=PAGE_NAME}}`
- If no matching game page found in Cargo, upload with `{{תיוג כרזת כדורסל}}` (no `משחק=`) for tracking
- Filename convention: `כרזת משחק כדורסל DD-MM-YYYY.jpg`

**Newspapers** (`File:` pages, template `{{תיוג עיתונים}}`):
- File naming: `{שם_עיתון}_{תאריך_המשחק}_{שם_היריבה}_{מספר}_{(תאריך_פרסום)}`

## 8. Non-Game Entities

**Fan Songs** (`שיר:` namespace, template `{{שיר}}`):
- Parameters: `קטגוריה`, `שם השיר`, `עונת בכורה`, `על השיר`, `ביצוע לשיר`, `מילים`

## 9. External Research Sources

See `.claude/maccabipedia_research_sources.md` for the full reference of where to search for data by sport and type (stats, rosters, video, etc.).

## 10. MediaWiki Search Behavior (`list=search`)

Live-verified against maccabipedia (2026-04-10) while building the `search_pages` MCP tool:

- **`srnamespace=*` is the only way to search all namespaces.** Omitting the param defaults to ns=0 only. The wildcard catches custom namespaces too, e.g. `ns=3000` (`שיר:` songs).
- **Quoted phrase search accepts `{{` and `}}` as literal characters.** Searching `srsearch='"{{משחק"'` returns ~24K hits (template and file pages that contain that literal source).
- **`:` inside a phrase does NOT match prefixed template names.** `srsearch='"תבנית:משחק"'` returns 0 hits even though hundreds of pages reference `{{תבנית:משחק}}`. To find template *usages*, search for the template body terms in the main namespace; to find the template source itself, use `namespace=10` (Template).
- **Main-namespace search indexes rendered output**, not source wikitext. Template namespace (ns=10) search indexes raw template source. Example: `srsearch='"מארחת"'` in ns=0 finds game pages where the rendered text says "הקבוצה המארחת", not pages whose wikitext has the template arg `|מארחת=`.
- **srlimit max is 500 per request.** For more results, use the `continue.sroffset` cursor. The MCP `search_pages` tool handles paging automatically.
