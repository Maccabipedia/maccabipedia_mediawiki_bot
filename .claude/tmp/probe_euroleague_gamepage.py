"""Probe a euroleague per-game page to confirm box-score is in __NEXT_DATA__."""
import json
import requests
from bs4 import BeautifulSoup

URL = "https://www.euroleaguebasketball.net/en/euroleague/game-center/2025-26/anadolu-efes-istanbul-maccabi-rapyd-tel-aviv/E2025/1/"
HEADERS = {"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US,en;q=0.9"}

resp = requests.get(URL, headers=HEADERS, timeout=30)
print(f"status={resp.status_code} len={len(resp.text)}")

soup = BeautifulSoup(resp.text, "html.parser")
nd = soup.select_one("script#__NEXT_DATA__")
if not nd:
    print("NO __NEXT_DATA__")
    raise SystemExit
data = json.loads(nd.text)
pp = data["props"]["pageProps"]
print("pageProps keys:", list(pp.keys()))

def find_player_stats(obj, depth=0, path=""):
    if depth > 8: return
    if isinstance(obj, dict):
        for k, v in obj.items():
            kl = k.lower()
            if kl in {"boxscore", "playerstats", "players", "stats", "lineups", "homestats", "awaystats"}:
                if isinstance(v, list):
                    print(f"  {path}.{k}: list[{len(v)}]")
                    if v and isinstance(v[0], dict):
                        print(f"    sample keys: {list(v[0].keys())[:30]}")
                elif isinstance(v, dict):
                    print(f"  {path}.{k}: dict keys={list(v.keys())[:20]}")
            find_player_stats(v, depth+1, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, item in enumerate(obj[:3]):
            find_player_stats(item, depth+1, f"{path}[{i}]")

find_player_stats(pp)

# Try a likely API: euroleague feeds
import re
api_urls = sorted(set(re.findall(r'https?://[a-z0-9.-]+/[^"\']*?game[^"\']*', resp.text, re.IGNORECASE)))[:10]
print(f"\napi/game URLs in HTML:")
for u in api_urls[:8]:
    print(f"  {u}")
