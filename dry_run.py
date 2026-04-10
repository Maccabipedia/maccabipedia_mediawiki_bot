import sys, asyncio
sys.path.insert(0, "packages/maccabipediabot/src")
from maccabipediabot.maintenance.videos.find_broken_videos import _find_broken_videos, format_report
from datetime import date

broken = asyncio.run(_find_broken_videos())
print(format_report(broken, date.today()))
