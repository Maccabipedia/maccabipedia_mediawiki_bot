"""
Compare mandate-era games from CSV (extracted from book) against MaccabiPedia.

Produces a report showing:
1. Games in CSV that exist/don't exist in MaccabiPedia (matched by date)
2. For matching games: scorer comparison with fuzzy name matching
3. Summary statistics

Usage:
    python research/compare_mandate_games.py
"""

import csv
import datetime
import json
import re
import sys
import urllib.parse
import urllib.request
from collections import defaultdict
from difflib import SequenceMatcher

CSV_PATH = "data/mandate_games_with_scorers.csv"
CARGO_URL = "https://www.maccabipedia.co.il/index.php"
REPORT_PATH = "data/mandate_comparison_report.txt"
HTML_REPORT_PATH = "data/mandate_comparison_report.html"
WIKI_BASE = "https://www.maccabipedia.co.il/wiki/"

# Competition name mapping: CSV name → wiki name (season-dependent)
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
    "1941/43":  "הליגה הארצית",
    "1943/44":  "ליגה א",
    "1944/45":  "הליגה הארצית",
    "1946/47":  "ליגה א",
    "1947/48":  "ליגה א",
}


def wiki_competition(csv_competition, season):
    if csv_competition == "ליגת ההתאחדות":
        return LEAGUE_BY_SEASON.get(season, "הליגה הארצית")
    return csv_competition


# Minimum similarity ratio for fuzzy matching
OPPONENT_SIMILARITY_THRESHOLD = 0.55
SCORER_SIMILARITY_THRESHOLD = 0.50


def cargo_query(tables, fields, where="", order_by="", limit=500, offset=0):
    """Query MaccabiPedia Cargo API and return parsed JSON."""
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
    url = f"{CARGO_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "MaccabipediaBot/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        if resp.status != 200:
            raise RuntimeError(f"Cargo API returned {resp.status}")
        ct = resp.headers.get("Content-Type", "")
        if "json" not in ct:
            raise RuntimeError(f"Unexpected Content-Type: {ct}")
        return json.loads(resp.read().decode("utf-8"))


def fetch_all_cargo(tables, fields, where="", order_by=""):
    """Fetch all results from Cargo, paginating as needed."""
    all_results = []
    offset = 0
    while True:
        batch = cargo_query(tables, fields, where, order_by, limit=500, offset=offset)
        if not batch:
            break
        all_results.extend(batch)
        if len(batch) < 500:
            break
        offset += 500
    return all_results


def date_csv_to_iso(date_str):
    """Convert DD-MM-YYYY to YYYY-MM-DD."""
    parts = date_str.strip().split("-")
    if len(parts) != 3:
        return None
    return f"{parts[2]}-{parts[1]}-{parts[0]}"


def similarity(a, b):
    """Compute string similarity ratio between two strings."""
    if not a or not b:
        return 0.0
    # Normalize: strip whitespace, remove common noise
    a = re.sub(r'["\s]+', ' ', a).strip()
    b = re.sub(r'["\s]+', ' ', b).strip()
    return SequenceMatcher(None, a, b).ratio()


def normalize_name(name):
    """Normalize a Hebrew name for comparison."""
    if not name:
        return ""
    # Remove quotes, parentheses, numbers-only fragments, question marks
    name = re.sub(r'[()?\[\]"\'׳]', '', name)
    # Remove leading/trailing digits and whitespace
    name = re.sub(r'^\d+\s*', '', name)
    name = re.sub(r'\s*\d+$', '', name)
    name = name.strip()
    return name


def is_junk_scorer(name):
    """Check if a parsed scorer name is junk/noise from OCR."""
    n = normalize_name(name)
    if not n:
        return True
    # Pure numbers or single char
    if re.match(r'^[\d\s]+$', n):
        return True
    if len(n) <= 1:
        return True
    # Just punctuation
    if re.match(r'^[()?\[\]"\',.\s]+$', n):
        return True
    return False


def best_scorer_match(csv_scorer, wiki_scorers):
    """Find the best matching wiki scorer for a CSV scorer name.
    Returns (best_match_name, similarity_ratio) or (None, 0)."""
    csv_norm = normalize_name(csv_scorer)
    if not csv_norm:
        return None, 0

    best_name = None
    best_ratio = 0
    for ws in wiki_scorers:
        ws_norm = normalize_name(ws)
        if not ws_norm:
            continue
        ratio = similarity(csv_norm, ws_norm)
        if ratio > best_ratio:
            best_ratio = ratio
            best_name = ws
    return best_name, best_ratio


def load_csv_games():
    """Load games from CSV file."""
    games = []
    with open(CSV_PATH, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Parse maccabi_scorers_parsed JSON (Maccabi-only scorers)
            scorers = []
            for field in ("maccabi_scorers_parsed", "scorers_parsed"):
                if row.get(field):
                    try:
                        parsed = json.loads(row[field])
                        scorers = [s["name"] for s in parsed if not is_junk_scorer(s.get("name", ""))]
                        break
                    except (json.JSONDecodeError, KeyError):
                        pass

            games.append({
                "date": row["date"].strip(),
                "date_iso": date_csv_to_iso(row["date"]),
                "season": row.get("season", "").strip(),
                "competition": row.get("competition", "").strip(),
                "opponent": row.get("opponent", "").strip(),
                "home_away": row.get("home_away", "").strip(),
                "maccabi_score": row.get("maccabi_score", "").strip(),
                "opponent_score": row.get("opponent_score", "").strip(),
                "scorers_raw": row.get("maccabi_scorers", row.get("scorers", "")).strip(),
                "scorers": scorers,
                "page": row.get("page", "").strip(),
            })
    return games


LEAGUE_COMPETITIONS = {"הליגה הארצית", "ליגה א", "ליגה לאומית"}


def fetch_wiki_games():
    """Fetch league-only football games from MaccabiPedia in the mandate period."""
    where = "Date >= '1930-01-01' AND Date <= '1948-12-31'"
    fields = "_pageName,Date,Opponent,HomeAway,Competition,ResultMaccabi,ResultOpponent,Season"
    games = fetch_all_cargo("Football_Games", fields, where=where, order_by="Date")
    # Filter to league competitions only — the book covers only official league games
    league_games = [g for g in games if g.get("Competition", "").strip() in LEAGUE_COMPETITIONS]
    filtered_out = len(games) - len(league_games)
    print(f"  Filtered out {filtered_out} non-league games (cups, friendlies, tours)")
    return league_games


def fetch_wiki_scorers(page_names_with_homeaway):
    """Fetch Maccabi goal scorers (EventType=3) for given game pages.

    page_names_with_homeaway: list of (page_name, home_away) tuples.
    Team=0 = home team, Team=1 = away team.
    When Maccabi is home (בית) → filter Team=0; when away (חוץ) → filter Team=1.
    """
    all_events = []
    batch_size = 5
    items = list(page_names_with_homeaway)
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        # Group by team number to minimize queries
        home_pages = [p for p, ha in batch if ha == 'בית']
        away_pages = [p for p, ha in batch if ha != 'בית']
        for pages, team_num in [(home_pages, 0), (away_pages, 1)]:
            if not pages:
                continue
            escaped = [p.replace("'", "\\'") for p in pages]
            in_clause = ",".join(f"'{p}'" for p in escaped)
            where = f"_pageName IN ({in_clause}) AND EventType=3 AND Team={team_num}"
            events = fetch_all_cargo("Games_Events", "_pageName,PlayerName,Minute", where=where)
            all_events.extend(events)
    return all_events


def main():
    print("Loading CSV games...")
    csv_games = load_csv_games()
    print(f"  Loaded {len(csv_games)} games from CSV")

    print("Fetching MaccabiPedia games (1930-1948)...")
    wiki_games = fetch_wiki_games()
    print(f"  Found {len(wiki_games)} games in MaccabiPedia")

    # Index wiki games by ISO date
    wiki_by_date = defaultdict(list)
    for wg in wiki_games:
        if wg.get("Date"):
            wiki_by_date[wg["Date"]].append(wg)

    # Match CSV games to wiki games
    matched = []       # (csv_game, wiki_game)
    csv_only = []      # csv_game (not in wiki)
    ambiguous = []     # csv_game with multiple wiki matches on same date

    for cg in csv_games:
        date_iso = cg["date_iso"]
        if not date_iso:
            csv_only.append(cg)
            continue

        candidates = wiki_by_date.get(date_iso, [])
        if not candidates:
            csv_only.append(cg)
            continue

        if len(candidates) == 1:
            matched.append((cg, candidates[0]))
            continue

        # Multiple games on same date - match by opponent similarity
        best_wg = None
        best_sim = 0
        for wg in candidates:
            sim = similarity(cg["opponent"], wg.get("Opponent", ""))
            if sim > best_sim:
                best_sim = sim
                best_wg = wg
        if best_wg and best_sim >= OPPONENT_SIMILARITY_THRESHOLD:
            matched.append((cg, best_wg))
        else:
            ambiguous.append((cg, candidates))

    # Collect page names for scorer queries
    wiki_page_names = [wg["_pageName"] for _, wg in matched]

    print(f"Fetching scorers for {len(wiki_page_names)} matched games...")
    wiki_events = fetch_wiki_scorers(wiki_page_names)
    print(f"  Found {len(wiki_events)} goal events")

    # Index wiki scorers by page name
    wiki_scorers_by_page = defaultdict(list)
    for ev in wiki_events:
        wiki_scorers_by_page[ev["_pageName"]].append(ev.get("PlayerName", ""))

    # Build the report
    lines = []
    lines.append("=" * 80)
    lines.append("דוח השוואת משחקי תקופת המנדט - ספר מול מכביפדיה")
    lines.append(f"Mandate Games Comparison Report")
    lines.append("=" * 80)
    lines.append("")

    # Summary stats
    total_csv = len(csv_games)
    total_matched = len(matched)
    total_csv_only = len(csv_only)
    total_ambiguous = len(ambiguous)

    lines.append("## SUMMARY ##")
    lines.append(f"Total games in CSV (book):        {total_csv}")
    lines.append(f"Total games in wiki (1930-1948):   {len(wiki_games)}")
    lines.append(f"Matched by date:                   {total_matched}")
    lines.append(f"In CSV but NOT in wiki:            {total_csv_only}")
    lines.append(f"Ambiguous (multiple wiki matches):  {total_ambiguous}")
    lines.append("")

    # Scorer statistics
    games_with_csv_scorers = 0
    games_with_wiki_scorers = 0
    games_both_have_scorers = 0
    games_csv_scorers_wiki_none = 0
    games_wiki_scorers_csv_none = 0
    total_csv_scorers = 0
    total_wiki_scorers = 0
    scorer_exact_matches = 0
    scorer_fuzzy_matches = 0
    scorer_csv_only = 0
    scorer_wiki_only = 0

    # Detailed game comparison
    game_details = []

    for cg, wg in matched:
        page_name = wg["_pageName"]
        csv_scorers = cg["scorers"]
        wiki_scorers = wiki_scorers_by_page.get(page_name, [])

        has_csv_scorers = len(csv_scorers) > 0
        has_wiki_scorers = len(wiki_scorers) > 0

        if has_csv_scorers:
            games_with_csv_scorers += 1
        if has_wiki_scorers:
            games_with_wiki_scorers += 1
        if has_csv_scorers and has_wiki_scorers:
            games_both_have_scorers += 1
        if has_csv_scorers and not has_wiki_scorers:
            games_csv_scorers_wiki_none += 1
        if has_wiki_scorers and not has_csv_scorers:
            games_wiki_scorers_csv_none += 1

        total_csv_scorers += len(csv_scorers)
        total_wiki_scorers += len(wiki_scorers)

        # Match scorers
        wiki_matched_indices = set()
        scorer_results = []

        for cs in csv_scorers:
            best_name, best_ratio = best_scorer_match(cs, wiki_scorers)
            if best_ratio >= 0.95:
                scorer_exact_matches += 1
                # Find the index to mark as matched
                for idx, ws in enumerate(wiki_scorers):
                    if ws == best_name and idx not in wiki_matched_indices:
                        wiki_matched_indices.add(idx)
                        break
                scorer_results.append(("exact", cs, best_name, best_ratio))
            elif best_ratio >= SCORER_SIMILARITY_THRESHOLD:
                scorer_fuzzy_matches += 1
                for idx, ws in enumerate(wiki_scorers):
                    if ws == best_name and idx not in wiki_matched_indices:
                        wiki_matched_indices.add(idx)
                        break
                scorer_results.append(("fuzzy", cs, best_name, best_ratio))
            else:
                scorer_csv_only += 1
                scorer_results.append(("csv_only", cs, best_name, best_ratio))

        # Wiki scorers not matched to any CSV scorer
        wiki_unmatched = [wiki_scorers[i] for i in range(len(wiki_scorers)) if i not in wiki_matched_indices]
        scorer_wiki_only += len(wiki_unmatched)

        # Score comparison
        score_match = (str(cg["maccabi_score"]) == str(wg.get("ResultMaccabi", ""))
                       and str(cg["opponent_score"]) == str(wg.get("ResultOpponent", "")))

        # Opponent comparison
        opp_sim = similarity(cg["opponent"], wg.get("Opponent", ""))
        opp_match = "exact" if opp_sim >= 0.95 else ("fuzzy" if opp_sim >= OPPONENT_SIMILARITY_THRESHOLD else "mismatch")

        game_details.append({
            "csv": cg,
            "wiki": wg,
            "score_match": score_match,
            "opp_match": opp_match,
            "opp_sim": opp_sim,
            "scorer_results": scorer_results,
            "wiki_unmatched_scorers": wiki_unmatched,
        })

    lines.append("## SCORER SUMMARY ##")
    lines.append(f"Matched games with scorers in CSV:    {games_with_csv_scorers}")
    lines.append(f"Matched games with scorers in wiki:   {games_with_wiki_scorers}")
    lines.append(f"Both have scorers:                    {games_both_have_scorers}")
    lines.append(f"CSV has scorers, wiki doesn't:        {games_csv_scorers_wiki_none}")
    lines.append(f"Wiki has scorers, CSV doesn't:        {games_wiki_scorers_csv_none}")
    lines.append(f"")
    lines.append(f"Total individual scorers in CSV:      {total_csv_scorers}")
    lines.append(f"Total individual scorers in wiki:     {total_wiki_scorers}")
    lines.append(f"Exact name matches (>=95%):           {scorer_exact_matches}")
    lines.append(f"Fuzzy name matches (50-95%):          {scorer_fuzzy_matches}")
    lines.append(f"CSV scorers not found in wiki:        {scorer_csv_only}")
    lines.append(f"Wiki scorers not found in CSV:        {scorer_wiki_only}")
    lines.append("")

    # ========== SECTION 1: Games NOT in wiki ==========
    lines.append("=" * 80)
    lines.append(f"## GAMES IN CSV BUT NOT IN MACCABIPEDIA ({total_csv_only} games) ##")
    lines.append("=" * 80)
    for cg in csv_only:
        score = f"{cg['maccabi_score']}-{cg['opponent_score']}"
        lines.append(f"  {cg['date']}  {cg['opponent']:30s}  {score:5s}  {cg['competition']}  (book p.{cg['page']})")
    lines.append("")

    # ========== SECTION 2: Ambiguous matches ==========
    if ambiguous:
        lines.append("=" * 80)
        lines.append(f"## AMBIGUOUS MATCHES ({total_ambiguous} games) ##")
        lines.append("=" * 80)
        for cg, candidates in ambiguous:
            lines.append(f"  CSV: {cg['date']}  {cg['opponent']}  {cg['maccabi_score']}-{cg['opponent_score']}")
            for wg in candidates:
                lines.append(f"    Wiki candidate: {wg['_pageName']}  opp={wg.get('Opponent','')}  {wg.get('ResultMaccabi','')}-{wg.get('ResultOpponent','')}")
        lines.append("")

    # ========== SECTION 3: Matched games with differences ==========
    lines.append("=" * 80)
    lines.append("## MATCHED GAMES - DETAILED COMPARISON ##")
    lines.append("=" * 80)

    # Group by status for readability
    games_with_issues = []
    games_clean = []

    for gd in game_details:
        has_issue = False
        if not gd["score_match"]:
            has_issue = True
        if gd["opp_match"] != "exact":
            has_issue = True
        if any(r[0] == "csv_only" for r in gd["scorer_results"]):
            has_issue = True
        if gd["wiki_unmatched_scorers"]:
            has_issue = True
        if any(r[0] == "fuzzy" for r in gd["scorer_results"]):
            has_issue = True

        if has_issue:
            games_with_issues.append(gd)
        else:
            games_clean.append(gd)

    lines.append("")
    lines.append(f"--- Games with differences ({len(games_with_issues)}) ---")
    lines.append("")

    for gd in games_with_issues:
        cg = gd["csv"]
        wg = gd["wiki"]
        lines.append(f"  DATE: {cg['date']}")
        lines.append(f"    CSV:  {cg['opponent']:30s}  {cg['maccabi_score']}-{cg['opponent_score']}  {cg['competition']}")
        lines.append(f"    Wiki: {wg.get('Opponent',''):30s}  {wg.get('ResultMaccabi','')}-{wg.get('ResultOpponent','')}  {wg.get('Competition','')}  [{wg['_pageName']}]")

        if not gd["score_match"]:
            lines.append(f"    *** SCORE MISMATCH: CSV={cg['maccabi_score']}-{cg['opponent_score']}  Wiki={wg.get('ResultMaccabi','')}-{wg.get('ResultOpponent','')}")

        if gd["opp_match"] != "exact":
            lines.append(f"    *** OPPONENT: {gd['opp_match'].upper()} (similarity={gd['opp_sim']:.0%})  CSV='{cg['opponent']}'  Wiki='{wg.get('Opponent','')}'")

        # Scorer details
        if gd["scorer_results"] or gd["wiki_unmatched_scorers"]:
            lines.append(f"    Scorers:")
            for status, csv_name, wiki_name, ratio in gd["scorer_results"]:
                if status == "exact":
                    lines.append(f"      ✓ exact:  '{normalize_name(csv_name)}' = '{normalize_name(wiki_name)}' ({ratio:.0%})")
                elif status == "fuzzy":
                    lines.append(f"      ~ fuzzy:  '{normalize_name(csv_name)}' ≈ '{normalize_name(wiki_name)}' ({ratio:.0%})")
                else:
                    lines.append(f"      ✗ CSV only: '{normalize_name(csv_name)}'  (best wiki match: '{normalize_name(wiki_name)}' {ratio:.0%})")
            for ws in gd["wiki_unmatched_scorers"]:
                lines.append(f"      ✗ Wiki only: '{ws}'")
        lines.append("")

    lines.append(f"--- Games matching cleanly ({len(games_clean)}) ---")
    lines.append("")
    for gd in games_clean:
        cg = gd["csv"]
        wg = gd["wiki"]
        n_csv_s = len(cg["scorers"])
        n_wiki_s = len(wiki_scorers_by_page.get(wg["_pageName"], []))
        score = f"{cg['maccabi_score']}-{cg['opponent_score']}"
        lines.append(f"  {cg['date']}  {cg['opponent']:30s}  {score:5s}  scorers: csv={n_csv_s} wiki={n_wiki_s}")
    lines.append("")

    # ========== SECTION 4: Wiki games NOT in CSV (same date range) ==========
    matched_wiki_pages = {wg["_pageName"] for _, wg in matched}
    wiki_not_in_csv = [wg for wg in wiki_games if wg["_pageName"] not in matched_wiki_pages]

    lines.append("=" * 80)
    lines.append(f"## WIKI GAMES NOT IN CSV ({len(wiki_not_in_csv)} games) ##")
    lines.append("  (These exist in MaccabiPedia but weren't in the book)")
    lines.append("=" * 80)
    for wg in wiki_not_in_csv:
        score = f"{wg.get('ResultMaccabi','')}-{wg.get('ResultOpponent','')}"
        lines.append(f"  {wg.get('Date','')}  {wg.get('Opponent',''):30s}  {score:5s}  {wg.get('Competition','')}")
    lines.append("")

    # Write report
    report = "\n".join(lines)
    with open(REPORT_PATH, "w", encoding="utf-8-sig") as f:
        f.write(report)
    print(f"\nReport written to {REPORT_PATH}")
    print(f"\n{'='*60}")
    print(report)


def h(text):
    """HTML-escape a string."""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def wiki_link(page_name):
    """Return an <a> tag linking to the wiki page."""
    url = WIKI_BASE + urllib.parse.quote(page_name.replace(" ", "_"), safe="/:()\"'")
    return f'<a href="{url}" target="_blank">{h(page_name)}</a>'


def build_html_report(
    csv_games, wiki_games, matched, near_miss, csv_only, ambiguous,
    game_details, wiki_scorers_by_page,
    games_with_issues, games_clean, wiki_not_in_csv,
    stats,
):
    total_csv = stats["total_csv"]
    total_wiki = stats["total_wiki"]
    total_matched = stats["total_matched"]
    total_csv_only = stats["total_csv_only"]
    total_ambiguous = stats["total_ambiguous"]
    games_with_csv_scorers = stats["games_with_csv_scorers"]
    games_with_wiki_scorers = stats["games_with_wiki_scorers"]
    games_both_have_scorers = stats["games_both_have_scorers"]
    games_csv_scorers_wiki_none = stats["games_csv_scorers_wiki_none"]
    games_wiki_scorers_csv_none = stats["games_wiki_scorers_csv_none"]
    total_csv_scorers = stats["total_csv_scorers"]
    total_wiki_scorers = stats["total_wiki_scorers"]
    scorer_exact_matches = stats["scorer_exact_matches"]
    scorer_fuzzy_matches = stats["scorer_fuzzy_matches"]
    scorer_csv_only_count = stats["scorer_csv_only"]
    scorer_wiki_only_count = stats["scorer_wiki_only"]

    parts = []
    parts.append("""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>דוח השוואת משחקי תקופת המנדט - מכביפדיה</title>
<style>
  :root {
    --green:  #1a7a2e; --green-bg:  #eafff0;
    --amber:  #b35900; --amber-bg:  #fff8ed;
    --red:    #c0392b; --red-bg:    #fff0ee;
    --blue:   #1a5276; --blue-bg:   #eaf2ff;
    --gray:   #555;    --gray-bg:   #f5f5f5;
    --border: #ddd;
  }
  * { box-sizing: border-box; }
  body {
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 14px;
    background: #f0f2f5;
    color: #222;
    margin: 0; padding: 20px;
  }
  h1 { font-size: 1.6em; margin-bottom: 4px; }
  h2 { font-size: 1.2em; margin: 24px 0 8px; border-bottom: 2px solid #ccc; padding-bottom: 4px; }
  h3 { font-size: 1em; margin: 16px 0 6px; color: #333; }
  a { color: #1a5276; }

  /* Summary cards */
  .cards { display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 20px; }
  .card {
    background: #fff; border-radius: 8px; border: 1px solid var(--border);
    padding: 14px 20px; min-width: 160px; flex: 1;
    text-align: center; box-shadow: 0 1px 4px rgba(0,0,0,.07);
  }
  .card .num { font-size: 2em; font-weight: 700; line-height: 1.1; }
  .card .lbl { font-size: .8em; color: #666; margin-top: 4px; }
  .card.green .num { color: var(--green); }
  .card.amber .num { color: var(--amber); }
  .card.red   .num { color: var(--red); }
  .card.blue  .num { color: var(--blue); }

  /* Tables */
  table { width: 100%; border-collapse: collapse; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,.07); margin-bottom: 16px; }
  th { background: #2c3e50; color: #fff; padding: 8px 10px; text-align: right; font-weight: 600; }
  td { padding: 7px 10px; border-bottom: 1px solid #eee; vertical-align: top; }
  tr:last-child td { border-bottom: none; }
  tr:hover td { background: #fafafa; }
  .badge {
    display: inline-block; border-radius: 4px; padding: 2px 7px;
    font-size: .78em; font-weight: 600; white-space: nowrap;
  }
  .badge-green  { background: var(--green-bg);  color: var(--green); }
  .badge-amber  { background: var(--amber-bg);  color: var(--amber); }
  .badge-red    { background: var(--red-bg);    color: var(--red); }
  .badge-blue   { background: var(--blue-bg);   color: var(--blue); }
  .badge-gray   { background: var(--gray-bg);   color: var(--gray); }

  /* Scorer pills */
  .scorers { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 4px; }
  .scorer-pill {
    border-radius: 12px; padding: 2px 9px; font-size: .8em; border: 1px solid;
  }
  .sp-exact { background: var(--green-bg); border-color: #9de0aa; color: var(--green); }
  .sp-fuzzy { background: var(--amber-bg); border-color: #f5c97a; color: var(--amber); }
  .sp-csv   { background: var(--red-bg);   border-color: #f5a99a; color: var(--red); }
  .sp-wiki  { background: var(--blue-bg);  border-color: #a9c4f5; color: var(--blue); }

  /* Sections */
  .section { background: #fff; border-radius: 10px; padding: 18px 20px; margin-bottom: 20px; box-shadow: 0 1px 4px rgba(0,0,0,.07); }

  /* Filter buttons */
  .filter-bar { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 10px; }
  .filter-btn {
    padding: 5px 14px; border-radius: 20px; border: 1px solid #ccc;
    background: #fff; cursor: pointer; font-size: .85em;
  }
  .filter-btn.active { background: #2c3e50; color: #fff; border-color: #2c3e50; }

  .issue-row { background: #fffdf0; }
  .score-mismatch-row { background: #fff5f5; }

  /* Collapsible */
  details summary { cursor: pointer; font-weight: 600; color: #2c3e50; }
  details[open] summary { margin-bottom: 8px; }

  /* Legend */
  .legend { display: flex; gap: 14px; flex-wrap: wrap; font-size: .82em; margin-bottom: 12px; align-items: center; }
  .legend-item { display: flex; align-items: center; gap: 5px; }

  @media (max-width: 600px) {
    .cards { flex-direction: column; }
    table { font-size: .78em; }
  }
</style>
</head>
<body>
<h1>⚽ דוח השוואת משחקי תקופת המנדט</h1>
<p style="color:#666; margin-top:0">ספר ← מכביפדיה | תקופה: 1930–1948 | Generated: today</p>
""")

    # ── Summary cards ──────────────────────────────────────────────────────────
    parts.append('<div class="cards">')
    parts.append(f'<div class="card blue"><div class="num">{total_csv}</div><div class="lbl">משחקים בספר</div></div>')
    parts.append(f'<div class="card blue"><div class="num">{total_wiki}</div><div class="lbl">משחקים במכביפדיה</div></div>')
    parts.append(f'<div class="card green"><div class="num">{total_matched}</div><div class="lbl">זוהו לפי תאריך</div></div>')
    total_near_miss = stats.get("total_near_miss", 0)
    if total_near_miss:
        parts.append(f'<div class="card amber"><div class="num">{total_near_miss}</div><div class="lbl">תאריך קרוב (±2 ימים)</div></div>')
    parts.append(f'<div class="card red"><div class="num">{total_csv_only}</div><div class="lbl">בספר — חסרים בוויקי</div></div>')
    parts.append(f'<div class="card amber"><div class="num">{len(wiki_not_in_csv)}</div><div class="lbl">בוויקי — לא בספר</div></div>')
    if total_ambiguous:
        parts.append(f'<div class="card amber"><div class="num">{total_ambiguous}</div><div class="lbl">עמביגואלי</div></div>')
    parts.append('</div>')

    # Scorer summary cards
    parts.append('<div class="cards">')
    parts.append(f'<div class="card green"><div class="num">{scorer_exact_matches}</div><div class="lbl">כובשים — התאמה מדויקת</div></div>')
    parts.append(f'<div class="card amber"><div class="num">{scorer_fuzzy_matches}</div><div class="lbl">כובשים — התאמה חלקית</div></div>')
    parts.append(f'<div class="card red"><div class="num">{scorer_csv_only_count}</div><div class="lbl">כובשים בספר בלבד</div></div>')
    parts.append(f'<div class="card blue"><div class="num">{scorer_wiki_only_count}</div><div class="lbl">כובשים בוויקי בלבד</div></div>')
    parts.append('</div>')

    # ── Section 0.5: Near-miss games (date off by 1-2 days) ──────────────────────
    if near_miss:
        parts.append(f'<div class="section">')
        parts.append(f'<h2>🟡 תאריך קרוב — ספר vs וויקי (±2 ימים) ({len(near_miss)})</h2>')
        parts.append('<p style="color:#888;font-size:.88em">משחקים שקיימים בשני המקורות אך עם הפרש של 1-2 ימים בתאריך. ייתכן שגיאת תאריך בספר או בוויקי.</p>')
        parts.append('<table><thead><tr><th>תאריך בספר</th><th>תאריך בוויקי</th><th>יריב</th><th>תוצאה (ספר)</th><th>הפרש</th><th>דף וויקי</th></tr></thead><tbody>')
        for cg, wg, delta in near_miss:
            csv_score = f"{cg['maccabi_score']}–{cg['opponent_score']}"
            parts.append(
                f'<tr class="issue-row">'
                f'<td>{h(cg["date"])}</td>'
                f'<td>{h(wg.get("Date",""))}</td>'
                f'<td>{h(cg["opponent"])}</td>'
                f'<td style="font-weight:600">{csv_score}</td>'
                f'<td style="text-align:center">Δ{delta}d</td>'
                f'<td style="font-size:.85em">{wiki_link(wg["_pageName"])}</td></tr>'
            )
        parts.append('</tbody></table></div>')

    # ── Section 1: CSV-only games (missing from wiki) ──────────────────────────
    parts.append(f'<div class="section">')
    parts.append(f'<h2>🔴 משחקים בספר שחסרים במכביפדיה ({total_csv_only})</h2>')
    parts.append('<table>')
    parts.append('<thead><tr><th>תאריך</th><th>עונה</th><th>יריב</th><th>תוצאה</th><th>תחרות</th><th>עמוד בספר</th></tr></thead><tbody>')
    for cg in csv_only:
        score = f"{cg['maccabi_score']}–{cg['opponent_score']}"
        scorers_txt = h(cg["scorers_raw"]) if cg["scorers_raw"] else ""
        comp_wiki = wiki_competition(cg["competition"], cg["season"])
        parts.append(
            f'<tr><td>{h(cg["date"])}</td><td>{h(cg["season"])}</td><td>{h(cg["opponent"])}</td>'
            f'<td style="font-weight:600">{score}</td>'
            f'<td>{h(comp_wiki)}</td>'
            f'<td style="text-align:center">{h(cg["page"])}</td></tr>'
        )
        if scorers_txt:
            parts.append(f'<tr><td colspan="6" style="color:#555;font-size:.85em;padding-top:2px;padding-right:30px">כובשים: {scorers_txt}</td></tr>')
    parts.append('</tbody></table></div>')

    # ── Section 2: Ambiguous ──────────────────────────────────────────────────
    if ambiguous:
        parts.append(f'<div class="section">')
        parts.append(f'<h2>⚠️ התאמות עמביגואליות ({total_ambiguous})</h2>')
        parts.append('<table><thead><tr><th>תאריך (ספר)</th><th>יריב (ספר)</th><th>תוצאה (ספר)</th><th>מועמדים בוויקי</th></tr></thead><tbody>')
        for cg, candidates in ambiguous:
            cands_html = "<br>".join(
                f'{wiki_link(wg["_pageName"])} — {h(wg.get("Opponent",""))} {wg.get("ResultMaccabi","")}-{wg.get("ResultOpponent","")}'
                for wg in candidates
            )
            parts.append(
                f'<tr><td>{h(cg["date"])}</td><td>{h(cg["opponent"])}</td>'
                f'<td>{cg["maccabi_score"]}–{cg["opponent_score"]}</td>'
                f'<td>{cands_html}</td></tr>'
            )
        parts.append('</tbody></table></div>')

    # ── Section 3: Matched games ───────────────────────────────────────────────
    parts.append('<div class="section">')
    parts.append(f'<h2>🔍 משחקים שזוהו — השוואה מפורטת ({total_matched})</h2>')

    # Legend
    parts.append('''<div class="legend">
      <strong>כובשים:</strong>
      <span class="legend-item"><span class="scorer-pill sp-exact">שם</span> התאמה מדויקת</span>
      <span class="legend-item"><span class="scorer-pill sp-fuzzy">שם</span> התאמה חלקית</span>
      <span class="legend-item"><span class="scorer-pill sp-csv">שם</span> בספר בלבד</span>
      <span class="legend-item"><span class="scorer-pill sp-wiki">שם</span> בוויקי בלבד</span>
    </div>''')

    # Sub-section: with differences
    parts.append(f'<details open><summary>משחקים עם הבדלים ({len(games_with_issues)})</summary>')
    parts.append('<table>')
    parts.append('<thead><tr><th>תאריך</th><th>יריב — ספר</th><th>יריב — וויקי</th><th>תוצאה ספר</th><th>תוצאה וויקי</th><th>דף</th><th>כובשים</th></tr></thead><tbody>')

    for gd in games_with_issues:
        cg = gd["csv"]
        wg = gd["wiki"]

        score_ok = gd["score_match"]
        opp_ok = gd["opp_match"]

        score_csv = f"{cg['maccabi_score']}–{cg['opponent_score']}"
        score_wiki = f"{wg.get('ResultMaccabi','')}–{wg.get('ResultOpponent','')}"

        score_cell_csv = f'<span class="badge badge-{"green" if score_ok else "red"}">{score_csv}</span>'
        score_cell_wiki = f'<span class="badge badge-{"green" if score_ok else "red"}">{score_wiki}</span>'

        if opp_ok == "exact":
            opp_csv_cell = f'<span class="badge badge-green">{h(cg["opponent"])}</span>'
            opp_wiki_cell = f'<span class="badge badge-green">{h(wg.get("Opponent",""))}</span>'
        elif opp_ok == "fuzzy":
            opp_csv_cell = f'<span class="badge badge-amber">{h(cg["opponent"])}</span>'
            opp_wiki_cell = f'<span class="badge badge-amber">{h(wg.get("Opponent",""))} <small>({gd["opp_sim"]:.0%})</small></span>'
        else:
            opp_csv_cell = f'<span class="badge badge-red">{h(cg["opponent"])}</span>'
            opp_wiki_cell = f'<span class="badge badge-red">{h(wg.get("Opponent",""))}</span>'

        # Scorer pills
        scorer_html_parts = ['<div class="scorers">']
        for status, csv_name, wiki_name, ratio in gd["scorer_results"]:
            cn = h(normalize_name(csv_name))
            wn = h(normalize_name(wiki_name)) if wiki_name else ""
            if status == "exact":
                scorer_html_parts.append(f'<span class="scorer-pill sp-exact" title="{cn}">{cn}</span>')
            elif status == "fuzzy":
                tip = f"{cn} ≈ {wn} ({ratio:.0%})"
                scorer_html_parts.append(f'<span class="scorer-pill sp-fuzzy" title="{tip}">{cn} <small>({ratio:.0%})</small></span>')
            else:
                tip = f"בספר בלבד: {cn}"
                scorer_html_parts.append(f'<span class="scorer-pill sp-csv" title="{tip}">{cn}</span>')
        for ws in gd["wiki_unmatched_scorers"]:
            scorer_html_parts.append(f'<span class="scorer-pill sp-wiki" title="בוויקי בלבד">{h(ws)}</span>')
        scorer_html_parts.append('</div>')
        scorers_cell = "".join(scorer_html_parts)

        row_class = "score-mismatch-row" if not score_ok else "issue-row"
        parts.append(
            f'<tr class="{row_class}">'
            f'<td style="white-space:nowrap">{h(cg["date"])}</td>'
            f'<td>{opp_csv_cell}</td>'
            f'<td>{opp_wiki_cell}<br><small style="color:#888">{wiki_link(wg["_pageName"])}</small></td>'
            f'<td>{score_cell_csv}</td>'
            f'<td>{score_cell_wiki}</td>'
            f'<td style="text-align:center">{h(cg["page"])}</td>'
            f'<td>{scorers_cell}</td>'
            f'</tr>'
        )
    parts.append('</tbody></table></details>')

    # Sub-section: clean
    parts.append(f'<details><summary>משחקים תואמים לחלוטין ({len(games_clean)})</summary>')
    parts.append('<table><thead><tr><th>תאריך</th><th>יריב</th><th>תוצאה</th><th>כובשים בספר</th><th>כובשים בוויקי</th><th>דף</th></tr></thead><tbody>')
    for gd in games_clean:
        cg = gd["csv"]
        wg = gd["wiki"]
        wiki_s = wiki_scorers_by_page.get(wg["_pageName"], [])
        csv_pills = "".join(f'<span class="scorer-pill sp-exact">{h(normalize_name(s))}</span>' for s in cg["scorers"])
        wiki_pills = "".join(f'<span class="scorer-pill sp-exact">{h(s)}</span>' for s in wiki_s)
        parts.append(
            f'<tr><td>{h(cg["date"])}</td>'
            f'<td>{h(cg["opponent"])}</td>'
            f'<td><span class="badge badge-green">{cg["maccabi_score"]}–{cg["opponent_score"]}</span></td>'
            f'<td><div class="scorers">{csv_pills or "—"}</div></td>'
            f'<td><div class="scorers">{wiki_pills or "—"}</div></td>'
            f'<td style="text-align:center">{h(cg["page"])}</td></tr>'
        )
    parts.append('</tbody></table></details>')
    parts.append('</div>')  # end section

    # ── Section 4: Wiki-only games ─────────────────────────────────────────────
    parts.append(f'<div class="section">')
    parts.append(f'<h2>🔵 משחקים בוויקי שאינם בספר ({len(wiki_not_in_csv)})</h2>')
    parts.append('<table><thead><tr><th>תאריך</th><th>עונה</th><th>יריב</th><th>תוצאה</th><th>תחרות</th><th>דף וויקי</th></tr></thead><tbody>')
    for wg in wiki_not_in_csv:
        score = f"{wg.get('ResultMaccabi','')}–{wg.get('ResultOpponent','')}"
        parts.append(
            f'<tr><td>{h(wg.get("Date",""))}</td>'
            f'<td>{h(wg.get("Season",""))}</td>'
            f'<td>{h(wg.get("Opponent",""))}</td>'
            f'<td>{score}</td>'
            f'<td>{h(wg.get("Competition",""))}</td>'
            f'<td style="font-size:.85em">{wiki_link(wg["_pageName"])}</td></tr>'
        )
    parts.append('</tbody></table></div>')

    parts.append('</body></html>')
    return "".join(parts)


def main():
    print("Loading CSV games...")
    csv_games = load_csv_games()
    print(f"  Loaded {len(csv_games)} games from CSV")

    print("Fetching MaccabiPedia games (1930-1948)...")
    wiki_games = fetch_wiki_games()
    print(f"  Found {len(wiki_games)} games in MaccabiPedia")

    # Index wiki games by ISO date
    wiki_by_date = defaultdict(list)
    for wg in wiki_games:
        if wg.get("Date"):
            wiki_by_date[wg["Date"]].append(wg)

    # Match CSV games to wiki games
    matched = []       # (csv_game, wiki_game)
    near_miss = []     # (csv_game, wiki_game, day_delta) — date off by 1-2 days
    csv_only = []      # csv_game (not in wiki)
    ambiguous = []     # csv_game with multiple wiki matches on same date

    for cg in csv_games:
        date_iso = cg["date_iso"]
        if not date_iso:
            csv_only.append(cg)
            continue

        candidates = wiki_by_date.get(date_iso, [])
        if not candidates:
            # Try ±2 days as near-miss fallback
            try:
                d = datetime.date.fromisoformat(date_iso)
                nearby = []
                for delta in range(1, 3):
                    for dd in [d + datetime.timedelta(days=delta), d - datetime.timedelta(days=delta)]:
                        for wg in wiki_by_date.get(dd.isoformat(), []):
                            nearby.append((wg, delta))
                if nearby:
                    best_wg, best_delta, best_sim = None, 0, 0
                    for wg, delta in nearby:
                        sim = similarity(cg["opponent"], wg.get("Opponent", ""))
                        if sim > best_sim:
                            best_sim = sim
                            best_wg = wg
                            best_delta = delta
                    if best_wg and best_sim >= OPPONENT_SIMILARITY_THRESHOLD:
                        near_miss.append((cg, best_wg, best_delta))
                        continue
            except ValueError:
                pass
            csv_only.append(cg)
            continue

        if len(candidates) == 1:
            matched.append((cg, candidates[0]))
            continue

        # Multiple games on same date - match by opponent similarity
        best_wg = None
        best_sim = 0
        for wg in candidates:
            sim = similarity(cg["opponent"], wg.get("Opponent", ""))
            if sim > best_sim:
                best_sim = sim
                best_wg = wg
        if best_wg and best_sim >= OPPONENT_SIMILARITY_THRESHOLD:
            matched.append((cg, best_wg))
        else:
            ambiguous.append((cg, candidates))

    # Collect (page_name, home_away) for scorer queries — filter to Maccabi goals only
    wiki_page_names_ha = [(wg["_pageName"], cg["home_away"]) for cg, wg in matched]
    wiki_page_names_ha += [(wg["_pageName"], cg["home_away"]) for cg, wg, _ in near_miss]
    wiki_page_names = [p for p, _ in wiki_page_names_ha]

    print(f"Fetching scorers for {len(wiki_page_names)} matched games...")
    wiki_events = fetch_wiki_scorers(wiki_page_names_ha)
    print(f"  Found {len(wiki_events)} goal events")

    # Index wiki scorers by page name
    wiki_scorers_by_page = defaultdict(list)
    for ev in wiki_events:
        wiki_scorers_by_page[ev["_pageName"]].append(ev.get("PlayerName", ""))

    # ── Compute all stats and game details ─────────────────────────────────────
    games_with_csv_scorers = 0
    games_with_wiki_scorers = 0
    games_both_have_scorers = 0
    games_csv_scorers_wiki_none = 0
    games_wiki_scorers_csv_none = 0
    total_csv_scorers = 0
    total_wiki_scorers = 0
    scorer_exact_matches = 0
    scorer_fuzzy_matches = 0
    scorer_csv_only = 0
    scorer_wiki_only = 0

    game_details = []

    for cg, wg in matched:
        page_name = wg["_pageName"]
        csv_scorers = cg["scorers"]
        wiki_scorers = wiki_scorers_by_page.get(page_name, [])

        has_csv_scorers = len(csv_scorers) > 0
        has_wiki_scorers = len(wiki_scorers) > 0

        if has_csv_scorers:
            games_with_csv_scorers += 1
        if has_wiki_scorers:
            games_with_wiki_scorers += 1
        if has_csv_scorers and has_wiki_scorers:
            games_both_have_scorers += 1
        if has_csv_scorers and not has_wiki_scorers:
            games_csv_scorers_wiki_none += 1
        if has_wiki_scorers and not has_csv_scorers:
            games_wiki_scorers_csv_none += 1

        total_csv_scorers += len(csv_scorers)
        total_wiki_scorers += len(wiki_scorers)

        wiki_matched_indices = set()
        scorer_results = []

        for cs in csv_scorers:
            best_name, best_ratio = best_scorer_match(cs, wiki_scorers)
            if best_ratio >= 0.95:
                scorer_exact_matches += 1
                for idx, ws in enumerate(wiki_scorers):
                    if ws == best_name and idx not in wiki_matched_indices:
                        wiki_matched_indices.add(idx)
                        break
                scorer_results.append(("exact", cs, best_name, best_ratio))
            elif best_ratio >= SCORER_SIMILARITY_THRESHOLD:
                scorer_fuzzy_matches += 1
                for idx, ws in enumerate(wiki_scorers):
                    if ws == best_name and idx not in wiki_matched_indices:
                        wiki_matched_indices.add(idx)
                        break
                scorer_results.append(("fuzzy", cs, best_name, best_ratio))
            else:
                scorer_csv_only += 1
                scorer_results.append(("csv_only", cs, best_name, best_ratio))

        wiki_unmatched = [wiki_scorers[i] for i in range(len(wiki_scorers)) if i not in wiki_matched_indices]
        scorer_wiki_only += len(wiki_unmatched)

        score_match = (str(cg["maccabi_score"]) == str(wg.get("ResultMaccabi", ""))
                       and str(cg["opponent_score"]) == str(wg.get("ResultOpponent", "")))

        opp_sim = similarity(cg["opponent"], wg.get("Opponent", ""))
        opp_match = "exact" if opp_sim >= 0.95 else ("fuzzy" if opp_sim >= OPPONENT_SIMILARITY_THRESHOLD else "mismatch")

        game_details.append({
            "csv": cg,
            "wiki": wg,
            "score_match": score_match,
            "opp_match": opp_match,
            "opp_sim": opp_sim,
            "scorer_results": scorer_results,
            "wiki_unmatched_scorers": wiki_unmatched,
        })

    games_with_issues = []
    games_clean = []
    for gd in game_details:
        has_issue = (
            not gd["score_match"]
            or gd["opp_match"] != "exact"
            or any(r[0] == "csv_only" for r in gd["scorer_results"])
            or gd["wiki_unmatched_scorers"]
            or any(r[0] == "fuzzy" for r in gd["scorer_results"])
        )
        (games_with_issues if has_issue else games_clean).append(gd)

    matched_wiki_pages = {wg["_pageName"] for _, wg in matched}
    matched_wiki_pages |= {wg["_pageName"] for _, wg, _ in near_miss}
    wiki_not_in_csv = [wg for wg in wiki_games if wg["_pageName"] not in matched_wiki_pages]

    stats = dict(
        total_csv=len(csv_games), total_wiki=len(wiki_games),
        total_matched=len(matched), total_near_miss=len(near_miss), total_csv_only=len(csv_only),
        total_ambiguous=len(ambiguous),
        games_with_csv_scorers=games_with_csv_scorers,
        games_with_wiki_scorers=games_with_wiki_scorers,
        games_both_have_scorers=games_both_have_scorers,
        games_csv_scorers_wiki_none=games_csv_scorers_wiki_none,
        games_wiki_scorers_csv_none=games_wiki_scorers_csv_none,
        total_csv_scorers=total_csv_scorers,
        total_wiki_scorers=total_wiki_scorers,
        scorer_exact_matches=scorer_exact_matches,
        scorer_fuzzy_matches=scorer_fuzzy_matches,
        scorer_csv_only=scorer_csv_only,
        scorer_wiki_only=scorer_wiki_only,
    )

    # ── Build plain-text report ────────────────────────────────────────────────
    lines = []
    lines.append("=" * 80)
    lines.append("Mandate Games Comparison Report")
    lines.append("=" * 80)
    lines.append(f"Games in CSV: {len(csv_games)}  |  In wiki: {len(wiki_games)}  |  Matched: {len(matched)}  |  Near-miss (±2d): {len(near_miss)}  |  CSV-only: {len(csv_only)}")
    lines.append(f"Scorers — exact: {scorer_exact_matches}  fuzzy: {scorer_fuzzy_matches}  CSV-only: {scorer_csv_only}  wiki-only: {scorer_wiki_only}")
    lines.append("")
    lines.append(f"NEAR-MISS GAMES — date off by 1-2 days ({len(near_miss)}):")
    for cg, wg, delta in near_miss:
        lines.append(f"  CSV {cg['date']}  {cg['opponent']:30s}  {cg['maccabi_score']}-{cg['opponent_score']}")
        lines.append(f"  Wiki {wg.get('Date','')}  {wg.get('Opponent',''):30s}  {wg.get('ResultMaccabi','')}-{wg.get('ResultOpponent','')}  (Δ{delta}d)")
    lines.append("")
    lines.append(f"GAMES IN CSV BUT NOT IN MACCABIPEDIA ({len(csv_only)}):")
    for cg in csv_only:
        lines.append(f"  {cg['date']}  {cg['opponent']:30s}  {cg['maccabi_score']}-{cg['opponent_score']}  {cg['competition']}  (p.{cg['page']})")
    lines.append("")
    lines.append(f"GAMES WITH DIFFERENCES ({len(games_with_issues)}):")
    for gd in games_with_issues:
        cg = gd["csv"]; wg = gd["wiki"]
        lines.append(f"  {cg['date']}  CSV={cg['opponent']} {cg['maccabi_score']}-{cg['opponent_score']}  "
                     f"Wiki={wg.get('Opponent','')} {wg.get('ResultMaccabi','')}-{wg.get('ResultOpponent','')}")
        for status, cn, wn, ratio in gd["scorer_results"]:
            tag = {"exact": "=", "fuzzy": "~", "csv_only": "✗"}[status]
            lines.append(f"    {tag} {normalize_name(cn)}" + (f" ≈ {normalize_name(wn)} ({ratio:.0%})" if status == "fuzzy" else ""))
        for ws in gd["wiki_unmatched_scorers"]:
            lines.append(f"    + {ws} (wiki only)")

    with open(REPORT_PATH, "w", encoding="utf-8-sig") as f:
        f.write("\n".join(lines))
    print(f"Text report → {REPORT_PATH}")

    # ── Build HTML report ──────────────────────────────────────────────────────
    html = build_html_report(
        csv_games, wiki_games, matched, near_miss, csv_only, ambiguous,
        game_details, wiki_scorers_by_page,
        games_with_issues, games_clean, wiki_not_in_csv,
        stats,
    )
    with open(HTML_REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML report → {HTML_REPORT_PATH}")


if __name__ == "__main__":
    main()
