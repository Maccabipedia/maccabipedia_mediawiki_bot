import asyncio
import logging
from dataclasses import dataclass
from datetime import date

import aiohttp
import requests

logger = logging.getLogger(__name__)

CARGO_URL = (
    "https://www.maccabipedia.co.il/index.php"
    "?title=Special:CargoExport&format=json"
    "&tables=Games_Videos"
    "&fields=_pageName,FullGame,Highlights,Highlights2"
    "&limit=5000&offset=0"
)
OEMBED_URL = "https://www.youtube.com/oembed?url={url}&format=json"
MAX_CONCURRENT = 20

VIDEO_TYPE_LABELS = {
    "FullGame": "משחק מלא",
    "Highlights": "תקציר ראשי",
    "Highlights2": "תקציר משני",
}


@dataclass
class BrokenVideo:
    page_name: str
    url: str
    video_type: str


def format_report(broken: list[BrokenVideo], report_date: date) -> str:
    by_page: dict[str, list[BrokenVideo]] = {}
    for v in broken:
        by_page.setdefault(v.page_name, []).append(v)

    lines = [f"סרטונים שבורים — {report_date} — נמצאו {len(broken)}"]
    for page_name, videos in sorted(by_page.items()):
        lines.append("")
        lines.append(page_name)
        for v in videos:
            lines.append(f"  ❌ {v.video_type}: {v.url}")
    return "\n".join(lines)


def fetch_game_videos() -> list[dict]:
    response = requests.get(CARGO_URL)
    response.raise_for_status()
    return response.json()


def _is_youtube_url(url: str) -> bool:
    return "youtube.com" in url or "youtu.be" in url


async def is_video_broken(session: aiohttp.ClientSession, url: str) -> bool:
    if _is_youtube_url(url):
        oembed = OEMBED_URL.format(url=url)
        try:
            async with session.get(oembed) as resp:
                return resp.status != 200
        except Exception:
            logger.exception("Error checking YouTube URL %s — skipping", url)
            return False
    else:
        try:
            async with session.head(url, allow_redirects=True) as resp:
                return resp.status >= 400
        except Exception:
            logger.exception("Error checking URL %s — skipping", url)
            return False


async def _find_broken_videos() -> list[BrokenVideo]:
    rows = fetch_game_videos()
    sem = asyncio.Semaphore(MAX_CONCURRENT)
    broken: list[BrokenVideo] = []

    async def check(session: aiohttp.ClientSession, page_name: str, url: str, field: str) -> None:
        async with sem:
            if await is_video_broken(session, url):
                broken.append(BrokenVideo(
                    page_name=page_name,
                    url=url,
                    video_type=VIDEO_TYPE_LABELS[field],
                ))

    async with aiohttp.ClientSession() as session:
        tasks = [
            check(session, row["_pageName"], url, field)
            for row in rows
            for field in VIDEO_TYPE_LABELS
            if (url := row.get(field))
        ]
        await asyncio.gather(*tasks)

    return broken


def main() -> None:
    logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
    broken = asyncio.run(_find_broken_videos())
    if broken:
        print(format_report(broken, date.today()))


if __name__ == "__main__":
    main()
