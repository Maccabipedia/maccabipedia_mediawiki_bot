# MaccabiPedia Structure & Knowledge Base

## 1. Namespaces and Page Prefixes

| Sport | Game Format | Player Pages |
|-------|-------------|--------------|
| **Football** | `משחק: DD-MM-YYYY [Home] נגד [Away] - [Competition]` | `Name` (main namespace, no prefix) |
| **Basketball** | `כדורסל:DD-MM-YYYY [Home] נגד [Away] - [Competition]` | `כדורסל:Name` |
| **Volleyball** | `כדורעף:DD-MM-YYYY [Home] נגד [Away] - [Competition]` | `כדורעף:Name` |

> **Note:** Football game pages use `משחק: ` with a space after the colon (confirmed via Cargo API). Football player pages, coaches, referees, and stadiums all live in the **main namespace** with no prefix — e.g. `שגיב יחזקאל`, not `שחקן:שגיב יחזקאל`.

Season/competition pages use the sport prefix (e.g. `כדורסל:עונת YYYY/YY`, `כדורעף:עונת YYYY/YY`).

## 2. Core Templates

| Sport | Template |
|-------|----------|
| Football | `קטלוג משחקים` |
| Basketball | `משחק כדורסל` (quarter points, optional overtime) |
| Volleyball | `משחק כדורעף` (set-by-set results) |

## 3. Page Purging
After uploading/updating a game, purge all related pages using a **batch purge** (collect a `set[str]`, one `purge(forcelinkupdate=True)` at the end):
1. Opponent page — plain name, main namespace
2. Season page — `עונת YYYY/YY`, main namespace
3. Competition page — plain name, main namespace
4. Stadium/Arena page — plain name, main namespace
5. Maccabi players' pages — plain name, **no `שחקן:` prefix** (confirmed: `שחקן:Name` does not exist)
6. Maccabi coach + Opponent coach — plain name, main namespace
7. Referee — plain name, main namespace

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

## 7. Non-Game Entities

**Newspapers** (`File:` pages, template `{{תיוג עיתונים}}`):
- File naming: `{שם_עיתון}_{תאריך_המשחק}_{שם_היריבה}_{מספר}_{(תאריך_פרסום)}`

**Tickets** (`File:` pages):
- Basketball: `{{תיוג משחק כדורסל|שם משחק=PAGE_NAME}}`

**Fan Songs** (`שיר:` namespace, template `{{שיר}}`):
- Parameters: `קטגוריה`, `שם השיר`, `עונת בכורה`, `על השיר`, `ביצוע לשיר`, `מילים`
