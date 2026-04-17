"""Round-trip test: real Euroleague OT game vs wiki. Specifically check OT fields."""
from datetime import datetime

import mwparserfromhell
import pywikibot as pw

from maccabipediabot.basketball.crawl_euroleague import (
    EuroleagueGameMeta,
    extract_next_data,
    fetch_html,
    parse_game_page,
)
from maccabipediabot.basketball.gamesbot_basketball import (
    _site,
    generate_page_name_from_game,
    render_basketball_game_to_wiki,
)

URL = "https://www.euroleaguebasketball.net/en/euroleague/game-center/2025-26/maccabi-rapyd-tel-aviv-dubai-basketball/E2025/333/"

# Build a meta manually (discovery fields we know about the game)
meta = EuroleagueGameMeta(
    scrape_url=URL,
    game_date=datetime(2026, 3, 26, 20, 0),  # will be overridden by parse if needed
    is_maccabi_home=True,
    opponent_name_eng="Dubai Basketball",
    home_team_score=0,  # parsed from data
    away_team_score=0,
    fixture_round=None,
)

# Fetch + parse as live
nd = extract_next_data(fetch_html(URL))
game = parse_game_page(nd, meta)
# Override scores from actual data since meta had placeholders
raw = nd["props"]["pageProps"]["mappedData"]["rawGameInfo"]
game.home_team_score = raw["home"]["score"]
game.away_team_score = raw["away"]["score"]

print(f"parsed: {game.home_team_name} {game.home_team_score} - {game.away_team_score} {game.away_team_name}")
print(f"Quarters Maccabi: Q1={game.first_quarter_maccabi_points} Q2={game.second_quarter_maccabi_points} "
      f"Q3={game.third_quarter_maccabi_points} Q4={game.fourth_quarter_maccabi_points} "
      f"OT1={game.first_overtime_maccabi_points} OT2={game.second_overtime_maccabi_points}")
print(f"Quarters Opponent: Q1={game.first_quarter_opponent_points} Q2={game.second_quarter_opponent_points} "
      f"Q3={game.third_quarter_opponent_points} Q4={game.fourth_quarter_opponent_points} "
      f"OT1={game.first_overtime_opponent_points} OT2={game.second_overtime_opponent_points}")
print(f"has_overtime: {game.has_overtime}")

# Compare OT fields with wiki
TEMPLATE = "משחק כדורסל"
title = generate_page_name_from_game(game)
print(f"\ntitle: {title}")
page = pw.Page(_site(), title)
if not page.exists():
    print("  page doesn't exist on wiki")
else:
    parsed = mwparserfromhell.parse(page.text)
    matches = parsed.filter_templates(matches=lambda t: t.name.matches(TEMPLATE))
    wiki_params = {str(p.name).strip(): str(p.value).strip() for p in matches[0].params} if matches else {}

    ot_keys = [
        "נקודות מכבי הארכה1", "נקודות מכבי הארכה2",
        "נקודות יריבה הארכה1", "נקודות יריבה הארכה2",
    ]
    print("\nOT field wiki values:")
    for k in ot_keys:
        print(f"  wiki {k!r} = {wiki_params.get(k, '(not present)')!r}")
    print("\nParsed-Python values (should match wiki):")
    ours_render = render_basketball_game_to_wiki(game)
    ours_parsed = mwparserfromhell.parse(ours_render)
    ours_matches = ours_parsed.filter_templates(matches=lambda t: t.name.matches(TEMPLATE))
    ours_params = {str(p.name).strip(): str(p.value).strip() for p in ours_matches[0].params}
    for k in ot_keys:
        wiki_v = wiki_params.get(k, None)
        ours_v = ours_params.get(k, None)
        mark = "OK" if wiki_v == ours_v else "MISMATCH"
        print(f"  [{mark}] {k!r} : ours={ours_v!r}  wiki={wiki_v!r}")
