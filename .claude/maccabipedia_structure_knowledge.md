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

Full curated list with links: `https://www.maccabipedia.co.il/מקורות_שימושיים`

### Where to search by need

| I need... | Check these sources |
|-----------|-------------------|
| **Football match results (historical)** | RSSSF (league tables + top scorers), Football Association Archive, WildStat |
| **Football match results (modern)** | Walla Sports, Cargo API |
| **Football player rosters / transfers** | Old maccabita.co.il (Wayback Machine), Twitter thread by @austurgi |
| **Football newspaper coverage** | JPress (Hebrew press, browsable by year), Ynet archive, Hadashot (color). For tours: Trove (Australia), Newspapers.com (US). Institutional: Yedioth Ahronoth + ProQuest (require TAU access) |
| **Football video** | maccabi-videos (Vimeo + YouTube) as primary, ~25 more YouTube channels on the sources page |
| **Football songs** | 12p forum (4 threads covering 2003–2014) |
| **Basketball stats / results** | Hebrew Wikipedia (league + cup seasons), Safsal (cup finals) |
| **Basketball player rosters** | maccabifans (Wayback Machine — has numbered roster pages), Kadorsela dictionary |
| **Basketball history** | "The Israeli Basketball Book" by Eliyahu Shochat (on Yumpu) |
| **Volleyball stats** | IVA dataproject (from 2010/11 only), Walla Sports Volleyball archive (from ~2006) |
| **Volleyball players** | Volleybox (player profiles + videos) |
| **Volleyball pre-2010 history** | Wincol PDF ("pre-establishment years"), Facebook group "כדורעף ושאר סיפורים" |
| **Handball** | Almost no sources. Only: 12p forum song threads (2009–2011). For rosters, try maccabita.co.il and maccabifans via Wayback Machine |
| **Photos (all sports)** | Getty Images, Facebook old photos album, retro blogs, 12p forum 1980s thread, Maccabiah exhibition |
| **Old official Maccabi websites** | maccabita.co.il (Wayback ~2002), maccabifans.co.il (Wayback ~2004–2007), Ultras 96 (Wayback) |
| **General archives** | Israel State Archives, NLI (newspapers + Ephemera/posters), Israeli Museums Portal, Harvard Digital Collections, Israeli Film Archive |

### Key coverage gaps

- **Handball**: no stats, no rosters, no video — only fan songs exist
- **Volleyball 1960s–2010**: IVA starts at 2010/11, Wincol PDF covers pre-establishment — the middle decades are largely undocumented
- **Football pre-1950s**: RSSSF has tables but no lineups/match details; JPress is the best bet for filling these in
- **Basketball video**: no known sources listed
