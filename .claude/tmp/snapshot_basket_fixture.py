"""Print the parsed BasketballGame from the basket.co.il fixture so we can
hand-paste the expected object into the test."""
from datetime import datetime
from pathlib import Path

from maccabipediabot.basketball.crawl_basket_co_il import GameDiscoveryMeta, parse_game_page

meta = GameDiscoveryMeta(
    game_id=26383,
    scrape_url="https://basket.co.il/game-zone.asp?GameId=26383",
    game_date=datetime(2025, 5, 30, 20, 30),
    is_maccabi_home=False,
    opponent_name="הפועל חולון",
    home_team_score=73,
    away_team_score=85,
    competition="ליגת העל",
)
html = Path("packages/maccabipediabot/tests/basketball/fixtures/basket_co_il_game_26383.html").read_bytes().decode("utf-8")
game = parse_game_page(html, meta)
print(game.model_dump_json(indent=2))
