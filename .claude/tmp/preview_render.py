"""Smoke test: load each crawler's JSON output and render game[0] to wiki text."""
from pathlib import Path
from pydantic import TypeAdapter
from maccabipediabot.basketball.basketball_game import BasketballGame
from maccabipediabot.basketball.gamesbot_basketball import render_basketball_game_to_wiki

for path in (Path("/tmp/basket.json"), Path("/tmp/euroleague.json")):
    games = TypeAdapter(list[BasketballGame]).validate_json(path.read_text(encoding="utf-8"))
    if not games:
        print(f"{path}: no games (off-season?)")
        continue
    print(f"\n--- {path} game[0] ---")
    print(render_basketball_game_to_wiki(games[0]))
