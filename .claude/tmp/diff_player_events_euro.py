"""Precise byte-level diff in 'שחקנים מכבי' for Euroleague game 2."""
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
    return {str(p.name).strip(): str(p.value).strip() for p in matches[0].params} if matches else {}


games = TypeAdapter(list[BasketballGame]).validate_json(
    Path("/tmp/euroleague2.json").read_text(encoding="utf-8")
)
g = games[1]  # Maccabi vs Hapoel TLV
title = generate_page_name_from_game(g)
print(f"comparing: {title}\n")

ours = _params(render_basketball_game_to_wiki(g))
theirs = _params(pw.Page(_site(), title).text)

for field in ("שחקנים מכבי", "שחקנים יריבה"):
    print(f"\n=== {field} ===")
    o, t = ours[field], theirs[field]
    print(f"ours len={len(o)} wiki len={len(t)} identical={o == t}")
    if o != t:
        diff = list(difflib.unified_diff(t.splitlines(keepends=True),
                                          o.splitlines(keepends=True),
                                          fromfile="wiki", tofile="ours", n=0))
        # Show only the actual +/- lines
        for line in diff:
            if line.startswith(("+", "-")) and not line.startswith(("+++", "---")):
                print(line.rstrip()[:250])
