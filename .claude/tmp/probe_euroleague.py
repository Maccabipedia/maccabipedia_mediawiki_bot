"""Probe euroleague pages to see if static HTML contains the data the TS Puppeteer scrape needs."""
import requests
from bs4 import BeautifulSoup

TEAM_URL = "https://www.euroleaguebasketball.net/en/euroleague/teams/maccabi-rapyd-tel-aviv/games/tel/"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

resp = requests.get(TEAM_URL, headers=HEADERS, timeout=30)
print(f"team_page status={resp.status_code} len={len(resp.text)}")
soup = BeautifulSoup(resp.text, "html.parser")

results_section = soup.select('section[class*="team-results_section"]')
print(f"team-results_section count: {len(results_section)}")

articles = soup.select("article")
print(f"top-level articles: {len(articles)}")

# Check for Next.js __NEXT_DATA__ which often contains everything pre-rendered
next_data = soup.select_one("script#__NEXT_DATA__")
print(f"__NEXT_DATA__ present: {bool(next_data)} (len={len(next_data.text) if next_data else 0})")

# Also try a known REST/JSON endpoint pattern for Euroleague
api_candidates = [
    "https://api-live.euroleague.net/v1/games?seasonCode=E2025&clubcode=TEL",
    "https://feeds.incrowdsports.com/provider/euroleague-feeds/v2/competitions/E/seasons/E2025/clubs/TEL/games",
]
for url in api_candidates:
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        print(f"{url} -> {r.status_code} ({r.headers.get('Content-Type')}) len={len(r.text)}")
    except Exception as e:
        print(f"{url} -> error {e}")
