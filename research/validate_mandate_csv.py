"""
Validate the extracted mandate-era games CSV before upload.

Checks:
  - Required fields are present and non-empty
  - Date format is DD-MM-YYYY and values are plausible
  - home_away is 'בית' or 'חוץ'
  - Scores are non-negative integers
  - Season format is YYYY/YY or YYYY
  - No duplicate (date, home_away, opponent) rows
  - Flags suspicious rows: score outliers, unknown opponents, reversed parens in scorers

Usage:
    python research/validate_mandate_csv.py
    python research/validate_mandate_csv.py --show-all   # print every row's issues, not just summary
"""

import csv
import re
import sys
from collections import Counter
from pathlib import Path

CSV_PATH = Path(__file__).parent.parent / "data" / "mandate_games_maccabi_ta.csv"

REQUIRED_FIELDS = ['date', 'season', 'competition', 'opponent', 'home_away', 'maccabi_score', 'opponent_score']
DATE_RE = re.compile(r'^(\d{2})-(\d{2})-(\d{4})$')
SEASON_RE = re.compile(r'^\d{4}(?:/\d{2,4})?$')
VALID_HOME_AWAY = {'בית', 'חוץ', 'נייטרלי'}


def validate_row(row, idx):
    issues = []

    # Required fields
    for field in REQUIRED_FIELDS:
        if not row.get(field, '').strip():
            issues.append(f"missing required field '{field}'")

    # Date format and range
    date_str = row.get('date', '')
    date_m = DATE_RE.match(date_str)
    if not date_m:
        issues.append(f"bad date format: {date_str!r} (expected DD-MM-YYYY)")
    else:
        day, month, year = int(date_m.group(1)), int(date_m.group(2)), int(date_m.group(3))
        if not (1 <= day <= 31):
            issues.append(f"day out of range: {day}")
        if not (1 <= month <= 12):
            issues.append(f"month out of range: {month}")
        if not (1925 <= year <= 1950):
            issues.append(f"year implausible for mandate era: {year}")

    # Season format
    season = row.get('season', '')
    if season and not SEASON_RE.match(season):
        issues.append(f"bad season format: {season!r}")

    # home_away
    ha = row.get('home_away', '')
    if ha and ha not in VALID_HOME_AWAY:
        issues.append(f"unexpected home_away value: {ha!r}")

    # Scores
    for field in ('maccabi_score', 'opponent_score'):
        val = row.get(field, '')
        try:
            s = int(val)
            if s < 0:
                issues.append(f"{field} is negative: {val}")
            if s > 20:
                issues.append(f"{field} suspiciously high: {val} (possible footnote contamination)")
        except (ValueError, TypeError):
            issues.append(f"{field} is not an integer: {val!r}")

    # Unknown opponent
    if row.get('opponent', '').strip() == '?':
        issues.append("opponent is unresolved '?'")

    # Reversed parentheses in scorers (PDF RTL artifact)
    scorers = row.get('scorers', '')
    if ')' in scorers and '(' not in scorers:
        issues.append("scorers has reversed parentheses (RTL artifact)")
    if scorers and re.search(r'\d+\)\s*\(', scorers):
        issues.append("scorers has reversed paren pattern e.g. '77) ('")

    return issues


def main():
    show_all = '--show-all' in sys.argv

    if not CSV_PATH.exists():
        print(f"ERROR: CSV not found at {CSV_PATH}")
        sys.exit(1)

    with open(CSV_PATH, encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Loaded {len(rows)} rows from {CSV_PATH.name}\n")

    # Per-row validation
    all_issues = []
    for idx, row in enumerate(rows, 1):
        issues = validate_row(row, idx)
        if issues:
            all_issues.append((idx, row, issues))
            if show_all or len(all_issues) <= 30:
                date = row.get('date', '?')
                opp = row.get('opponent', '?')
                ha = row.get('home_away', '?')
                ms = row.get('maccabi_score', '?')
                os_ = row.get('opponent_score', '?')
                season = row.get('season', '?')
                print(f"  Row {idx:3d} | {date} | {ha} vs {opp} {ms}–{os_} [{season}]")
                for issue in issues:
                    print(f"           ⚠ {issue}")

    if not show_all and len(all_issues) > 30:
        print(f"  ... and {len(all_issues) - 30} more rows with issues (run with --show-all)")

    # Duplicate detection
    print()
    seen = {}
    duplicates = []
    for idx, row in enumerate(rows, 1):
        key = (row.get('date'), row.get('home_away'), row.get('opponent'))
        if key in seen:
            duplicates.append((seen[key], idx, key))
        else:
            seen[key] = idx
    if duplicates:
        print(f"Duplicate rows ({len(duplicates)}):")
        for r1, r2, key in duplicates:
            print(f"  Rows {r1} and {r2}: {key}")
    else:
        print("No duplicate (date, home_away, opponent) rows found.")

    # Summary statistics
    print()
    seasons = Counter(r['season'] for r in rows)
    print("Games per season:")
    for season, count in sorted(seasons.items()):
        print(f"  {season}: {count}")

    opponents = Counter(r['opponent'] for r in rows)
    print(f"\nUnique opponents: {len(opponents)}")
    print("Opponents:")
    for opp, count in sorted(opponents.items(), key=lambda x: -x[1]):
        print(f"  {opp}: {count}")

    competitions = Counter(r['competition'] for r in rows)
    print(f"\nCompetitions:")
    for comp, count in sorted(competitions.items(), key=lambda x: -x[1]):
        print(f"  {comp}: {count}")

    # Final verdict
    print()
    n_issues = len(all_issues)
    n_dupes = len(duplicates)
    if n_issues == 0 and n_dupes == 0:
        print(f"✓ All {len(rows)} rows valid — ready for upload.")
    else:
        print(f"⚠ {n_issues} rows with issues, {n_dupes} duplicates — review before upload.")


if __name__ == '__main__':
    main()
