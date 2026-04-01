"""
Upload British Mandate era football games (1930-1948) to Maccabipedia.

Reads data/mandate_games_with_scorers.csv, identifies games missing from the wiki,
and creates קטלוג משחקים template pages for them.

Usage:
    python src/maccabipediabot/football/upload_mandate_games.py               # dry-run (all missing)
    python src/maccabipediabot/football/upload_mandate_games.py --season 1930/31  # dry-run one season
    python src/maccabipediabot/football/upload_mandate_games.py --upload      # real upload
    python src/maccabipediabot/football/upload_mandate_games.py --upload --season 1930/31

Dependencies:
    pip install pywikibot
    source ~/.secrets && MACCABIPEDIA_UA_SCRIPT=gamesbot python ...
"""

import argparse
import csv
import datetime
import json
import logging
import re
import urllib.parse
import urllib.request
from pathlib import Path

logging.basicConfig(format="%(asctime)s : %(levelname)s : %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

CSV_PATH = Path("data/mandate_games_with_scorers.csv")
CARGO_URL = "https://www.maccabipedia.co.il/index.php"
MACCABI_NAME = "מכבי תל אביב"

# ---------------------------------------------------------------------------
# Competition name mapping: (csv_competition, season) → wiki competition name
# ---------------------------------------------------------------------------

# For "ליגת ההתאחדות", the wiki name depends on the season.
# Source: queried from Cargo API.
LEAGUE_BY_SEASON = {
    "1930/31":  "הליגה הארצית",
    "1931/32":  "הליגה הארצית",
    "1932/33":  "הליגה הארצית",
    "1933/34":  "הליגה הארצית",
    "1934/35":  "הליגה הארצית",
    "1935/36":  "הליגה הארצית",
    "1937":     "הליגה הארצית",
    "1938":     "הליגה הארצית",
    "1938/39":  "הליגה הארצית",
    "1939":     "הליגה הארצית",
    "1940":     "הליגה הארצית",
    "1941/42":  "הליגה הארצית",
    "1941/43":  "הליגה הארצית",   # multi-year war season; wiki calls it 1941/42
    "1943/44":  "ליגה א",
    "1944/45":  "הליגה הארצית",
    "1946/47":  "ליגה א",
    "1947/48":  "ליגה א",          # tentative — no existing 47/48 wiki games
}


def wiki_season(csv_season: str) -> str:
    """Map CSV season to wiki season name (handles multi-year war seasons)."""
    return {"1941/43": "1941/42"}.get(csv_season, csv_season)


def wiki_competition(csv_competition: str, season: str) -> str:
    """Map CSV competition name to wiki competition name."""
    if csv_competition == "ליגת ההתאחדות":
        return LEAGUE_BY_SEASON.get(season, "הליגה הארצית")
    return csv_competition


# ---------------------------------------------------------------------------
# Cargo helpers
# ---------------------------------------------------------------------------

def cargo_query(tables, fields, where="", order_by="", limit=500, offset=0):
    params = {
        "title": "Special:CargoExport",
        "format": "json",
        "tables": tables,
        "fields": fields,
        "where": where,
        "order_by": order_by,
        "limit": str(limit),
        "offset": str(offset),
    }
    url = CARGO_URL + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "MaccabipediaBot/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        ct = resp.headers.get("Content-Type", "")
        if "json" not in ct:
            raise RuntimeError(f"Unexpected Content-Type: {ct!r} — expected JSON")
        return json.loads(resp.read().decode("utf-8"))


def fetch_all_cargo(tables, fields, where="", order_by=""):
    results, offset = [], 0
    while True:
        batch = cargo_query(tables, fields, where, order_by, limit=500, offset=offset)
        if not batch:
            break
        results.extend(batch)
        if len(batch) < 500:
            break
        offset += 500
    return results


# ---------------------------------------------------------------------------
# Identify missing games
# ---------------------------------------------------------------------------

LEAGUE_NAMES = {"הליגה הארצית", "ליגה א", "ליגה לאומית"}


def fetch_wiki_league_dates():
    """Return set of ISO date strings for mandate-era league games in the wiki."""
    rows = fetch_all_cargo(
        "Football_Games", "Date,Competition",
        where="Date >= '1930-01-01' AND Date <= '1948-12-31'",
    )
    dates = set()
    for r in rows:
        if r.get("Competition", "").strip() in LEAGUE_NAMES:
            if r.get("Date"):
                dates.add(r["Date"])
    return dates


def near_miss_dates(wiki_dates):
    """Expand a set of ISO date strings by ±2 days."""
    expanded = set(wiki_dates)
    for d_str in wiki_dates:
        try:
            d = datetime.date.fromisoformat(d_str)
            for delta in range(1, 3):
                expanded.add((d + datetime.timedelta(days=delta)).isoformat())
                expanded.add((d - datetime.timedelta(days=delta)).isoformat())
        except ValueError:
            pass
    return expanded


def load_missing_games(season_filter=None):
    """
    Load CSV rows for games not already in the wiki (±2 day tolerance).
    Optionally filter to a single season.
    """
    log.info("Loading CSV…")
    with open(CSV_PATH, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    log.info(f"  {len(rows)} CSV games")

    log.info("Fetching wiki league dates…")
    wiki_dates = fetch_wiki_league_dates()
    matched = near_miss_dates(wiki_dates)
    log.info(f"  {len(wiki_dates)} wiki league games (±2 day tolerance applied)")

    missing = []
    for row in rows:
        d = row["date"].strip()
        parts = d.split("-")
        if len(parts) != 3:
            continue
        iso = f"{parts[2]}-{parts[1]}-{parts[0]}"
        if iso in matched:
            continue
        if season_filter and row["season"] != season_filter:
            continue
        # Only upload official league games; skip ליגה ב' (likely reserve-team games)
        if row["competition"] != "ליגת ההתאחדות":
            continue
        missing.append(row)

    log.info(f"  {len(missing)} missing games to upload")
    return missing


# ---------------------------------------------------------------------------
# Build template text
# ---------------------------------------------------------------------------

def build_events_field(row):
    """
    Build the אירועי שחקנים field value from maccabi_scorers_parsed
    and opponent_scorers_parsed.

    Format per event: NAME::אין-מספר::גול::MINUTE::TEAM
    """
    events = []

    for field, team_label in [
        ("maccabi_scorers_parsed",  "מכבי"),
        ("opponent_scorers_parsed", "יריבה"),
    ]:
        raw = row.get(field, "")
        if not raw:
            continue
        try:
            scorers = json.loads(raw)
        except json.JSONDecodeError:
            continue
        for s in scorers:
            name = s.get("name", "").strip()
            if not name or not re.search(r"[\u05D0-\u05EA]", name):
                continue
            minute = s.get("minute") or 0
            events.append(f"{name}::אין-מספר::גול::{minute}::{team_label}\n")

    return "".join(events)


def build_page_name(row):
    """
    Build the wiki page title.
    Convention (matches all existing mandate-era pages):
      משחק:DD-MM-YYYY מכבי תל אביב נגד OPPONENT - COMPETITION
    """
    date = row["date"]
    opponent = row["opponent"]
    comp = wiki_competition(row["competition"], row["season"])
    return f"משחק:{date} {MACCABI_NAME} נגד {opponent} - {comp}"


def build_template_text(row):
    """Build the full {{קטלוג משחקים}} wikitext for a game row."""
    comp = wiki_competition(row["competition"], row["season"])
    events = build_events_field(row)

    lines = [
        "{{קטלוג משחקים",
        f"|תאריך המשחק={row['date']}",
        "|שעת המשחק=",
        f"|עונה={wiki_season(row['season'])}",
        f"|מפעל={comp}",
        "|שלב במפעל=",
        f"|שם יריבה={row['opponent']}",
        f"|בית חוץ={row['home_away']}",
        f"|אצטדיון={row.get('stadium', '')}",
        f"|תוצאת משחק מכבי={row['maccabi_score']}",
        f"|תוצאת משחק יריבה={row['opponent_score']}",
        "|מאמן מכבי=",
        "|מאמן יריבה=",
        "|שופט ראשי=",
        "|עוזרי שופט=",
        "|כמות קהל=",
        "|גוף שידור=",
        "|מדים=",
        f"|אירועי שחקנים={events}",
        "}}",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Dry-run output
# ---------------------------------------------------------------------------

def print_dry_run(missing_games):
    print(f"\n{'='*70}")
    print(f"DRY RUN — {len(missing_games)} games would be uploaded")
    print(f"{'='*70}\n")

    by_season = {}
    for row in missing_games:
        by_season.setdefault(row["season"], []).append(row)

    for season, games in sorted(by_season.items()):
        print(f"--- {season} ({len(games)} games) ---")
        for row in games:
            page = build_page_name(row)
            scorers = json.loads(row.get("maccabi_scorers_parsed") or "[]")
            scorer_names = [s["name"] for s in scorers]
            opp_scorers = json.loads(row.get("opponent_scorers_parsed") or "[]")
            opp_names = [s["name"] for s in opp_scorers]
            score = f"{row['maccabi_score']}-{row['opponent_score']}"
            print(f"  {row['date']} | {row['home_away']} | {score}")
            print(f"    → {page}")
            if scorer_names:
                print(f"    מכבי: {', '.join(scorer_names)}")
            if opp_names:
                print(f"    יריבה: {', '.join(opp_names)}")
        print()


# ---------------------------------------------------------------------------
# Real upload
# ---------------------------------------------------------------------------

def upload_games(missing_games):
    import pywikibot as pw
    from maccabipediabot.common.wiki_login import get_site

    site = get_site()

    saved = 0
    skipped = 0
    pages_to_purge = set()

    for row in missing_games:
        page_name = build_page_name(row)
        page = pw.Page(site, page_name)

        if page.exists():
            log.info(f"  SKIP (exists): {page_name}")
            skipped += 1
            continue

        page.text = build_template_text(row)
        log.info(f"  Saving: {page_name}")
        page.save(summary="MaccabiBot - Mandate era game (1930-1948)")
        saved += 1

        # Collect pages to purge
        pages_to_purge.add(row["opponent"])
        pages_to_purge.add(f"עונת {row['season']}")
        pages_to_purge.add(wiki_competition(row["competition"], row["season"]))
        for s in json.loads(row.get("maccabi_scorers_parsed") or "[]"):
            if s.get("name"):
                pages_to_purge.add(s["name"])

    log.info(f"\nDone. {saved} saved, {skipped} skipped.")

    # Batch purge
    if pages_to_purge:
        log.info(f"Purging {len(pages_to_purge)} related pages…")
        for pname in sorted(pages_to_purge):
            try:
                p = pw.Page(site, pname)
                if p.exists():
                    p.purge(forcelinkupdate=True)
            except Exception as e:
                log.warning(f"  Purge failed for {pname}: {e}")
        log.info("Purge complete.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Upload mandate-era games to Maccabipedia")
    parser.add_argument("--upload", action="store_true",
                        help="Actually upload (default is dry-run)")
    parser.add_argument("--season", default=None,
                        help="Limit to a single season, e.g. 1930/31")
    args = parser.parse_args()

    missing = load_missing_games(season_filter=args.season)

    if not missing:
        print("No missing games found.")
        return

    if args.upload:
        log.info("=== UPLOAD MODE ===")
        upload_games(missing)
    else:
        print_dry_run(missing)
        print("Re-run with --upload to actually save pages.")


if __name__ == "__main__":
    main()
