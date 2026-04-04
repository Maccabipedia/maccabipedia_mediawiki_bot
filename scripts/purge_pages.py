"""Purge winning-game pages so MediaWiki re-renders with new template categories.

Usage:
  uv run python scripts/purge_pages.py          # dry-run
  uv run python scripts/purge_pages.py --purge   # actually purge
"""
import sys

import pywikibot as pw

from maccabipediabot.common.wiki_login import get_site

DRY_RUN = '--purge' not in sys.argv

site = get_site()

FOOTBALL = '\u05de\u05e9\u05d7\u05e7\u05d9 \u05d6\u05db\u05d9\u05d4 \u05d1\u05ea\u05d5\u05d0\u05e8 (\u05db\u05d3\u05d5\u05e8\u05d2\u05dc)'
VOLLEYBALL = '\u05de\u05e9\u05d7\u05e7\u05d9 \u05d6\u05db\u05d9\u05d4 \u05d1\u05ea\u05d5\u05d0\u05e8 (\u05db\u05d3\u05d5\u05e8\u05e2\u05e3)'
BASKETBALL = '\u05de\u05e9\u05d7\u05e7\u05d9 \u05d6\u05db\u05d9\u05d4 \u05d1\u05ea\u05d5\u05d0\u05e8 (\u05db\u05d3\u05d5\u05e8\u05e1\u05dc)'
GLOBAL_CAT = '\u05de\u05e9\u05d7\u05e7\u05d9 \u05d6\u05db\u05d9\u05d4 \u05d1\u05ea\u05d5\u05d0\u05e8'
CAT_PREFIX = '\u05e7\u05d8\u05d2\u05d5\u05e8\u05d9\u05d4:'

sport_cats = [FOOTBALL, VOLLEYBALL, BASKETBALL]

pages_to_purge = set()

for cat_name in sport_cats:
    cat = pw.Category(site, CAT_PREFIX + cat_name)
    if not cat.exists():
        print(f'  (category not found: {cat_name})')
        continue
    members = list(cat.articles(recurse=True))
    print(f'{cat_name}: {len(members)} pages')
    for p in members:
        pages_to_purge.add(p.title())

for c in [GLOBAL_CAT, FOOTBALL, VOLLEYBALL, BASKETBALL]:
    pages_to_purge.add(CAT_PREFIX + c)

print(f'\nTotal: {len(pages_to_purge)} unique pages to purge')
print(f'Mode: {"DRY RUN" if DRY_RUN else "PURGING"}\n')

purged = 0
for title in sorted(pages_to_purge):
    if DRY_RUN:
        print(f'  WOULD PURGE: {title}')
    else:
        p = pw.Page(site, title)
        p.purge(forcelinkupdate=True)
        purged += 1
        if purged % 10 == 0:
            print(f'  Purged {purged}...')

print(f'\nDone. {"Would purge" if DRY_RUN else "Purged"}: {len(pages_to_purge) if DRY_RUN else purged}')
if DRY_RUN:
    print('Run with --purge to apply.')
