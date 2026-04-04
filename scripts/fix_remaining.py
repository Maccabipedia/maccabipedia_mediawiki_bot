"""Remove old tags from 6 remaining הגביע הארץ ישראלי pages and purge them."""
import re
import sys

import pywikibot as pw

from maccabipediabot.common.wiki_login import get_site

DRY_RUN = '--save' not in sys.argv

site = get_site()

cat = pw.Category(site, '\u05e7\u05d8\u05d2\u05d5\u05e8\u05d9\u05d4:\u05d2\u05d1\u05d9\u05e2 \u05d4\u05de\u05d3\u05d9\u05e0\u05d4: \u05d6\u05db\u05d9\u05d5\u05ea')
pages = list(cat.articles())
print(f'{len(pages)} pages to fix')
print(f'Mode: {"DRY RUN" if DRY_RUN else "SAVING"}\n')

pattern = re.compile(r'\n?\[\[\u05e7\u05d8\u05d2\u05d5\u05e8\u05d9\u05d4:\s*\u05d2\u05d1\u05d9\u05e2 \u05d4\u05de\u05d3\u05d9\u05e0\u05d4[^\]]*\]\]')

for p in pages:
    match = pattern.search(p.text)
    if not match:
        print(f'SKIP (no tag): {p.title()}')
        continue

    print(f'{p.title()}: {match.group(0).strip()}')
    if not DRY_RUN:
        p.text = pattern.sub('', p.text)
        p.save(summary='\u05d4\u05e1\u05e8\u05ea \u05ea\u05d2 \u05e7\u05d8\u05d2\u05d5\u05e8\u05d9\u05d4 \u05d9\u05d3\u05e0\u05d9 \u2014 \u05de\u05d5\u05d7\u05dc\u05e3 \u05d0\u05d5\u05d8\u05d5\u05de\u05d8\u05d9\u05ea \u05e2\u05dc \u05d9\u05d3\u05d9 \u05d4\u05ea\u05d1\u05e0\u05d9\u05ea', minor=True)
        p.purge(forcelinkupdate=True)
        print(f'  SAVED + PURGED')

print('\nDone.')
