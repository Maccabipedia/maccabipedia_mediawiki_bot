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
