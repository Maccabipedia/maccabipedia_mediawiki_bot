"""Encoding-aware probe of basket.co.il game-zone.asp."""
import sys
import requests
from bs4 import BeautifulSoup

GAME_ID = sys.argv[1] if len(sys.argv) > 1 else "26383"
URL = f"https://basket.co.il/game-zone.asp?GameId={GAME_ID}"

resp = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
print(f"requests.encoding (auto): {resp.encoding}")
print(f"apparent_encoding: {resp.apparent_encoding}")
resp.encoding = "utf-8"  # force
soup = BeautifulSoup(resp.text, "html.parser")

container = soup.select_one("#wrap_inner_3")
print(f"\n#wrap_inner_3 h4: {container.select_one('h4').get_text(' ', strip=True)[:120] if container else None}")
print(f"#wrap_inner_3 h5: {container.select_one('h5').get_text(' ', strip=True)[:120] if container else None}")
print(f"#wrap_inner_3 h6: {container.select_one('h6').get_text(' ', strip=True)[:120] if container else None}")

cats = soup.select("table.stats_tbl.categories")
print(f"\ntables.stats_tbl.categories: {len(cats)}")
if cats:
    rows = cats[0].select("tr")
    for r in rows[:5]:
        cells = [td.get_text(strip=True) for td in r.select("td")]
        print(f"  row: {cells}")

stats_tables = soup.select("table.stats_tbl")
print(f"\nplayer tables (3rd & 4th of stats_tbl): rows={len(stats_tables[2].select('tr')) if len(stats_tables) > 2 else 'n/a'}")
if len(stats_tables) > 2:
    for r in stats_tables[2].select("tr")[:3]:
        cells = [td.get_text(strip=True) for td in r.select("td")]
        print(f"  row: {cells}")
