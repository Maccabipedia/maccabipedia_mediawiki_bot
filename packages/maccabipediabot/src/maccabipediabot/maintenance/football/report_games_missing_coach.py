"""
Report historical football games (pre-1963) with no recorded Maccabi coach.
Writes docs/games_missing_coach.csv as a research checklist.

How to run
----------
    uv run python -m maccabipediabot.maintenance.football.report_games_missing_coach

Research sources (see .claude/maccabipedia_research_sources.md):
  - JPress: https://www.jpress.org.il
  - RSSSF Israel: http://www.rsssf.com/tablesil/
  - Maccabi TLV archives
"""
import csv
import sys
import requests

CARGO_EXPORT_URL = "https://www.maccabipedia.co.il/index.php"
OUTPUT_CSV = "docs/games_missing_coach.csv"


def query_games_missing_coach() -> list[dict]:
    params = {
        "title": "Special:CargoExport",
        "format": "json",
        "tables": "Football_Games",
        "fields": "_pageName,Date,Competition,CoachMaccabi",
        "where": "CoachMaccabi IS NULL AND Date < '1963-01-01'",
        "limit": "500",
        "order by": "Date",
    }
    response = requests.get(CARGO_EXPORT_URL, params=params, timeout=30)
    if response.status_code != 200 or "application/json" not in response.headers.get("Content-Type", ""):
        raise RuntimeError(
            f"Unexpected Cargo response: status={response.status_code}\n{response.text[:500]}"
        )
    return response.json()


def main() -> None:
    games = query_games_missing_coach()
    print(f"Found {len(games)} historical games (pre-1963) missing Maccabi coach")

    fieldnames = ["pageName", "Date", "Competition", "CoachMaccabi", "ResearchedCoach", "Source"]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for game in games:
            writer.writerow({
                "pageName": game.get("_pageName", ""),
                "Date": game.get("Date", ""),
                "Competition": game.get("Competition", ""),
                "CoachMaccabi": game.get("CoachMaccabi", "") or "",
                "ResearchedCoach": "",
                "Source": "",
            })

    print(f"Written to {OUTPUT_CSV}")
    print("Fill in ResearchedCoach and Source columns via JPress / RSSSF / Maccabi archives")


if __name__ == "__main__":
    sys.exit(main())
