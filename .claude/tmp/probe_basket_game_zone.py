"""Probe basket.co.il game-zone.asp without JS to see if static HTML has the data the TS Puppeteer scrape relies on."""
import sys

import requests
from bs4 import BeautifulSoup

GAME_ID = sys.argv[1] if len(sys.argv) > 1 else "30253"  # any recent maccabi game id
URL = f"https://basket.co.il/game-zone.asp?GameId={GAME_ID}"

resp = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
print(f"status={resp.status_code} len={len(resp.text)} ctype={resp.headers.get('Content-Type')}")
soup = BeautifulSoup(resp.text, "html.parser")

# TS scrape relies on: #wrap_inner_3 with h4/h5/h6 + tables.stats_tbl.categories + tables.stats_tbl
container = soup.select_one("#wrap_inner_3")
print(f"#wrap_inner_3 found: {bool(container)}")
if container:
    print(f"  h4: {container.select_one('h4').get_text(strip=True)[:80] if container.select_one('h4') else None}")
    print(f"  h5: {container.select_one('h5').get_text(strip=True)[:80] if container.select_one('h5') else None}")
    print(f"  h6: {container.select_one('h6').get_text(strip=True)[:80] if container.select_one('h6') else None}")

cats = soup.select("table.stats_tbl.categories")
print(f"tables.stats_tbl.categories: {len(cats)}")

all_stats = soup.select("table.stats_tbl")
print(f"tables.stats_tbl total: {len(all_stats)}")
