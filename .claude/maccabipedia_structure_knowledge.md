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

Wiki page with full list: `https://www.maccabipedia.co.il/מקורות_שימושיים`

### Cross-sport sources

**Old Maccabi websites (Wayback Machine):**
- maccabita.co.il (~2002): https://web.archive.org/web/20021201114805/http://www.maccabita.co.il/default.asp — old official site, useful for rosters across all sports
- maccabifans.co.il (~2004–2007): https://web.archive.org/web/20070508213837/http://www.maccabifans.co.il/ — roster pages: https://web.archive.org/web/20040310150332/http://www.maccabifans.co.il/segel_show.asp?num=15
- Ultras 96: https://web.archive.org/web/20040822043201/http://www.ultras.co.il/one_news.asp?IDNews=1028

**National archives:**
- Israel State Archives: https://catalog.archives.gov.il/
- NLI — JPress (Hebrew press by year): https://jpress.org.il/Olive/APA/NLI_heb/
- NLI — Ephemera/posters: http://primo.nli.org.il/primo-explore/search?query=any,contains,%D7%9E%D7%9B%D7%91%D7%99%20%D7%AA%22%D7%90&tab=default_tab&search_scope=Ephemera1&vid=NNL_Ephemera&sortby=rank&lang=iw_IL
- NLI — Hadashot newspaper (color): https://www.nli.org.il/he/newspapers/
- Israeli Museums Portal: https://museums.gov.il/he/items/Pages/default.aspx
- Harvard Digital Collections: https://digitalcollections.library.harvard.edu/catalog
- Israeli Film Archive: https://jfc.org.il/

**Press:**
- Ynet archive: https://www.ynet.co.il/home/0,7340,L-4269-77-57,00.html
- Walla Sports: https://sports.walla.co.il/
- Pendel magazines: http://www.pendelmag.com/index.html
- Trove (Australian newspapers — Maccabi tours): https://trove.nla.gov.au/
- Newspapers.com (US — Maccabi tours): https://www.newspapers.com/
- Yedioth Ahronoth full archive (**requires TAU access**): http://192.115.83.120.rproxy.tau.ac.il/Olive/APA/Test/
- ProQuest Global (**requires TAU access**): https://www.proquest.com/?accountid=14765

**Photos:**
- Getty Images: https://www.gettyimages.com/photos/maccabi-tel-aviv
- Facebook old photos album: https://www.facebook.com/media/set/?set=a.10201605865284990&type=3
- Retro blog 1: https://futboltelevisionretro.blogspot.com/2015/07/maccabi-tel-aviv-tv.html
- Retro blog 2: https://lagaleriadelfutbol.blogspot.com/2015/07/maccabitelaviv.html

**Forums:**
- 12p forum (songs, tifos, photos, all sports): https://forum.12p.co.il/

### Football

**Stats & results:**
- RSSSF league tables: http://www.rsssf.com/tablesi/israhist.html
- RSSSF top scorers: http://www.rsssf.com/tablesi/isratops.html
- Football Association Archive: http://archive.football.org.il/
- WildStat: http://wildstat.com/p/5015/club/ISR_Maccabi_Tel_Aviv

**Video (primary channels):**
- maccabi-videos Vimeo: https://vimeo.com/428829885
- maccabi-videos YouTube: https://www.youtube.com/channel/UCxnAYpW-2OJUXbrSil5EeQQ
- maccabifullgame: https://www.youtube.com/channel/UCD5xM1VeIT7VaMhqv3xOZVw
- mtaarchive: https://m.youtube.com/user/mtaarchive
- ~25 more channels listed on the wiki sources page

**Songs:**
- 12p forum threads (2003–2014): https://forum.12p.co.il/index.php?showtopic=157350

### Basketball

**Stats & results:**
- Hebrew Wikipedia (league seasons): https://he.wikipedia.org/wiki/עונת_2002/2003_בליגת_העל_בכדורסל
- Hebrew Wikipedia (state cup): https://he.wikipedia.org/wiki/גביע_המדינה_בכדורסל_2002/2003
- Safsal (cup finals): https://safsal.co.il/?page_id=17580

**Rosters & players:**
- Kadorsela dictionary: http://www.cadursela.co.il/Dictionary.asp
- maccabifans roster pages (Wayback): see cross-sport section

**Books:**
- "The Israeli Basketball Book" by Eliyahu Shochat: https://www.yumpu.com/ar/document/read/61848121/-

### Volleyball

**Stats & results:**
- IVA Premier League (from 2010/11 only): https://iva-web.dataproject.com/History.aspx?ID=29
- Walla Sports Volleyball archive (from ~2006): https://sports.walla.co.il/archive/191?year=2006&month=3

**Players & video:**
- Volleybox players: https://volleybox.net/maccabi-tel-aviv-t1631/players
- Volleybox videos: https://volleybox.net/maccabi-tel-aviv-t1631/movies

**History:**
- Wincol PDF (pre-establishment): https://www.wincol.ac.il/wincol.ac.il/originals/netunim-caduraf.pdf
- Facebook group "כדורעף ושאר סיפורים": https://www.facebook.com/groups/254545287973398

### Handball

Almost no dedicated sources. Only fan songs:
- 12p forum 2009/10: https://forum.12p.co.il/index.php?app=forums&module=forums&controller=topic&id=107974
- 12p forum 2010/11: https://forum.12p.co.il/index.php?app=forums&module=forums&controller=topic&id=126273

For rosters/players, try maccabita.co.il and maccabifans via Wayback Machine (see cross-sport section).

### Key coverage gaps

- **Handball**: no stats, no rosters, no video — only fan songs
- **Volleyball 1960s–2010**: IVA starts at 2010/11, Wincol PDF covers pre-establishment — middle decades undocumented
- **Football pre-1950s**: RSSSF has tables but no lineups/match details; JPress is the best bet
- **Basketball video**: no known sources
