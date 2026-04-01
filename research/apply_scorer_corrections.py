"""
Apply scorer name corrections to mandate_games_with_scorers.csv.

Corrections come from two rounds of manual review:
 - Round 1: fuzzy matches confirmed (use wiki spelling)
 - Round 2: page-by-page review of undecided names

For each game row, the maccabi_scorers_parsed and opponent_scorers_parsed JSON columns
are updated: corrected names get the canonical wiki spelling, junk names are removed.

Usage:
    python research/apply_scorer_corrections.py
"""

import csv
import json
import re
from pathlib import Path

INPUT_CSV  = Path("data/mandate_games_with_scorers.csv")
OUTPUT_CSV = Path("data/mandate_games_with_scorers.csv")  # in-place

# ---------------------------------------------------------------------------
# All approved corrections (csv normalized name → wiki name)
# ---------------------------------------------------------------------------
USE_WIKI = {
    "אברהם רזניק 02":                  "אברהם רזניק",
    "גאול מכליס 66":                   "גאול מכליס",
    "מרדכי צנובסקי":                   "מרדכי פצנובסקי",
    "יוס מרימוביץ":                    "יוסף מרימוביץ",
    "הרצל ריצנר":                      "הרצל פריצנר",
    "שמואל בכ ר":                      "שמואל בכר",
    "אלי וקס":                         "אלי פוקס",
    "י קב זליבנסקי":                   "יעקב זליבנסקי",
    "נתן נץ":                          "נתן פנץ",
    "בן-ציון א שטיין":                 "בן ציון אפשטיין",
    "רי נוי לד":                       "פרי נויפלד",
    "רי נוי לד 09":                    "פרי נויפלד",
    "אלי זר ש יגל":                    "אליעזר שפיגל",
    "סטודינסקי":                       "צבי סטודינסקי",
    "צבי ארליך דוקטור":                "צבי ארליך",
    "זליבנסק י":                       "אריה זליבנסקי",
    "יהוש גלזר":                       "שייע גלזר",
    # round 2
    "בן-ציון א שטיין":                 "בן ציון אפשטיין",  # duplicate, consistent
}

JUNK = {
    "זליבנסקי",
    "רוברט מורגן",
    "מרדכי צנובסקי או מנחם חרש",
    "נחס ידלר",
    "אמרה י קב י",
    "אמרה י קבי",
    "צבי וול וביץ",
    "הו סק",
    "טכני",
    "זוני",
    "דב שונשיין",
    "צבי",
    "שמואל בן -דרור 04",
    "יוס",
    "שמואל ישראלי",
    "או",
    "הקיצוני השמאלי",
    "המקשר השמאלי",
    "המקשר השמאל י",
    "יושה",
    "יוש ה",
}


def normalize(name):
    if not name:
        return ""
    name = re.sub(r'[()?\[\]"\'׳\u05F3]', '', name)
    name = re.sub(r'^\d+\s*', '', name)
    name = name.strip()
    name = re.sub(r'\s*\d+$', '', name)
    return re.sub(r'\s+', ' ', name).strip()


# Normalize the correction keys once
USE_WIKI_NORM = {normalize(k): v for k, v in USE_WIKI.items()}
JUNK_NORM     = {normalize(j) for j in JUNK}


def is_junk(name):
    """Return True if name is a parse artifact with no Hebrew content."""
    n = normalize(name)
    if not n or len(n) <= 1:
        return True
    if re.match(r'^[\d\s]+$', n):
        return True
    if re.match(r'^[()?\[\]"\',.\s]+$', n):
        return True
    if not re.search(r'[\u05D0-\u05EA]', n):  # no Hebrew letters
        return True
    return False


def apply_corrections(parsed_json):
    """
    Given a JSON string of [{name, minute}, ...], return corrected list.
    Names matching USE_WIKI_NORM are replaced; names in JUNK_NORM or is_junk() are dropped.
    """
    try:
        entries = json.loads(parsed_json)
    except (json.JSONDecodeError, TypeError):
        return parsed_json

    corrected = []
    for entry in entries:
        raw = entry.get("name", "")
        norm = normalize(raw)
        if is_junk(raw) or norm in JUNK_NORM:
            continue
        entry = dict(entry)
        if norm in USE_WIKI_NORM:
            entry["name"] = USE_WIKI_NORM[norm]
        else:
            # Store the cleaned-up form (strips parens, stray digits, etc.)
            entry["name"] = norm
        corrected.append(entry)
    return json.dumps(corrected, ensure_ascii=False)


def main():
    with open(INPUT_CSV, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
        fieldnames = list(rows[0].keys()) if rows else []

    stats = {"corrected": 0, "dropped": 0}

    for row in rows:
        for field in ("maccabi_scorers_parsed", "opponent_scorers_parsed"):
            if not row.get(field):
                continue
            original = row[field]
            updated  = apply_corrections(original)
            if updated != original:
                orig_names = [e["name"] for e in json.loads(original)]
                upd_names  = [e["name"] for e in json.loads(updated)]
                dropped    = [n for n in orig_names if n not in upd_names and
                              normalize(n) in JUNK_NORM]
                changed    = [(o, u) for o, u in zip(orig_names, upd_names) if o != u]
                for o, u in changed:
                    print(f"  [rename] {row['date']} {field}: {o!r} → {u!r}")
                    stats["corrected"] += 1
                for d in dropped:
                    print(f"  [drop]   {row['date']} {field}: {d!r}")
                    stats["dropped"] += 1
                row[field] = updated

    with open(OUTPUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nDone. {stats['corrected']} names corrected, {stats['dropped']} names dropped.")
    print(f"Written to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
