"""
Report football player profiles where PreferFoot (dominant foot) is empty.
Writes docs/profiles_missing_dominant_foot.csv for manual research.

How to run
----------
    uv run python -m maccabipediabot.maintenance.football.report_profiles_missing_dominant_foot

After filling in the ProposedFoot column (ימין/שמאל/שתיים), run fix_profiles_dominant_foot.py.
"""
import csv
import sys
import requests

CARGO_EXPORT_URL = "https://www.maccabipedia.co.il/index.php"
OUTPUT_CSV = "docs/profiles_missing_dominant_foot.csv"


def query_profiles_missing_dominant_foot() -> list[dict]:
    params = {
        "title": "Special:CargoExport",
        "format": "json",
        "tables": "Profiles",
        "fields": "_pageName,PreferFoot",
        "where": "PreferFoot IS NULL OR PreferFoot='' OR PreferFoot='0'",
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
    profiles = query_profiles_missing_dominant_foot()
    print(f"Found {len(profiles)} profiles missing dominant foot")

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f, fieldnames=["pageName", "PreferFoot", "ProposedFoot"]
        )
        writer.writeheader()
        for profile in profiles:
            writer.writerow({
                "pageName": profile.get("_pageName", ""),
                "PreferFoot": profile.get("PreferFoot", "") or "",
                "ProposedFoot": "",
            })

    print(f"Written to {OUTPUT_CSV}")
    print("Fill in ProposedFoot column: ימין / שמאל / שתיים (sources: Transfermarkt, Soccerway, Wikipedia)")
    print("Then run fix_profiles_dominant_foot.py")


if __name__ == "__main__":
    sys.exit(main())
