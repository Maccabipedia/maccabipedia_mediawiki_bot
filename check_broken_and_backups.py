import sys
sys.path.insert(0, "packages/maccabipediabot/src")

import asyncio
import aiohttp
import os
from pathlib import Path

BACKUP_ROOT = Path("/mnt/d/maccabipedia_google_drive/מכביפדיה_ראשי/וידאו/כדורגל/עונות")

BROKEN = [
    ("05-10-2023", "גנט נגד מכבי תל אביב", "הליגה האזורית", "תקציר ראשי", "https://www.youtube.com/watch?v=XChN1ZXjRxc"),
    ("07-03-2024", "אולימפיאקוס נגד מכבי תל אביב", "הליגה האזורית", "תקציר ראשי", "https://www.youtube.com/watch?v=_tyYolmzxhs"),
    ("13-07-2017", "מכבי תל אביב נגד קיי.אר. רייקיאוויק", "מוקדמות הליגה האירופית", "משחק מלא", "https://www.youtube.com/watch?v=tBKjlM6ZAEY&t=6s"),
    ("14-12-2002", "מכבי תל אביב נגד הפועל באר שבע", "ליגת העל", "משחק מלא", "https://www.youtube.com/watch?v=GPvWZggrLpI"),
    ("15-09-2004", "מכבי תל אביב נגד באיירן מינכן", "ליגת האלופות", "תקציר ראשי", "https://www.youtube.com/watch?v=OnG8XQRbc6_R_LpL"),
    ("16-09-1999", "מכבי תל אביב נגד לאנס", "גביע אופא", "משחק מלא", "https://www.youtube.com/watch?v=JwUrFyR75sY"),
    ("17-08-2017", "ריינדורף אלטאך נגד מכבי תל אביב", "הליגה האירופית", "משחק מלא", "https://www.youtube.com/watch?v=9DpFdGAzpnM"),
    ("20-02-2014", "מכבי תל אביב נגד פ.צ. באזל", "הליגה האירופית", "תקציר ראשי", "https://www.youtube.com/watch?v=pzqyA_0qXNk"),
    ("21-04-2021", "מ.ס. אשדוד נגד מכבי תל אביב", "גביע המדינה", "משחק מלא", "https://www.youtube.com/watch?v=MC8a79iKpxY"),
    ("21-08-2025", "מכבי תל אביב נגד דינמו קייב", "מוקדמות הליגה האירופית", "משחק מלא", "https://www.youtube.com/watch?v=OSSJDPanHn0"),
    ("22-12-2018", "בית\"ר ירושלים נגד מכבי תל אביב", "גביע המדינה", "תקציר משני", "https://www.youtube.com/watch?v=OSEUPJIQlp0"),
    ("28-08-2025", "דינמו קייב נגד מכבי תל אביב", "מוקדמות הליגה האירופית", "משחק מלא", "https://www.youtube.com/watch?v=yrllL64VjKA"),
    ("31-08-2023", "צליה נגד מכבי תל אביב", "הליגה האזורית", "משחק מלא", "https://www.youtube.com/watch?v=cfbvhDl9PPA"),
]


def date_to_season(date_str):
    day, month, year = date_str.split("-")
    month, year = int(month), int(year)
    if month >= 7:
        return f"{year}-{str(year+1)[-2:]}"
    else:
        return f"{year-1}-{str(year)[-2:]}"


def find_backup(date_str, opponents):
    season = date_to_season(date_str)
    season_path = BACKUP_ROOT / f"עונת {season}"
    if not season_path.exists():
        return None, season

    # Collect keywords from opponents (skip common words)
    skip = {"מכבי", "תל", "אביב", "נגד"}
    keywords = [w for w in opponents.replace(".", "").split() if w not in skip and len(w) > 2]

    day = date_str.split("-")[0]

    matches = []
    for f in season_path.rglob("*"):
        if f.is_file():
            name = f.name
            if day in name or any(k in name for k in keywords):
                matches.append(str(f.relative_to(BACKUP_ROOT.parent.parent)))
    return matches or None, season


async def check_url(session, url):
    oembed = f"https://www.youtube.com/oembed?url={url}&format=json"
    try:
        async with session.get(oembed, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            return resp.status != 200
    except Exception:
        return False


async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [check_url(session, url) for *_, url in BROKEN]
        results = await asyncio.gather(*tasks)

    for (date_str, opponents, competition, vtype, url), still_broken in zip(BROKEN, results):
        season = date_to_season(date_str)
        backups, _ = find_backup(date_str, opponents)
        status = "❌ BROKEN" if still_broken else "✅ fixed"
        backup_str = "\n    backup: " + ", ".join(backups) if backups else "\n    backup: none"
        print(f"{status}  {date_str} {opponents} ({competition}) [{vtype}]")
        if still_broken:
            print(f"    url: {url}{backup_str}")


asyncio.run(main())
