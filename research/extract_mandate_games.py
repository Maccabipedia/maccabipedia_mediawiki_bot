"""
Extract Maccabi Tel Aviv games from the British Mandate era football book (1930-1948).

Source PDF: ליגת ההתאחדות לכדורגל בתקופת המנדט הבריטי-1930-1948.pdf
Output: data/mandate_games_maccabi_ta.csv

Usage:
    python research/extract_mandate_games.py               # dry-run: print to console
    python research/extract_mandate_games.py --write       # write CSV file

Dependencies:
    pip install pdfplumber
"""

import re
import csv
import sys
from pathlib import Path

import pdfplumber

PDF_PATH = "/mnt/c/maccabipedia/automations/ליגת ההתאחדות לכדורגל בתקופת המנדט הבריטי-1930-1948.pdf"
OUTPUT_CSV = Path(__file__).parent.parent / "data" / "mandate_games_maccabi_ta.csv"

# ---------------------------------------------------------------------------
# RTL text fix
# ---------------------------------------------------------------------------

def fix_hebrew_word(word):
    """Reverse character order of Hebrew words to fix RTL PDF extraction."""
    if any('\u0590' <= c <= '\u05FF' for c in word):
        return word[::-1]
    return word


def fix_rtl_line(line):
    """Fix a full RTL line: reverse word order + reverse each Hebrew word's chars."""
    words = line.split()
    return ' '.join(fix_hebrew_word(w) for w in reversed(words))


def fix_encoding(text):
    """Fix known PDF font encoding artifacts in the fixed text."""
    # ð maps to נ (Nun) consistently throughout the book
    return text.replace('ð', 'נ')


def normalize_team_name(name):
    """
    Fix rendering artifacts in team names:
      - 'ת" א'    → 'ת"א'        (Step 1: abbreviation space before city initial)
      - 'ירושלי ם' → 'ירושלים'  (Step 2: final letter stored as separate glyph)
      - 'חיפ ה'   → 'חיפה'

    Order matters: fix abbreviations first, then final letters.
    The negative lookahead (?!["']) in Step 2 prevents collapsing 'מכבי ת"א' → 'מכבית"א'
    and 'רחובות ב'' → 'רחובותב''.
    """
    # Step 1: Fix abbreviation space: 'ת" א' → 'ת"א', 'פ" ת' → 'פ"ת'
    name = re.sub(r'([\u05D0-\u05EA]")\s+([\u05D0-\u05EA])', r'\1\2', name)
    # Step 2: Collapse final letter stored as separate glyph: 'ירושלי ם' → 'ירושלים'
    # Negative lookahead (?!["']) prevents merging before abbreviation/reserve suffixes
    name = re.sub(r'([\u05D0-\u05EA]{2,})\s+([\u05D0-\u05EA])\b(?!["\'"])', r'\1\2', name)
    return re.sub(r'\s+', ' ', name).strip()


# ---------------------------------------------------------------------------
# Parsing patterns
# ---------------------------------------------------------------------------

# Date at the start of a game record line: D.M[.YY]
DATE_RE = re.compile(r'^(\d{1,2})\.(\d{1,2})(?:\.(\d{2,4}))?(?=\s)')

# Season header after RTL fix: "עונת 1930-31" or "עונת 1937"
SEASON_RE = re.compile(r'עונת\s+(\d{4}[-/]\d{2,4}|\d{4})\b')

# Division header: "ליגה ב'" signals 2nd division section
DIVISION_B_RE = re.compile(r'ליגה\s+ב\'')

# Cup section
CUP_RE = re.compile(r'גביע')

# Games section header
GAMES_SECTION_MARKER = 'משחקי הליגה'

# Score: two-token format "N M–"  →  home=N, away=M
TWO_TOKEN_SCORE_RE = re.compile(r'\s(\d+)\s+(\d+)–(?:\s|$)')

# Score: single-token format "N–M"  →  away=N, home=M  (char-reversed in PDF)
SINGLE_TOKEN_SCORE_RE = re.compile(r'\s(\d+)–(\d+)(?:\s|$)')

# Team name start prefixes (after RTL fix)
TEAM_PREFIX_RE = re.compile(
    r'(?:מכבי|הפועל|המעופפים|המשטרה|הגדוד|גדוד|הכח|החלוץ|'
    r'בית"ר|נס"ק|דגל|ריח|ה"א|בית"ל|הנוטר|הדסה|הומנטמן|אגד|בני)'
)

# Maccabi TA identifier: matches "מכבי ת"א" or "מכבי ת" א" (PDF rendering artifact)
# Negative lookahead excludes reserve-team entries like "מכבי ת"א ב'" or "מכבי ת"א ב '"
MACCABI_TA_RE = re.compile(r'מכבי\s+ת"?\s*א(?!\s*["\s]*ב\s*\')')


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def strip_footnote(score):
    """
    Strip leading footnote digits from a score if implausibly large (>15).
    Football scores rarely exceed 15; anything larger is a footnote prefix glued
    to the real score digit. Strategy: strip one leading digit at a time until
    the score is ≤15, then take last digit if still too large.
    E.g. 273 → 73 → 3; 3010 → 10 → 0; 311 → 11 → 1.
    """
    while score > 15:
        stripped = score % (10 ** (len(str(score)) - 1))
        if stripped == score:  # shouldn't happen, guard against infinite loop
            break
        score = stripped
    # Final fallback: if still > 15, take last digit
    if score > 15:
        score = score % 10
    return score


def find_score(line):
    """
    Find the score in a game record line.
    Returns (home_score, away_score, score_start, score_end) or None.

    Two-token "N M–": home=N, away=M
    Single-token "N–M": away=N, home=M
    """
    m = TWO_TOKEN_SCORE_RE.search(line)
    if m:
        h, a = int(m.group(1)), int(m.group(2))
        if h > 25 or a > 25:
            print(f"  [score sanity] raw={h}–{a} → stripping footnote prefix")
            h, a = strip_footnote(h), strip_footnote(a)
        return h, a, m.start(), m.end()

    m = SINGLE_TOKEN_SCORE_RE.search(line)
    if m:
        # Single-token: characters were reversed in PDF → away first
        h, a = int(m.group(2)), int(m.group(1))
        if h > 25 or a > 25:
            print(f"  [score sanity] raw={h}–{a} → stripping footnote prefix")
            h, a = strip_footnote(h), strip_footnote(a)
        return h, a, m.start(), m.end()

    return None


def fix_scorers(text):
    """Fix reversed parentheses around minute numbers: '77) (' → '(77)'."""
    return re.sub(r'(\d+)\)\s*\(', r'(\1)', text)


def split_teams(teams_str):
    """
    Split 'HOME AWAY' string into two team names using known team prefixes.
    Returns (home_team, away_team). Falls back to ('?', teams_str) if unclear.
    """
    matches = list(TEAM_PREFIX_RE.finditer(teams_str))
    if len(matches) >= 2:
        split_pos = matches[1].start()
        home = normalize_team_name(teams_str[:split_pos])
        away = normalize_team_name(teams_str[split_pos:])
        return home, away
    # Only one team found: return it as home, away unknown
    if len(matches) == 1:
        return normalize_team_name(teams_str), '?'
    return '?', teams_str


def infer_year(day, month, season_str, last_date=None):
    """
    Infer the 4-digit year from season string and month.
    Season formats: '1930-31', '1931/32', '1937', '1941-43', '1947-48'

    If last_date is provided, validates that the inferred date doesn't jump more
    than 90 days backwards. If it does, tries the other year of the season.
    This handles seasons that extend into the Jul-Sep of the second year
    (e.g. 1946/47 games in September 1947).
    """
    import datetime

    year_match = re.match(r'(\d{4})[-/](\d{2,4})', season_str)
    if year_match:
        first_year = int(year_match.group(1))
        last_part = year_match.group(2)
        last_year = first_year // 100 * 100 + int(last_part) if len(last_part) == 2 else int(last_part)
        year = first_year if month >= 7 else last_year

        if last_date is not None:
            try:
                inferred = datetime.date(year, month, min(day, 28))
                gap = (inferred - last_date).days  # positive = forward, negative = backward
                # Trigger fix if: jumped backwards >90 days OR forwards >200 days
                if gap < -90 or gap > 200:
                    alt_year = last_year if year == first_year else first_year
                    # Only apply fix if alt date is within the season's plausible range:
                    # seasons should not extend past October of their last year
                    if not (alt_year > last_year or (alt_year == last_year and month > 10)):
                        alt_inferred = datetime.date(alt_year, month, min(day, 28))
                        alt_gap = (alt_inferred - last_date).days
                        # Only use alt if it's closer AND doesn't go significantly backwards
                        if (abs(alt_gap) < abs(gap)) and alt_gap > -30:
                            print(f"  [year fix] {day:02d}-{month:02d}: inferred {year} but last game was {last_date} → using {alt_year}")
                            year = alt_year
            except ValueError:
                pass
        return year
    else:
        return int(season_str)


def season_to_wiki_format(season_str):
    """Convert '1930-31' → '1930/31', '1937' → '1937'."""
    return season_str.replace('-', '/')


# ---------------------------------------------------------------------------
# Main extraction
# ---------------------------------------------------------------------------

def extract_games():
    games = []
    skipped_lines = []

    current_season_raw = ''
    current_date_parts = None   # (day, month, year_or_None)
    last_game_date = None       # datetime.date of last successfully parsed game
    last_explicit_year = None   # last year seen from an explicit date in the PDF (e.g. "13.6.42" → 1942)
    in_games_section = False
    pending_continuation = None  # last appended game, waiting for its continuation scorer line
    competition = 'ליגת ההתאחדות'  # default; updated when ליגה ב' detected

    with pdfplumber.open(PDF_PATH) as pdf:
        print(f"PDF opened: {len(pdf.pages)} pages")

        for page_num, page in enumerate(pdf.pages, 1):
            raw_text = page.extract_text()
            if not raw_text:
                continue

            for raw_line in raw_text.split('\n'):
                # Step 1: fix RTL + encoding
                line = fix_encoding(fix_rtl_line(raw_line))
                if not line.strip():
                    continue

                # Step 2: track season header
                season_m = SEASON_RE.search(line)
                if season_m:
                    current_season_raw = season_m.group(1)
                    in_games_section = False
                    competition = 'ליגת ההתאחדות'
                    last_game_date = None  # reset year-inference context for new season
                    last_explicit_year = None
                    pending_continuation = None
                    continue

                # Step 3: track division / section headers
                # Only treat as a section header if the line is short (standalone heading)
                stripped = line.strip()
                if DIVISION_B_RE.search(stripped) and len(stripped) < 20:
                    competition = "ליגה ב'"
                    in_games_section = False
                    last_game_date = None  # reset so year inference starts fresh for this section
                    last_explicit_year = None
                    pending_continuation = None
                    continue

                if GAMES_SECTION_MARKER in line:
                    in_games_section = True
                    last_game_date = None  # reset so year inference starts fresh for this section
                    last_explicit_year = None
                    pending_continuation = None
                    continue

                if not in_games_section or not current_season_raw:
                    continue

                # Step 4: try to parse as game record line
                date_m = DATE_RE.match(line)
                rest_start = 0

                if date_m:
                    pending_continuation = None  # new date line = end of any pending continuation
                    day = int(date_m.group(1))
                    month = int(date_m.group(2))
                    year_raw = date_m.group(3)
                    if year_raw:
                        year_2d = int(year_raw) if len(year_raw) == 4 else int(year_raw)
                        year = 1900 + year_2d if year_2d < 100 else year_2d
                        # Sanity-check explicit 2-digit years against last_game_date
                        # (catches book typos like "9.6.44" that should be "9.6.45")
                        # Skip for multi-year seasons (e.g. 1941/43) — the book may list
                        # sub-sections non-chronologically, so last_game_date is unreliable.
                        season_span = 1
                        s_m = re.match(r'(\d{4})[-/](\d{2,4})', current_season_raw or '')
                        if s_m:
                            fy = int(s_m.group(1))
                            lp = s_m.group(2)
                            ly = fy // 100 * 100 + int(lp) if len(lp) == 2 else int(lp)
                            season_span = ly - fy
                        if last_game_date is not None and year_2d < 100 and season_span <= 1:
                            import datetime
                            try:
                                gap = (datetime.date(year, month, min(day, 28)) - last_game_date).days
                                if gap < -90 or gap > 200:
                                    year_fixed = infer_year(day, month, current_season_raw, last_date=last_game_date)
                                    if year_fixed != year:
                                        print(f"  [year fix explicit] {day:02d}-{month:02d}-{year_2d}: explicit year {year} → using {year_fixed}")
                                        year = year_fixed
                            except ValueError:
                                pass
                        last_explicit_year = year  # carry forward for subsequent no-year lines
                    else:
                        # If a recent explicit year was seen in this section, try using it first.
                        # This handles "DD.MM" lines that immediately follow an explicit-year line
                        # (e.g. "20.6" after "13.6.42" → year 1942).
                        if last_explicit_year is not None:
                            import datetime
                            try:
                                candidate = datetime.date(last_explicit_year, month, min(day, 28))
                                gap = (candidate - last_game_date).days if last_game_date else 0
                                # Use explicit-year context if the date is plausible (not too far back/forward)
                                if -90 <= gap <= 200:
                                    year = last_explicit_year
                                else:
                                    year = infer_year(day, month, current_season_raw, last_date=last_game_date)
                            except ValueError:
                                year = infer_year(day, month, current_season_raw, last_date=last_game_date)
                        else:
                            year = infer_year(day, month, current_season_raw, last_date=last_game_date)
                    current_date_parts = (day, month, year)
                    rest_start = date_m.end()

                # Need a known date to parse the game
                if current_date_parts is None:
                    continue

                # Step 5: find score in line
                rest = line[rest_start:]
                score_result = find_score(rest)
                if not score_result:
                    # Check if this is a continuation scorer line (second team's scorers)
                    # Pattern: no date at start, no score, but follows a game line.
                    # Stadium/referee/header lines are excluded by keyword checks.
                    if (pending_continuation is not None
                            and date_m is None  # must not be a new date line
                            and pending_continuation.get('continuation_scorers') is None  # only first continuation
                            and not re.search(r'שופט|מגרש|אצטדיון|קהל|צופים', line)
                            and re.search(r'[\u05D0-\u05EA]{2,}', line)):  # has Hebrew text
                        raw = fix_scorers(fix_encoding(line.strip()))
                        pending_continuation['continuation_scorers'] = raw
                    else:
                        pending_continuation = None  # non-scorer line breaks continuation
                    continue

                home_score, away_score, score_start, score_end = score_result
                teams_str = rest[:score_start].strip()
                scorers_raw = fix_scorers(fix_encoding(rest[score_end:].strip()))

                # Step 6: normalize teams_str to fix PDF rendering artifacts before matching
                teams_str_norm = normalize_team_name(teams_str)

                # Filter for Maccabi TA games
                if not MACCABI_TA_RE.search(teams_str_norm):
                    continue

                # Step 7: split teams
                home_team, away_team = split_teams(teams_str_norm)

                # Determine if Maccabi is home or away
                maccabi_is_home = bool(MACCABI_TA_RE.search(home_team))
                opponent = away_team if maccabi_is_home else home_team
                home_away = 'בית' if maccabi_is_home else 'חוץ'
                maccabi_score = home_score if maccabi_is_home else away_score
                opponent_score = away_score if maccabi_is_home else home_score

                # Step 8: format date
                day, month, year = current_date_parts
                date_str = f"{day:02d}-{month:02d}-{year}"

                import datetime
                try:
                    last_game_date = datetime.date(year, month, min(day, 28))
                except ValueError:
                    pass

                game_record = {
                    'date': date_str,
                    'season': season_to_wiki_format(current_season_raw),
                    'competition': competition,
                    'round': '',
                    'opponent': normalize_team_name(opponent),
                    'home_away': home_away,
                    'stadium': '',
                    'maccabi_score': maccabi_score,
                    'opponent_score': opponent_score,
                    'maccabi_coach': '',
                    'opponent_coach': '',
                    'referee': '',
                    'crowd': '',
                    # scorers_raw = text after score on the game line = HOME team scorers
                    'scorers': scorers_raw,
                    'continuation_scorers': None,   # filled by next line if present
                    'maccabi_is_home': maccabi_is_home,
                    'raw_home_team': normalize_team_name(home_team),
                    'raw_away_team': normalize_team_name(away_team),
                    'page': page_num,
                }
                games.append(game_record)
                pending_continuation = game_record

    # Assign maccabi_scorers / opponent_scorers based on home/away
    # The game line always contains HOME team scorers; continuation = AWAY team scorers
    for g in games:
        home_scorers = g.pop('scorers', '')
        cont_scorers = g.pop('continuation_scorers') or ''
        maccabi_is_home = g.pop('maccabi_is_home', True)
        if maccabi_is_home:
            g['maccabi_scorers'] = home_scorers
            g['opponent_scorers'] = cont_scorers
        else:
            g['maccabi_scorers'] = cont_scorers
            g['opponent_scorers'] = home_scorers

    # Deduplicate by (date, home_away, opponent) — keep first occurrence
    seen = set()
    unique_games = []
    for g in games:
        key = (g['date'], g['home_away'], g['opponent'])
        if key not in seen:
            seen.add(key)
            unique_games.append(g)
        else:
            print(f"  [dedup] removed duplicate: {g['date']} {g['home_away']} vs {g['opponent']} (p.{g['page']})")
    return unique_games


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

CSV_FIELDS = [
    'date', 'season', 'competition', 'round',
    'opponent', 'home_away', 'stadium',
    'maccabi_score', 'opponent_score',
    'maccabi_coach', 'opponent_coach',
    'referee', 'crowd',
    'maccabi_scorers', 'opponent_scorers',
    'raw_home_team', 'raw_away_team', 'page',
]


def print_games(games):
    for g in games:
        flag = '⚠' if g['opponent'] == '?' else ''
        print(
            f"  {g['date']}  {g['home_away']}  מכבי ת\"א {g['maccabi_score']}–{g['opponent_score']} {g['opponent']}"
            f"  [{g['season']} / {g['competition']}]"
            f"  p.{g['page']} {flag}"
        )
        if g['maccabi_scorers']:
            print(f"    מבקיעי מכבי: {g['maccabi_scorers'][:80]}")
        if g['opponent_scorers']:
            print(f"    מבקיעי יריב: {g['opponent_scorers'][:80]}")


def write_csv(games, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(games)
    print(f"\nWrote {len(games)} rows → {path}")


if __name__ == '__main__':
    write = '--write' in sys.argv

    print("Extracting Maccabi TA games from mandate-era PDF...\n")
    games = extract_games()

    print(f"\nFound {len(games)} Maccabi TA games:\n")
    print_games(games)

    # Summary by season
    from collections import Counter
    season_counts = Counter(g['season'] for g in games)
    print(f"\nGames per season:")
    for season, count in sorted(season_counts.items()):
        print(f"  {season}: {count}")

    # Flag games with unknown teams
    unknown = [g for g in games if g['opponent'] == '?']
    if unknown:
        print(f"\n⚠ {len(unknown)} games with unresolved opponent names — manual review needed")

    if write:
        write_csv(games, OUTPUT_CSV)
    else:
        print(f"\nDry run complete. Run with --write to save {OUTPUT_CSV}")
