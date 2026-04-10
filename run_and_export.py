import asyncio
import sys
sys.path.insert(0, "packages/maccabipediabot/src")

from collections import defaultdict
from datetime import date
from maccabipediabot.maintenance.videos.find_broken_videos import _find_broken_videos, format_report

broken = asyncio.run(_find_broken_videos())
print(f"Total broken: {len(broken)}", file=sys.stderr)

with open("broken_videos.html", "w", encoding="utf-8") as f:
    f.write("""<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
<meta charset="UTF-8">
<title>סרטונים שבורים</title>
<style>
  body { font-family: Arial, sans-serif; margin: 2em; background: #f5f5f5; }
  h1 { color: #c00; }
  .game { background: white; border-radius: 6px; padding: 1em 1.5em; margin: 0.8em 0; box-shadow: 0 1px 3px rgba(0,0,0,.15); }
  .game-title { font-weight: bold; margin-bottom: 0.4em; }
  .video-row { margin: 0.2em 0 0.2em 1em; }
  .label { color: #555; }
  a { color: #1a0dab; }
  .summary { color: #555; margin-bottom: 1.5em; }
</style>
</head>
<body>
""")
    f.write(f"<h1>סרטונים שבורים — {date.today()}</h1>\n")
    f.write(f'<p class="summary">נמצאו {len(broken)} סרטונים שבורים</p>\n')

    by_page = defaultdict(list)
    for v in broken:
        by_page[v.page_name].append(v)

    for page_name, videos in sorted(by_page.items()):
        wiki_url = "https://www.maccabipedia.co.il/" + page_name.replace(" ", "_")
        f.write('<div class="game">\n')
        f.write(f'  <div class="game-title"><a href="{wiki_url}" target="_blank">{page_name}</a></div>\n')
        for v in videos:
            f.write(f'  <div class="video-row">❌ <span class="label">{v.video_type}:</span> <a href="{v.url}" target="_blank">{v.url}</a></div>\n')
        f.write('</div>\n')

    f.write("</body></html>\n")

print("Written to broken_videos.html", file=sys.stderr)
