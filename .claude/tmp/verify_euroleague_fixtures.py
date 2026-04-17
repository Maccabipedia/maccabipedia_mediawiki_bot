"""Verify the captured Euroleague fixtures contain the expected __NEXT_DATA__ shape."""
import json
from pathlib import Path
from bs4 import BeautifulSoup

team_path = Path("packages/maccabipediabot/tests/basketball/fixtures/euroleague_team_results.html")
game_path = Path("packages/maccabipediabot/tests/basketball/fixtures/euroleague_game_E2025_R1.html")

team_data = json.loads(BeautifulSoup(team_path.read_text("utf-8"), "html.parser").select_one("script#__NEXT_DATA__").text)
game_data = json.loads(BeautifulSoup(game_path.read_text("utf-8"), "html.parser").select_one("script#__NEXT_DATA__").text)

assert "results" in team_data["props"]["pageProps"], "team-results missing results"
results = team_data["props"]["pageProps"]["results"]["results"]
assert isinstance(results, list) and len(results) > 0, "no games in team-results"

mapped = game_data["props"]["pageProps"]["mappedData"]
assert "rawGameInfo" in mapped, "game page missing rawGameInfo"
assert "boxScores" in mapped, "game page missing boxScores"
assert isinstance(mapped["rawGameInfo"]["home"]["players"], list), "no home players"

print(f"team page: {len(results)} games")
print(f"game page: {len(mapped['rawGameInfo']['home']['players'])} home players, "
      f"{len(mapped['rawGameInfo']['away']['players'])} away players")
