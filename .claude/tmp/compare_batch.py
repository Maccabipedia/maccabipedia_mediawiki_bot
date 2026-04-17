"""Compare our pipeline's render vs live MaccabiPedia, for N games per source.

Outputs a compact per-game summary plus an aggregate of which diff types appear
most, so we can tell the difference between systemic code bugs and one-off
wiki/data-side quirks.
"""
import sys
from collections import Counter
from pathlib import Path

import mwparserfromhell
import pywikibot as pw
from pydantic import TypeAdapter

from maccabipediabot.basketball.basketball_game import BasketballGame
from maccabipediabot.basketball.gamesbot_basketball import (
    _site,
    generate_page_name_from_game,
    render_basketball_game_to_wiki,
)

TEMPLATE = "משחק כדורסל"


def params(text: str) -> dict[str, str]:
    parsed = mwparserfromhell.parse(text)
    matches = parsed.filter_templates(matches=lambda t: t.name.matches(TEMPLATE))
    return {str(p.name).strip(): str(p.value).strip() for p in matches[0].params} if matches else {}


def compare(json_path: Path, label: str) -> tuple[Counter, int, int]:
    """Return (diff_field_counter, n_games_compared, n_new_pages)."""
    games = TypeAdapter(list[BasketballGame]).validate_json(json_path.read_text(encoding="utf-8"))
    site = _site()
    diff_fields: Counter = Counter()
    wiki_only_fields: Counter = Counter()
    n_compared = 0
    n_new = 0
    print(f"\n{'='*72}\n{label} — {len(games)} games\n{'='*72}")
    for g in games:
        title = generate_page_name_from_game(g)
        page = pw.Page(site, title)
        if not page.exists():
            n_new += 1
            print(f"  NEW    {title}")
            continue
        ours = params(render_basketball_game_to_wiki(g))
        theirs = params(page.text)
        if not theirs:
            print(f"  NOTMPL {title}")
            continue
        n_compared += 1
        differs = [k for k in set(ours) & set(theirs) if ours[k] != theirs[k]]
        ours_only = [k for k in set(ours) - set(theirs)]
        wiki_only = [k for k in set(theirs) - set(ours)]
        for f in differs:
            diff_fields[f] += 1
        for f in wiki_only:
            wiki_only_fields[f] += 1
        print(f"  match  {title}  same={len(set(ours) & set(theirs)) - len(differs)} "
              f"differs={len(differs)} wiki-only={len(wiki_only)} ours-only={len(ours_only)}")
    return diff_fields, wiki_only_fields, n_compared, n_new


def main() -> None:
    all_diffs: Counter = Counter()
    all_wiki_only: Counter = Counter()
    total_compared = 0
    total_new = 0
    for path, label in [
        (Path("/tmp/basket10.json"), "basket.co.il"),
        (Path("/tmp/euroleague10.json"), "euroleague"),
    ]:
        d, w, c, n = compare(path, label)
        all_diffs.update(d)
        all_wiki_only.update(w)
        total_compared += c
        total_new += n

    print(f"\n\n{'='*72}\nAGGREGATE — {total_compared} games compared, {total_new} new\n{'='*72}")
    print("\nDIFFERS (how many games the field was present in both but values differed):")
    for field, count in all_diffs.most_common():
        print(f"  {count:3d}  {field}")
    print("\nWIKI-ONLY (field present on wiki but not emitted by gamesbot):")
    for field, count in all_wiki_only.most_common():
        print(f"  {count:3d}  {field}")


if __name__ == "__main__":
    main()
