"""Map JSON paths in the Euroleague team-results page __NEXT_DATA__."""
import json
from pathlib import Path
from bs4 import BeautifulSoup

html = Path("packages/maccabipediabot/tests/basketball/fixtures/euroleague_team_results.html").read_text("utf-8")
data = json.loads(BeautifulSoup(html, "html.parser").select_one("script#__NEXT_DATA__").text)
results = data["props"]["pageProps"]["results"]["results"]

print(f"== {len(results)} games ==\n")
print("First game keys:")
print(list(results[0].keys()))
print("\nFirst game (truncated):")
print(json.dumps(results[0], ensure_ascii=False, indent=2)[:1500])
print("\nDistinct status values:")
print(set(g.get("status") for g in results))
