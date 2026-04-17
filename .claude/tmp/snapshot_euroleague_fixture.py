"""Snapshot the parsed BasketballGame from the Euroleague fixture."""
from datetime import datetime
from pathlib import Path

from maccabipediabot.basketball.crawl_euroleague import (
    EuroleagueGameMeta,
    extract_next_data,
    parse_game_page,
)

meta = EuroleagueGameMeta(
    scrape_url="https://www.euroleaguebasketball.net/en/euroleague/game-center/2025-26/anadolu-efes-istanbul-maccabi-rapyd-tel-aviv/E2025/1/",
    game_date=datetime(2025, 9, 30, 20, 30),
    is_maccabi_home=False,
    opponent_name_eng="Anadolu Efes Istanbul",
    home_team_score=85,
    away_team_score=78,
    fixture_round=1,
)
html = Path("packages/maccabipediabot/tests/basketball/fixtures/euroleague_game_E2025_R1.html").read_bytes().decode("utf-8")
game = parse_game_page(extract_next_data(html), meta)
print(game.model_dump_json(indent=2))
