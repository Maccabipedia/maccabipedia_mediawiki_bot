"""Show the precise byte-level diff in 'שחקנים מכבי' for one game."""
import difflib
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


def _params(text: str) -> dict[str, str]:
    parsed = mwparserfromhell.parse(text)
    matches = parsed.filter_templates(matches=lambda t: t.name.matches("משחק כדורסל"))
    if not matches:
        return {}
    return {str(p.name).strip(): str(p.value).strip() for p in matches[0].params}


games = TypeAdapter(list[BasketballGame]).validate_json(
    Path("/tmp/basket2.json").read_text(encoding="utf-8")
)
g = games[1]  # 09-02-2026 (the one with cleanest diff)
title = generate_page_name_from_game(g)
print(f"comparing: {title}\n")

ours = _params(render_basketball_game_to_wiki(g))
theirs = _params(pw.Page(_site(), title).text)

field = "שחקנים מכבי"
o, t = ours[field], theirs[field]
print(f"ours len: {len(o)}")
print(f"wiki len: {len(t)}")
print(f"identical?: {o == t}")
print()
# print just the diff
diff = list(difflib.unified_diff(t.splitlines(keepends=True), o.splitlines(keepends=True),
                                  fromfile="wiki", tofile="ours", n=1))
print("".join(diff[:30]))
