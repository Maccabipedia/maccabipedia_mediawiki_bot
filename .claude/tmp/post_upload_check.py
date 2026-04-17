"""Verify the just-uploaded Virtus Bologna page round-trips cleanly."""
import mwparserfromhell, pywikibot as pw
from pydantic import TypeAdapter
from pathlib import Path
from maccabipediabot.basketball.basketball_game import BasketballGame
from maccabipediabot.basketball.gamesbot_basketball import (
    _site, generate_page_name_from_game, render_basketball_game_to_wiki,
)

games = TypeAdapter(list[BasketballGame]).validate_json(Path("/tmp/eu2.json").read_text("utf-8"))
target = next(g for g in games if "וירטוס בולוניה" in g.away_team_name or "וירטוס בולוניה" in g.home_team_name)
title = generate_page_name_from_game(target)
page = pw.Page(_site(), title)
print(f"page exists: {page.exists()}")
print(f"page url   : https://www.maccabipedia.co.il/index.php?title={title.replace(' ', '_')}")
print(f"saved size : {len(page.text)} bytes")

ours = render_basketball_game_to_wiki(target)
def params(text):
    parsed = mwparserfromhell.parse(text)
    matches = parsed.filter_templates(matches=lambda t: t.name.matches("משחק כדורסל"))
    return {str(p.name).strip(): str(p.value).strip() for p in matches[0].params} if matches else {}
o, w = params(ours), params(page.text)
diffs = [k for k in set(o) & set(w) if o[k] != w[k]]
print(f"\nfields same={len(set(o)&set(w))-len(diffs)} differs={len(diffs)} ours-only={len(set(o)-set(w))} wiki-only={len(set(w)-set(o))}")
for k in diffs:
    print(f"  DIFFERS {k}\n    ours: {o[k][:140]}\n    wiki: {w[k][:140]}")
