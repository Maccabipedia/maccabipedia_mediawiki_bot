# Tracking Categories — Handoff Document

**Session date:** 2026-04-10  
**Status:** Category 1 partially complete. Categories 2–5 not yet started.

---

## Background

Maccabipedia uses hidden wiki categories to flag pages with data issues. We reviewed all tracking categories and ranked the top 5 by ROI. This document captures what was done and what remains.

**Key reference files:**
- `.claude/maccabipedia_structure_knowledge.md` — template formats, valid event types, Cargo API
- `illegal_events_report.html` — full HTML report with all 5 categories and suggested fixes
- `packages/maccabipediabot/src/maccabipediabot/common/maccabistats_player_event.py` — event type mappings

---

## Category 1: אירועי שחקנים לא חוקיים (Illegal Player Events)

### What was done

**Template fix:** Added `בישול-נגיחה` (headed assist, subtype 47) as a valid event type to:
- `תבנית:קטלוג משחקים/הזנת אירועי משחק לטבלת אירועי משחק` ✅
- `מיוחד:CargoTables/Games_Sub_Events_Mapping` ✅

**Auto-fixes applied to 4 pages:**
| Page | Fix |
|------|-----|
| משחק:14-02-1970 מכבי נתניה נגד מכבי תל אביב - ליגה לאומית | `גול-נגיחה:67` → single colon fixed |
| משחק:01-05-1971 מכבי תל אביב נגד הפועל פתח תקווה - גביע המדינה | `גול-רגך` → `גול-רגל` (typo) |
| משחק:03-12-1994 מכבי תל אביב נגד מכבי הרצליה - ליגה לאומית | `בישול-סחיטת פנדל מוצלח` → `בישול-סחיטת פנדל` (×2) |
| משחק:23-04-2003 מכבי תל אביב נגד הפועל באר שבע - ליגת העל | `בישול-קלאיסי` → `בישול-קלאסי` (typo) |

**Important findings from template analysis:**
- `גול` (bare, no subtype) — **valid**, does NOT trigger the tracking category
- `בישול` (bare, no subtype) — **valid**, does NOT trigger the tracking category
- `גול-עצמי` — **valid** (subtype 33)
- `גול-חופשית` — **valid** (same as `גול-בעיטה חופשית`, subtype 34)
- `כרטיס צהוב-ראשון` / `כרטיס צהוב-שני` — **valid** (subtypes 74/72)
- `בישול-נגיחה` — **now valid** after template update (subtype 47)

### Still open — requires human judgment (8 pages)

These have genuinely ambiguous event types. A human needs to watch the game or find a source to determine the correct subtype:

| Page | Issue | Notes |
|------|-------|-------|
| [משחק:13-12-2020 הפועל חיפה](https://www.maccabipedia.co.il/משחק:13-12-2020_מכבי_תל_אביב_נגד_הפועל_חיפה_-_ליגת_העל) | `גול-קלאסי` (חנן ממן) | Could be רגל/נגיחה/פנדל |
| [משחק:15-09-1973 הפועל אור יהודה](https://www.maccabipedia.co.il/משחק:15-09-1973_מכבי_תל_אביב_נגד_הפועל_אור_יהודה_-_גביע_המדינה) | `גול-פרץ` (ויקי פרץ) | Last name used as type by mistake |
| [משחק:26-02-1955 מכבי חיפה](https://www.maccabipedia.co.il/משחק:26-02-1955_מכבי_חיפה_נגד_מכבי_תל_אביב_-_ליגה_לאומית) | `גול-ישראל` (פפו ישראלי) | Same — last name used as type |
| [משחק:11-04-1942 שבאב אל ערב](https://www.maccabipedia.co.il/משחק:11-04-1942_שבאב_אל_ערב_חיפה_נגד_מכבי_תל_אביב_-_הגביע_הארץ_ישראלי) | `גול-ידוע` ×11 | "Known goal" — means scorer is known but method isn't. Note: `גול-לא-ידוע` IS valid but `גול-ידוע` is not |
| [משחק:20-09-1958 שמשון](https://www.maccabipedia.co.il/משחק:20-09-1958_שמשון_תל_אביב_נגד_מכבי_תל_אביב_-_גביע_המדינה) | `גול-לא רגל` (רפי לוי) | "Not by foot" — נגיחה or חזה? |
| [משחק:13-01-1962 הפועל חיפה](https://www.maccabipedia.co.il/משחק:13-01-1962_הפועל_חיפה_נגד_מכבי_תל_אביב_-_ליגה_לאומית) | `גול-קלאסי` (שלמה לוי) | Could be רגל/נגיחה/פנדל |
| [משחק:18-02-1961 בני יהודה](https://www.maccabipedia.co.il/משחק:18-02-1961_בני_יהודה_נגד_מכבי_תל_אביב_-_ליגה_לאומית) | `גול-קלאסי` ×2 (י מזרחי, מלאך רוטשס) | Could be רגל/נגיחה/פנדל |
| [משחק:13-12-2014 הפועל פ"ת](https://www.maccabipedia.co.il/משחק:13-12-2014_הפועל_פתח_תקווה_נגד_מכבי_תל_אביב_-_ליגת_העל) | `בישול-רגל` (מייקל טוקורה) | Foot assist — likely `בישול-קלאסי` but verify |

---

## Category 2: פרופילים ללא שם לועזי (Profiles Missing Latin Name)

~20+ player profiles have no Latin name (`FullForeignName` field empty in Cargo `Profiles` table).  
The HTML report (`illegal_events_report.html`, Category 2 section) includes 20 sample profiles with proposed Latin name values based on known player data.  
**Action needed:** Review proposed names and fill them in on the wiki profile pages.

---

## Category 3: שופטים ללא עמוד (Referees Without a Page)

94 football games reference referees who have no dedicated wiki page.  
Games are categorized under `משחקים המפנים לשופט ללא עמוד`.  
The HTML report lists all 94 games.  
**Action needed:** Create stub pages for each missing referee, or batch-create via bot.

---

## Category 4: פרופילים ללא רגל דומיננטית (Profiles Missing Dominant Foot)

Player profiles missing the `PreferFoot` field in Cargo.  
The HTML report includes 15 sample profiles.  
**Action needed:** Research and fill in dominant foot for each player.

---

## Category 5: משחקים היסטוריים ללא מאמן (Historical Games Missing Coach)

53 games from 1930–1962 have no Maccabi coach recorded.  
**Action needed:** Historical research (JPress, RSSSF, old newspapers) to identify coaches per season. See `.claude/maccabipedia_research_sources.md` for sources.

---

## Pending Code Task

**Add `בישול-נגיחה` to maccabistats** — the bot's `maccabistats_player_event.py` already maps `GoalTypes.HEADER → "נגיחה"` so headed assists should naturally produce `בישול-נגיחה`. Needs verification and possible CHANGELOG/version bump.  
See task #2 in the current task list.
