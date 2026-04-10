"""
Report football player profiles where FullForeignName (Latin name) is empty.
Writes docs/profiles_missing_latin_name.csv for manual research.

How to run
----------
    uv run python -m maccabipediabot.maintenance.football.report_profiles_missing_latin_name

After filling in the ProposedLatinName column, run fix_profiles_latin_names.py.
"""
import csv
import sys
import requests

CARGO_EXPORT_URL = "https://www.maccabipedia.co.il/index.php"
OUTPUT_CSV = "docs/profiles_missing_latin_name.csv"


def query_profiles_missing_latin_name() -> list[dict]:
    params = {
        "title": "Special:CargoExport",
        "format": "json",
        "tables": "Profiles",
        "fields": "_pageName,FullForeignName",
        "where": "FullForeignName IS NULL OR FullForeignName=''",
        "limit": "500",
        "order by": "_pageName",
    }
    response = requests.get(CARGO_EXPORT_URL, params=params, timeout=30)
    if response.status_code != 200 or "application/json" not in response.headers.get("Content-Type", ""):
        raise RuntimeError(
            f"Unexpected Cargo response: status={response.status_code}\n{response.text[:500]}"
        )
    return response.json()


def main() -> None:
    profiles = query_profiles_missing_latin_name()
    print(f"Found {len(profiles)} profiles missing Latin name")

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f, fieldnames=["pageName", "FullForeignName", "ProposedLatinName"]
        )
        writer.writeheader()
        for profile in profiles:
            writer.writerow({
                "pageName": profile.get("_pageName", ""),
                "FullForeignName": profile.get("FullForeignName", "") or "",
                "ProposedLatinName": "",
            })

    print(f"Written to {OUTPUT_CSV}")
    print("Fill in ProposedLatinName column (sources: Transfermarkt, Soccerway, Wikipedia, Wikidata)")
    print("Then run fix_profiles_latin_names.py")


if __name__ == "__main__":
    sys.exit(main())
