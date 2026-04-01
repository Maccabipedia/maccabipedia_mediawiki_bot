"""
Parse scorer names and minutes from the CSV scorers field.

Handles formats like:
  - "שמעון לאומי (85), אליהו רופל (30)"
  - "נתן פנץ (9) יוסף מרימוביץ' (11), ..."
  - "בן-ציון אפשטיין (?), דבורקין (40)"

Outputs: new CSV with added `scorers_parsed` column (JSON format)

Usage:
    python research/parse_scorers.py
"""

import csv
import re
import json
from pathlib import Path

CSV_PATH = Path(__file__).parent.parent / "data" / "mandate_games_maccabi_ta.csv"
OUTPUT_PATH = Path(__file__).parent.parent / "data" / "mandate_games_with_scorers.csv"


def parse_scorers(text):
    """
    Parse scorer text into list of {name, minute} dicts.

    Handles multiple formats from the PDF:
      - "Name (minute)" — clean format
      - "Name )minute(" — RTL-reversed parens
      - "Name [minute]" — bracket format
      - "Name minute" — space-separated
      - "Name, minute" — comma-separated
      - "Name (?) — unknown minute
      - Mixed: separators can be commas, spaces, or unclear

    Returns: list of {"name": str, "minute": int or None}
    """
    if not text or not text.strip():
        return []

    scorers = []

    # Step 1: Normalize various bracket/paren formats to standard (minute)
    # RTL reversed: )NUM( → (NUM)
    text = re.sub(r'\)([0-9?]+)\(', r'(\1)', text)
    # Brackets: [NUM] → (NUM)
    text = re.sub(r'\[([0-9?]+)\]', r'(\1)', text)
    # Strip stray font markers: )ע(, )פ( (PDF encoding artifacts) → remove
    text = re.sub(r'\)[א-ת]\(', '', text)

    # Step 2: Split by comma and/or by patterns like ") NAME"
    # Split by comma, or by ") " followed by Hebrew letter
    segments = re.split(r',|\)\s+(?=[א-ת\w])', text)

    for segment in segments:
        segment = segment.strip()
        if not segment:
            continue

        # Try to extract: NAME (MINUTE) or NAME MINUTE
        # Pattern 1: "Name (minute)" or "Name (?)"
        m = re.search(r'([\u05D0-\u05EA\w\s\-\',\.]*?)\s*\(([0-9?]+)\)', segment)
        if m:
            name = m.group(1).strip()
            minute_str = m.group(2)
        else:
            # Pattern 2: "Name minute" — look for trailing digit(s)
            m = re.search(r'([\u05D0-\u05EA\w\s\-\',\.]+?)\s+([0-9?]+)\s*$', segment)
            if m:
                name = m.group(1).strip()
                minute_str = m.group(2)
            else:
                # No minute found — use entire segment as name with unknown minute
                name = segment.strip()
                minute_str = None

        if not name or name == '?':
            continue

        # Clean up PDF artifacts from name
        name = re.sub(r'\s*[)\[\]ע-פ]+\s*', ' ', name)  # Remove stray parens/brackets/font chars
        name = re.sub(r'\s+', ' ', name).strip()  # Normalize whitespace

        # Handle appended digits: "זליבנסקי31" → name="זליבנסקי", minute=31
        if not minute_str:
            m = re.search(r'([\u05D0-\u05EA\w\s\-\']+?)\s*([0-9]+)\s*$', name)
            if m and len(m.group(2)) <= 2:  # digit chunk ≤ 2 chars is likely minute
                name = m.group(1).strip()
                minute_str = m.group(2)

        if not name:
            continue

        minute_val = None
        if minute_str and minute_str != '?':
            try:
                minute_val = int(minute_str)
            except ValueError:
                pass

        scorers.append({
            'name': name,
            'minute': minute_val,
        })

    return scorers


def main():
    print("Loading CSV...")
    with open(CSV_PATH, encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Loaded {len(rows)} games\n")

    # Parse scorers for each game
    stats = {
        'games_with_scorers': 0,
        'games_without_scorers': 0,
        'total_scorers': 0,
        'scorers_with_unknown_minute': 0,
    }

    for row in rows:
        for field, out_field in [('maccabi_scorers', 'maccabi_scorers_parsed'),
                                  ('opponent_scorers', 'opponent_scorers_parsed')]:
            text = row.get(field, '').strip()
            parsed = parse_scorers(text)
            if field == 'maccabi_scorers':
                if parsed:
                    stats['games_with_scorers'] += 1
                    stats['total_scorers'] += len(parsed)
                    stats['scorers_with_unknown_minute'] += sum(1 for s in parsed if s['minute'] is None)
                else:
                    stats['games_without_scorers'] += 1
            row[out_field] = json.dumps(parsed, ensure_ascii=False)

    # Write output CSV
    output_fields = list(rows[0].keys())
    with open(OUTPUT_PATH, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Statistics:")
    print(f"  Games with Maccabi scorers: {stats['games_with_scorers']}")
    print(f"  Games without scorers: {stats['games_without_scorers']}")
    print(f"  Total Maccabi scorer entries: {stats['total_scorers']}")
    print(f"  Scorers with unknown minute: {stats['scorers_with_unknown_minute']}")
    print(f"\nWrote {OUTPUT_PATH}")

    # Show samples
    print(f"\nSample parsed scorers:")
    for i, row in enumerate(rows[:10]):
        if row['maccabi_scorers_parsed'] != '[]':
            print(f"  {row['date']}: Maccabi={row['maccabi_scorers_parsed'][:80]}")
            if row['opponent_scorers_parsed'] != '[]':
                print(f"          Opponent={row['opponent_scorers_parsed'][:80]}")


if __name__ == '__main__':
    main()
