import asyncio
import logging
from dataclasses import dataclass
from datetime import date

import aiohttp
import requests

logger = logging.getLogger(__name__)

CARGO_BASE = (
    "https://www.maccabipedia.co.il/index.php"
    "?title=Special:CargoExport&format=json"
    "&limit=5000&offset=0"
)
OEMBED_URL = "https://www.youtube.com/oembed?url={url}&format=json"
MAX_CONCURRENT = 20

_FOOTBALL_FIELDS = {
    "FullGame": "משחק מלא",
    "Highlights": "תקציר ראשי",
    "Highlights2": "תקציר משני",
}
_BALL_SPORTS_FIELDS = {
    "FullGameVideo": "משחק מלא",
    "FullGameVideo2": "משחק מלא 2",
    "HighlightsVideo": "תקציר ראשי",
    "HighlightsVideo2": "תקציר משני",
    "FansVideo": "וידאו אוהדים",
}

VIDEO_TABLES: list[tuple[str, dict[str, str]]] = [
    ("Games_Videos", _FOOTBALL_FIELDS),
    ("Volleyball_Games", _BALL_SPORTS_FIELDS),
    ("Basketball_Games", _BALL_SPORTS_FIELDS),
]


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


def _fetch_from_table(table: str, fields: dict[str, str]) -> list[tuple[str, str, str]]:
    """Returns (page_name, url, label) for every non-null video URL in the given table."""
    fields_str = "_pageName," + ",".join(fields.keys())
    response = requests.get(f"{CARGO_BASE}&tables={table}&fields={fields_str}")
    response.raise_for_status()
    result = []
    for row in response.json():
        page_name = row["_pageName"]
        for field, label in fields.items():
            video_url = row.get(field)
            if video_url:
                result.append((page_name, video_url, label))
    return result


def fetch_game_videos() -> list[tuple[str, str, str]]:
    """Returns (page_name, url, label) for all non-null video URLs across all sports."""
    all_videos: list[tuple[str, str, str]] = []
    for table, fields in VIDEO_TABLES:
        all_videos.extend(_fetch_from_table(table, fields))
    return all_videos


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
    entries = fetch_game_videos()
    sem = asyncio.Semaphore(MAX_CONCURRENT)
    broken: list[BrokenVideo] = []

    async def check(session: aiohttp.ClientSession, page_name: str, url: str, label: str) -> None:
        async with sem:
            if await is_video_broken(session, url):
                broken.append(BrokenVideo(page_name=page_name, url=url, video_type=label))

    async with aiohttp.ClientSession() as session:
        tasks = [check(session, page_name, url, label) for page_name, url, label in entries]
        await asyncio.gather(*tasks)

    return broken


def main() -> None:
    logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
    broken = asyncio.run(_find_broken_videos())
    if broken:
        print(format_report(broken, date.today()))


if __name__ == "__main__":
    main()
