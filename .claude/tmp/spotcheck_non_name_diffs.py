"""Print ours vs wiki for the small-count DIFFERS fields — non-name-list diffs
that could be actual code bugs (crowd, arena, refs, coach, URL)."""
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
FIELDS_OF_INTEREST = {"כמות קהל", "עוזרי שופט", "אולם", "מאמן יריבה", "כתבה1"}


def params(text: str) -> dict[str, str]:
    parsed = mwparserfromhell.parse(text)
    matches = parsed.filter_templates(matches=lambda t: t.name.matches(TEMPLATE))
    return {str(p.name).strip(): str(p.value).strip() for p in matches[0].params} if matches else {}


def scan(json_path: Path, label: str) -> None:
    games = TypeAdapter(list[BasketballGame]).validate_json(json_path.read_text(encoding="utf-8"))
    site = _site()
    print(f"\n{'='*72}\n{label}\n{'='*72}")
    for g in games:
        title = generate_page_name_from_game(g)
        page = pw.Page(site, title)
        if not page.exists():
            continue
        ours = params(render_basketball_game_to_wiki(g))
        theirs = params(page.text)
        field_diffs = []
        for f in FIELDS_OF_INTEREST:
            o, t = ours.get(f, ""), theirs.get(f, "")
            if o != t:
                field_diffs.append((f, o, t))
        if field_diffs:
            print(f"\n{title}")
            for f, o, t in field_diffs:
                # compact single-line each
                print(f"  {f}:")
                print(f"    ours : {o[:150]}")
                print(f"    wiki : {t[:150]}")


scan(Path("/tmp/basket10.json"), "basket.co.il")
scan(Path("/tmp/euroleague10.json"), "euroleague")
