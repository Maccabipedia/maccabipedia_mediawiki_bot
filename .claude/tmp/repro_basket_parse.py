"""Reproduce the basket.co.il parse failure to diagnose."""
import logging
logging.basicConfig(level=logging.DEBUG)

from maccabipediabot.basketball.crawl_basket_co_il import (
    discover_games_latest_season,
    fetch_game_html,
    parse_game_page,
)

metas = discover_games_latest_season(limit=1)
print(f"discovered: {len(metas)}")
for m in metas:
    print(f"  {m}")
    html = fetch_game_html(m.scrape_url)
    print(f"  html len: {len(html)}")
    game = parse_game_page(html, m)
    print(f"  parsed OK: {game.home_team_name} vs {game.away_team_name}")
