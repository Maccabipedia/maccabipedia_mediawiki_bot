"""Map JSON paths in the Euroleague game-center __NEXT_DATA__ to wiki fields."""
import json
from pathlib import Path
from bs4 import BeautifulSoup

html = Path("packages/maccabipediabot/tests/basketball/fixtures/euroleague_game_E2025_R1.html").read_text("utf-8")
data = json.loads(BeautifulSoup(html, "html.parser").select_one("script#__NEXT_DATA__").text)
mapped = data["props"]["pageProps"]["mappedData"]

print("== mappedData top-level keys ==")
print(list(mapped.keys())[:30])

print("\n== rawGameInfo keys ==")
print(list(mapped["rawGameInfo"].keys()))

print("\n== home keys ==")
print(list(mapped["rawGameInfo"]["home"].keys()))

print("\n== home.coach ==")
print(json.dumps(mapped["rawGameInfo"]["home"].get("coach"), ensure_ascii=False, indent=2))

print("\n== home.players[0] full ==")
print(json.dumps(mapped["rawGameInfo"]["home"]["players"][0], ensure_ascii=False, indent=2))

# Quarter scores
print("\n== boxScores top keys ==")
print(list(mapped["boxScores"].keys()))
print("\n== boxScores.statsTable[0] full (home) ==")
print(json.dumps(mapped["boxScores"]["statsTable"][0], ensure_ascii=False, indent=2)[:2000])

# Venue / referees — search top-level rawGameInfo
print("\n== anything venue-like ==")
for k, v in mapped["rawGameInfo"].items():
    if k.lower() in {"venue", "stadium", "arena", "referees"}:
        print(f"  {k}: {json.dumps(v, ensure_ascii=False)[:300]}")
print("\n== full rawGameInfo (truncated) keys for stadium/refs ==")
flat = json.dumps(mapped["rawGameInfo"], ensure_ascii=False)
for kw in ("venue", "stadium", "arena", "referee"):
    idx = flat.lower().find(kw)
    if idx >= 0:
        print(f"  found '{kw}' near: ...{flat[max(0, idx-40):idx+200]}...")
