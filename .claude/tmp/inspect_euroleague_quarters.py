"""Inspect Euroleague quarter scores + venue + referees layout."""
import json
from pathlib import Path
from bs4 import BeautifulSoup

html = Path("packages/maccabipediabot/tests/basketball/fixtures/euroleague_game_E2025_R1.html").read_text("utf-8")
data = json.loads(BeautifulSoup(html, "html.parser").select_one("script#__NEXT_DATA__").text)
raw = data["props"]["pageProps"]["mappedData"]["rawGameInfo"]
mapped = data["props"]["pageProps"]["mappedData"]

print("== rawGameInfo.venue ==")
print(json.dumps(raw["venue"], ensure_ascii=False, indent=2))

print("\n== rawGameInfo.referees ==")
print(json.dumps(raw["referees"], ensure_ascii=False, indent=2))

print("\n== rawGameInfo.audience ==")
print(json.dumps(raw["audience"], ensure_ascii=False, indent=2))

print("\n== rawGameInfo.round ==")
print(json.dumps(raw["round"], ensure_ascii=False))

print("\n== rawGameInfo.home.score ==")
print(json.dumps(raw["home"]["score"], ensure_ascii=False))
print("== rawGameInfo.home.quarters ==")
print(json.dumps(raw["home"]["quarters"], ensure_ascii=False))

print("\n== rawGameInfo.away.quarters ==")
print(json.dumps(raw["away"]["quarters"], ensure_ascii=False))

print("\n== boxScores.byQuarterInfo ==")
print(json.dumps(mapped["boxScores"]["byQuarterInfo"], ensure_ascii=False, indent=2)[:1500])
