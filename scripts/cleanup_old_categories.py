"""Clean up old winning categories:
1. Remove [[קטגוריה:זכיות בתארים]] from old empty category pages
2. Remove manual tags from גביע ליליאן: זכיות pages
"""
import re
import sys

import pywikibot as pw

from maccabipediabot.common.wiki_login import get_site

DRY_RUN = '--save' not in sys.argv

site = get_site()

print(f'Mode: {"DRY RUN" if DRY_RUN else "SAVING"}\n')

# Part 1: Remove parent tag from old category pages
old_cats = [
    '\u05d0\u05dc\u05d5\u05e3 \u05d4\u05d0\u05dc\u05d5\u05e4\u05d9\u05dd: \u05d6\u05db\u05d9\u05d5\u05ea',
    '\u05d2\u05d1\u05d9\u05e2 \u05d0\u05e1\u05d9\u05d4 \u05dc\u05d0\u05dc\u05d5\u05e4\u05d5\u05ea: \u05d6\u05db\u05d9\u05d4',
    '\u05d2\u05d1\u05d9\u05e2 \u05d4\u05d8\u05d5\u05d8\u05d5: \u05d6\u05db\u05d9\u05d5\u05ea',
    '\u05d2\u05d1\u05d9\u05e2 \u05d4\u05de\u05d3\u05d9\u05e0\u05d4: \u05d6\u05db\u05d9\u05d5\u05ea',
    '\u05d2\u05d1\u05d9\u05e2 \u05dc\u05d9\u05dc\u05d9\u05d0\u05df: \u05d6\u05db\u05d9\u05d5\u05ea',
    '\u05de\u05e9\u05d7\u05e7\u05d9 \u05d0\u05dc\u05d9\u05e4\u05d5\u05ea',
]

parent_pattern = re.compile(r'\n?\[\[\u05e7\u05d8\u05d2\u05d5\u05e8\u05d9\u05d4:\s*\u05d6\u05db\u05d9\u05d5\u05ea \u05d1\u05ea\u05d0\u05e8\u05d9\u05dd[^\]]*\]\]')

print('=== Part 1: Remove parent tag from old category pages ===\n')
for cat_name in old_cats:
    page = pw.Page(site, '\u05e7\u05d8\u05d2\u05d5\u05e8\u05d9\u05d4:' + cat_name)
    if not page.exists():
        print(f'SKIP (not found): {cat_name}')
        continue

    match = parent_pattern.search(page.text)
    if not match:
        print(f'SKIP (no parent tag): {cat_name}')
        continue

    print(f'{cat_name}: will remove {match.group(0).strip()!r}')
    if not DRY_RUN:
        page.text = parent_pattern.sub('', page.text)
        page.save(summary='\u05d4\u05e1\u05e8\u05ea \u05e7\u05d8\u05d2\u05d5\u05e8\u05d9\u05d4 \u05d9\u05e9\u05e0\u05d4 \u2014 \u05d4\u05d5\u05d7\u05dc\u05e4\u05d4 \u05d1\u05de\u05e2\u05e8\u05db\u05ea \u05d7\u05d3\u05e9\u05d4', minor=True)
        page.purge(forcelinkupdate=True)
        print(f'  SAVED + PURGED')

# Part 2: Remove manual tags from גביע ליליאן: זכיות pages
print('\n=== Part 2: Check and remove גביע ליליאן: זכיות manual tags ===\n')

lilian_cat = pw.Category(site, '\u05e7\u05d8\u05d2\u05d5\u05e8\u05d9\u05d4:\u05d2\u05d1\u05d9\u05e2 \u05dc\u05d9\u05dc\u05d9\u05d0\u05df: \u05d6\u05db\u05d9\u05d5\u05ea')
if not lilian_cat.exists():
    print('Category does not exist')
else:
    pages = list(lilian_cat.articles())
    print(f'Found {len(pages)} pages\n')

    lilian_pattern = re.compile(r'\n?\[\[\u05e7\u05d8\u05d2\u05d5\u05e8\u05d9\u05d4:\s*\u05d2\u05d1\u05d9\u05e2 \u05dc\u05d9\u05dc\u05d9\u05d0\u05df[^\]]*\]\]')

    for p in pages:
        print(f'{p.title()}:')
        match = lilian_pattern.search(p.text)
        if match:
            print(f'  REMOVE: {match.group(0).strip()!r}')
            if not DRY_RUN:
                p.text = lilian_pattern.sub('', p.text)
                p.save(summary='\u05d4\u05e1\u05e8\u05ea \u05ea\u05d2 \u05e7\u05d8\u05d2\u05d5\u05e8\u05d9\u05d4 \u05d9\u05d3\u05e0\u05d9 \u2014 \u05de\u05d5\u05d7\u05dc\u05e3 \u05d0\u05d5\u05d8\u05d5\u05de\u05d8\u05d9\u05ea \u05e2\u05dc \u05d9\u05d3\u05d9 \u05d4\u05ea\u05d1\u05e0\u05d9\u05ea', minor=True)
                p.purge(forcelinkupdate=True)
                print(f'  SAVED + PURGED')
        else:
            print(f'  No manual tag found (template-driven)')

print('\nDone.')
if DRY_RUN:
    print('Run with --save to apply.')
