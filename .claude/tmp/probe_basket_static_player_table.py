"""See whether the existing python crawler's selector ('שם שחקן' tables) actually finds data on basket.co.il game-zone.asp without JS."""
import re
import sys

import requests
from bs4 import BeautifulSoup

GAME_ID = sys.argv[1] if len(sys.argv) > 1 else "26383"
URL = f"https://basket.co.il/game-zone.asp?GameId={GAME_ID}"

resp = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
print(f"status={resp.status_code} len={len(resp.text)}")
soup = BeautifulSoup(resp.text, "html.parser")

# selector used by existing Python crawler
player_tables = soup.find_all(
    lambda tag: tag.name == "table" and "שם שחקן" in tag.get_text()
)
print(f"player tables ('שם שחקן' tables): {len(player_tables)}")

print(f"\nany 'מכבי' in HTML: {'מכבי' in resp.text}")
print(f"any 'גילבוע' or 'הפועל' (likely opponent today): {bool(re.search(r'גילבוע|הפועל', resp.text))}")

# Look for hidden API/JSON endpoints fetched by the JS
endpoints = sorted(set(re.findall(r'(/[^\s"\'<>]+\.(?:asp|json|aspx)\?[^\s"\'<>]+)', resp.text)))
print(f"\nasp/json endpoints found in HTML ({len(endpoints)}):")
for e in endpoints[:20]:
    print(f"  {e}")
