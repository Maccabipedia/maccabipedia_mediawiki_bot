"""Find game-page URL pattern on basket.co.il team page."""
import re

import requests

URL = "https://basket.co.il/team.asp?TeamId=1096"
resp = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
print(f"status={resp.status_code} len={len(resp.text)}")

candidates = set(re.findall(r'href="([^"]*game[^"]*)"', resp.text, re.IGNORECASE))
for c in sorted(candidates):
    print(f"  {c}")
