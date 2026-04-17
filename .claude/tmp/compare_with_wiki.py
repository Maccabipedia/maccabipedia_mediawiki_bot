"""Compare what our pipeline would render vs. what's currently on MaccabiPedia.

For each game in /tmp/basket2.json and /tmp/euroleague2.json:
  1. Generate the page name our pipeline produces
  2. Render the wiki template text we'd upload
  3. Fetch the existing wiki page text (if any)
  4. Parse both as {{משחק כדורסל}} templates
  5. Diff parameter-by-parameter
"""
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

TEMPLATE_NAME = "משחק כדורסל"


def _params(text: str) -> dict[str, str]:
    parsed = mwparserfromhell.parse(text)
    matches = parsed.filter_templates(matches=lambda t: t.name.matches(TEMPLATE_NAME))
    if not matches:
        return {}
    tmpl = matches[0]
    return {str(p.name).strip(): str(p.value).strip() for p in tmpl.params}


def compare(json_path: Path, label: str) -> None:
    print(f"\n{'=' * 70}\n{label}\n{'=' * 70}")
    games = TypeAdapter(list[BasketballGame]).validate_json(
        json_path.read_text(encoding="utf-8")
    )
    site = _site()
    for game in games:
        title = generate_page_name_from_game(game)
        print(f"\n--- {title} ---")
        ours = _params(render_basketball_game_to_wiki(game))

        page = pw.Page(site, title)
        if not page.exists():
            print(f"(page does not exist on wiki — would be created NEW with {len(ours)} params)")
            continue

        theirs = _params(page.text)
        if not theirs:
            print(f"(wiki page has no {TEMPLATE_NAME!r} template — unusual)")
            continue

        all_keys = sorted(set(ours) | set(theirs))
        diffs = []
        same = 0
        ours_only = 0
        theirs_only = 0
        for k in all_keys:
            o, t = ours.get(k), theirs.get(k)
            if o == t:
                same += 1
            elif o is None:
                theirs_only += 1
                diffs.append(f"  WIKI ONLY  {k!r}: {t!r}")
            elif t is None:
                ours_only += 1
                diffs.append(f"  OURS ONLY  {k!r}: {o!r}")
            else:
                diffs.append(f"  DIFFERS    {k!r}\n    ours : {o[:160]!r}\n    wiki : {t[:160]!r}")

        print(f"  same: {same}  ours-only: {ours_only}  wiki-only: {theirs_only}  differs: {len([d for d in diffs if d.startswith('  DIFFERS')])}")
        for d in diffs[:25]:
            print(d)
        if len(diffs) > 25:
            print(f"  ... ({len(diffs) - 25} more)")


compare(Path("/tmp/basket2.json"), "basket.co.il — last 2 games")
compare(Path("/tmp/euroleague2.json"), "euroleague — last 2 games")
