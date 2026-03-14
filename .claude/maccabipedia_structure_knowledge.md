# MaccabiPedia Structure & Knowledge Base

## 1. Namespaces and Page Prefixes

| Sport | Game Format | Player Pages |
|-------|-------------|--------------|
| **Football** | `משחק:DD-MM-YYYY [Home] נגד [Away] - [Competition]` | `שחקן:Name` |
| **Basketball** | `כדורסל:DD-MM-YYYY [Home] נגד [Away] - [Competition]` | `כדורסל:Name` |
| **Volleyball** | `כדורעף:DD-MM-YYYY [Home] נגד [Away] - [Competition]` | `כדורעף:Name` |

Season/competition pages use the sport prefix (e.g. `כדורסל:עונת YYYY/YY`, `כדורעף:עונת YYYY/YY`).

## 2. Core Templates

| Sport | Template |
|-------|----------|
| Football | `קטלוג משחקים` |
| Basketball | `משחק כדורסל` (quarter points, optional overtime) |
| Volleyball | `משחק כדורעף` (set-by-set results) |

## 3. Page Purging
After uploading/updating a game, purge all related pages using a **batch purge** (collect a `set[str]`, one `purge(forcelinkupdate=True)` at the end):
1. Opponent page
2. Season page
3. Competition page
4. Stadium/Arena page
5. Maccabi players' pages (mainly football)
6. Coaches' & Referees' pages

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
