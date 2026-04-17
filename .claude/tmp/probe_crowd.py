"""Find where crowd ('צופים:') lives in basket.co.il game-zone HTML."""
from pathlib import Path
import re

import requests
from bs4 import BeautifulSoup

# Use the same fixture we already have
html = Path("packages/maccabipediabot/tests/basketball/fixtures/basket_co_il_game_26383.html").read_bytes().decode("utf-8")
print(f"fixture has 'צופים:': {'צופים:' in html}")

# Find context around צופים:
for m in re.finditer(r"צופים:[^<]{0,200}", html):
    print(f"  match: {m.group(0)[:200]!r}")

# Now check the live game we just compared
resp = requests.get("https://basket.co.il/game-zone.asp?GameId=26503", headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
resp.encoding = "utf-8"
print(f"\nlive 26503 has 'צופים:': {'צופים:' in resp.text}")
for m in re.finditer(r"צופים:[^<]{0,200}", resp.text):
    print(f"  match: {m.group(0)[:200]!r}")

# What does our current parser see?
soup = BeautifulSoup(resp.text, "html.parser")
container = soup.select_one("#wrap_inner_3")
h5 = container.select_one("h5") if container else None
print(f"\nh5 element present: {bool(h5)}")
print(f"h5 text: {h5.get_text(' ', strip=True)[:200] if h5 else None}")
crowd_div = h5.select_one("div.link-1") if h5 else None
print(f"h5 div.link-1: {crowd_div.get_text(' ', strip=True)[:200] if crowd_div else None}")

# Try alternative: is צופים: in the whole header container?
if container:
    cont_text = container.get_text(" ", strip=True)
    if "צופים" in cont_text:
        idx = cont_text.find("צופים")
        print(f"\ncontainer text around 'צופים': {cont_text[idx:idx+100]!r}")
