"""Find a Maccabi Euroleague game that went to overtime so we can round-trip a real OT parse.

Strategy: hit the team-results page, pull the full game list from __NEXT_DATA__,
fetch each game's __NEXT_DATA__, and look for any quarter dict with a non-null ot1.
Stop at the first OT game found.
"""
from maccabipediabot.basketball.crawl_euroleague import (
    discover_games_from_html,
    extract_next_data,
    fetch_html,
    TEAM_RESULTS_URL,
)

html = fetch_html(TEAM_RESULTS_URL)
metas = discover_games_from_html(html, limit=None)
print(f"scanning {len(metas)} games for OT…\n")
for meta in metas:
    gh = fetch_html(meta.scrape_url)
    nd = extract_next_data(gh)
    try:
        raw = nd["props"]["pageProps"]["mappedData"]["rawGameInfo"]
    except KeyError:
        continue
    h = raw.get("home", {}).get("quarters") or {}
    a = raw.get("away", {}).get("quarters") or {}
    if h.get("ot1") is not None or a.get("ot1") is not None:
        date = meta.game_date.strftime("%Y-%m-%d")
        print(f"  OT! {date}  {meta.opponent_name_eng}  home_ot1={h.get('ot1')} away_ot1={a.get('ot1')}")
        print(f"     url: {meta.scrape_url}")
        break
else:
    print("  no OT game in the current season's team-results page")
