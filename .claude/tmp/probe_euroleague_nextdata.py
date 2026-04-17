"""Inspect __NEXT_DATA__ on euroleague to see if games list + box scores are server-rendered."""
import json

import requests
from bs4 import BeautifulSoup

URL = "https://www.euroleaguebasketball.net/en/euroleague/teams/maccabi-rapyd-tel-aviv/games/tel/"
HEADERS = {"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US,en;q=0.9"}

resp = requests.get(URL, headers=HEADERS, timeout=30)
soup = BeautifulSoup(resp.text, "html.parser")
data = json.loads(soup.select_one("script#__NEXT_DATA__").text)

# Print top-level shape
print("top-level keys:", list(data.keys()))
print("props.pageProps keys:", list(data.get("props", {}).get("pageProps", {}).keys())[:50])

# Find games inside pageProps
def walk(obj, depth=0, path=""):
    if depth > 6: return
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_path = f"{path}.{k}"
            if k.lower() in {"games", "results", "schedule", "fixtures"}:
                if isinstance(v, list):
                    print(f"  found {new_path}: list of {len(v)}")
                    if v and isinstance(v[0], dict):
                        print(f"    sample keys: {list(v[0].keys())[:40]}")
                else:
                    print(f"  found {new_path}: {type(v).__name__}")
            walk(v, depth+1, new_path)
    elif isinstance(obj, list):
        for i, item in enumerate(obj[:3]):
            walk(item, depth+1, f"{path}[{i}]")

walk(data["props"]["pageProps"])

# Try a per-game URL too — find the URL pattern
import re
game_links = sorted(set(re.findall(r'/euroleague/[^"]*?game-center/[^"]*', resp.text))) or sorted(set(re.findall(r'/euroleague/[^"]*?games/[^"\s]*', resp.text)))[:5]
print(f"\nsample game/game-center URLs:")
for g in game_links[:5]:
    print(f"  {g}")
