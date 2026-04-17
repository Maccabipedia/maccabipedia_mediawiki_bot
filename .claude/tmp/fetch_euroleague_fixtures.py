"""Capture Euroleague HTML snapshots via Python requests (curl gets a Vercel challenge page)."""
from pathlib import Path

import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

PAIRS = [
    ("https://www.euroleaguebasketball.net/en/euroleague/teams/maccabi-rapyd-tel-aviv/games/tel/",
     "packages/maccabipediabot/tests/basketball/fixtures/euroleague_team_results.html"),
    ("https://www.euroleaguebasketball.net/en/euroleague/game-center/2025-26/anadolu-efes-istanbul-maccabi-rapyd-tel-aviv/E2025/1/",
     "packages/maccabipediabot/tests/basketball/fixtures/euroleague_game_E2025_R1.html"),
]

for url, path in PAIRS:
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    Path(path).write_bytes(resp.content)
    print(f"  {path}: {len(resp.content)} bytes (status={resp.status_code})")
