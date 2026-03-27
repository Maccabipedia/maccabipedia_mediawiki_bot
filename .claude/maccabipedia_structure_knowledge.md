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

## 9. External Research Sources (מקורות שימושיים)

MaccabiPedia maintains an official curated list of approved research sources at:
`https://www.maccabipedia.co.il/מקורות_שימושיים`

---

### Football — Historical/Archival

| Source | URL | Useful for |
|--------|-----|-----------|
| JPress (NLI Hebrew press) | https://jpress.org.il/Olive/APA/NLI_heb/ | Newspaper articles browsable by year |
| RSSSF — league tables | http://www.rsssf.com/tablesi/israhist.html | Historical league results |
| RSSSF — top scorers | http://www.rsssf.com/tablesi/isratops.html | Goal scorers by season |
| Football Association Archive | http://archive.football.org.il/search.asp | Match results & league records |
| WildStat | http://wildstat.com/p/5015/club/ISR_Maccabi_Tel_Aviv | Match data and stats |
| Walla Sports | https://sports.walla.co.il/leagueround/5070?leagueId=361 | Match reports |
| NLI (Ephemera — posters) | http://primo.nli.org.il/primo-explore/search | Old match posters |
| NLI (newspapers / Hadashot) | https://www.nli.org.il/he/newspapers/ | Historical newspaper pages |
| Israel State Archives | https://catalog.archives.gov.il/ | Official state records |
| Israeli Museums Portal | https://museums.gov.il/he/items/Pages/default.aspx | Museum collections |
| Harvard Digital Collections | https://digitalcollections.library.harvard.edu/catalog | Historical materials |
| Trove (Australia) | https://trove.nla.gov.au/ | Coverage of Maccabi tours to Australia |
| Newspapers.com (US) | https://www.newspapers.com/ | Coverage of Maccabi tours to the US |
| Yedioth Ahronoth Archive | http://192.115.83.120.rproxy.tau.ac.il/Olive/APA/Test/ | Full-text archive (**requires TAU access**) |
| ProQuest Global | https://www.proquest.com/?accountid=14765 | Global newspapers (**requires TAU access**) |
| Kan Sport Archive | https://www.kan.org.il/lobby/kan_sport/ | Broadcast archives |
| **Old official Maccabi site** (Web Archive) | https://web.archive.org/web/20021201114805/http://www.maccabita.co.il/default.asp | Old maccabita.co.il — **useful for players/rosters across all sports** |
| Getty Images | https://www.gettyimages.com/photos/maccabi-tel-aviv | Professional photography |

### Football — Video

| Source | URL | Notes |
|--------|-----|-------|
| maccabi-videos (Vimeo) | https://vimeo.com/428829885 | Primary video archive |
| maccabi-videos (YouTube) | https://www.youtube.com/channel/UCxnAYpW-2OJUXbrSil5EeQQ | Official channel |
| NirHoori | https://www.youtube.com/@NirHoori-ii2vk | Match recordings |
| mtaarchive | https://m.youtube.com/user/mtaarchive | Team archives |
| MTAGold | https://www.youtube.com/user/eman12b/videos | Archive content |
| maccabifullgame | https://www.youtube.com/channel/UCD5xM1VeIT7VaMhqv3xOZVw | Complete matches |
| Old VHS cassettes | https://www.youtube.com/@old-vhs-cassettes | Vintage footage |
| Israeli Film Archive | https://jfc.org.il/ | Documentary films |
| State Archives (YouTube) | https://www.youtube.com/user/israelarchive/search | Official archives |
| Sport2 Archive | https://www.youtube.com/user/GamesSportsHD | Broadcast recordings |
| Sport1 Archive | https://www.youtube.com/channel/UC3fmhtLpKrJ525atoWJ4CCA | Broadcast recordings |
| Maccabi in UEFA (blog) | https://mtainuefa.weebly.com/ | European competition coverage |
| Retro photos blog | https://futboltelevisionretro.blogspot.com/2015/07/maccabi-tel-aviv-tv.html | Old photos |

---

### Basketball

| Source | URL | Useful for |
|--------|-----|-----------|
| Kadorsela dictionary | http://www.cadursela.co.il/Dictionary.asp | Historical player/stats reference |
| Safsal — cup finals | https://safsal.co.il/?page_id=17580 | Cup final game records |
| maccabifans (Web Archive, site) | https://web.archive.org/web/20070508213837/http://www.maccabifans.co.il/ | Old fan site, general history |
| maccabifans (Web Archive, **rosters**) | https://web.archive.org/web/20040310150332/http://www.maccabifans.co.il/segel_show.asp?num=15 | **Historical player rosters** — very useful for finding past players |
| "The Israeli Basketball Book" (Yumpu) | https://www.yumpu.com/ar/document/read/61848121/- | Comprehensive written history by Eliyahu Shochat |
| Wikipedia — Premier League seasons | https://he.wikipedia.org/wiki/עונת_2002/2003_בליגת_העל_בכדורסל | Season statistics |
| Wikipedia — State Cup | https://he.wikipedia.org/wiki/גביע_המדינה_בכדורסל_2002/2003 | Cup tournament info |

---

### Volleyball

| Source | URL | Useful for |
|--------|-----|-----------|
| Volleybox — team page | https://volleybox.net/maccabi-tel-aviv-t1631/movies | Match videos |
| Volleybox — **player profiles** | https://volleybox.net/maccabi-tel-aviv-t1631/players | **Finding players and their details** |
| IVA stats (from 2010/11) | https://iva-web.dataproject.com/History.aspx?ID=29 | League standings history |
| Walla Sports Volleyball Archive | https://sports.walla.co.il/archive/191?year=2006&month=3 | Match coverage |
| Volleyball history PDF (Wincol) | https://www.wincol.ac.il/wincol.ac.il/originals/netunim-caduraf.pdf | Pre-establishment history |
| Facebook group | https://www.facebook.com/groups/254545287973398 | "Volleyball and Other Stories" community |

---

### Handball (כדוריד)

The מקורות שימושיים page only lists **song sources** for handball:
- 12p forum — 2009/10 player songs: https://forum.12p.co.il/index.php?app=forums&module=forums&controller=topic&id=107974
- 12p forum — 2010/11 player songs: https://forum.12p.co.il/index.php?app=forums&module=forums&controller=topic&id=126273

For **finding handball players and rosters**, no dedicated source is listed on the page. Useful cross-sport options:
- **Old official Maccabi site** (maccabita.co.il via Web Archive) — see Football section above
- **maccabifans Web Archive** (see basketball section) — may contain handball rosters
- **12p.co.il forum** — search handball topics for player mentions

---

### Cross-Sport Notes
- **12p.co.il / forum.12p.co.il** — the primary fan forum, referenced across all sports for songs, tifos, old photos, and player discussions
- **Web Archive (archive.org)** — frequently used to access dead Maccabi fan sites and old official pages
- Many sources are **Hebrew-only**; some football sources are international (RSSSF, Trove, Newspapers.com)
