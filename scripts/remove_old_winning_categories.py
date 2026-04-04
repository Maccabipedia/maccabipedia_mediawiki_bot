"""Remove old manual winning-category tags from game pages.

Removes: גביע המדינה: זכיות, גביע הטוטו: זכיות, אלוף האלופים: זכיות,
         גביע אסיה לאלופות: זכיה, משחקי אליפות
Does NOT remove unrelated categories like משחקים עם שלושה שערים לשחקן.

Usage:
  uv run python scripts/remove_old_winning_categories.py          # dry-run
  uv run python scripts/remove_old_winning_categories.py --save    # save
"""
import re
import sys

import pywikibot as pw

from maccabipediabot.common.wiki_login import get_site

DRY_RUN = '--save' not in sys.argv

site = get_site()

sport_cats = [
    '\u05de\u05e9\u05d7\u05e7\u05d9 \u05d6\u05db\u05d9\u05d4 \u05d1\u05ea\u05d5\u05d0\u05e8 (\u05db\u05d3\u05d5\u05e8\u05d2\u05dc)',
    '\u05de\u05e9\u05d7\u05e7\u05d9 \u05d6\u05db\u05d9\u05d4 \u05d1\u05ea\u05d5\u05d0\u05e8 (\u05db\u05d3\u05d5\u05e8\u05e2\u05e3)',
    '\u05de\u05e9\u05d7\u05e7\u05d9 \u05d6\u05db\u05d9\u05d4 \u05d1\u05ea\u05d5\u05d0\u05e8 (\u05db\u05d3\u05d5\u05e8\u05e1\u05dc)',
]

all_pages = set()
for cat_name in sport_cats:
    cat = pw.Category(site, '\u05e7\u05d8\u05d2\u05d5\u05e8\u05d9\u05d4:' + cat_name)
    if cat.exists():
        for p in cat.articles(recurse=True):
            all_pages.add(p.title())

print(f'Total winning game pages: {len(all_pages)}')
print(f'Mode: {"DRY RUN" if DRY_RUN else "SAVING"}\n')

# Old winning categories to remove (pattern matches the category name before |)
OLD_CATS = [
    '\u05d2\u05d1\u05d9\u05e2 \u05d4\u05de\u05d3\u05d9\u05e0\u05d4: \u05d6\u05db\u05d9\u05d5\u05ea',      # גביע המדינה: זכיות
    '\u05d2\u05d1\u05d9\u05e2 \u05d4\u05d8\u05d5\u05d8\u05d5: \u05d6\u05db\u05d9\u05d5\u05ea',      # גביע הטוטו: זכיות
    '\u05d0\u05dc\u05d5\u05e3 \u05d4\u05d0\u05dc\u05d5\u05e4\u05d9\u05dd: \u05d6\u05db\u05d9\u05d5\u05ea',  # אלוף האלופים: זכיות
    '\u05d2\u05d1\u05d9\u05e2 \u05d0\u05e1\u05d9\u05d4 \u05dc\u05d0\u05dc\u05d5\u05e4\u05d5\u05ea: \u05d6\u05db\u05d9\u05d4',  # גביע אסיה לאלופות: זכיה
    '\u05de\u05e9\u05d7\u05e7\u05d9 \u05d0\u05dc\u05d9\u05e4\u05d5\u05ea',  # משחקי אליפות
]

# Build regex: match [[קטגוריה: OLD_CAT_NAME...]]  with optional leading newline
old_cat_patterns = []
for cat_name in OLD_CATS:
    pattern = re.compile(r'\n?\[\[\u05e7\u05d8\u05d2\u05d5\u05e8\u05d9\u05d4:\s*' + re.escape(cat_name) + r'[^\]]*\]\]')
    old_cat_patterns.append((cat_name, pattern))

saved = 0
for title in sorted(all_pages):
    page = pw.Page(site, title)
    original = page.text
    new_text = original

    removed = []
    for cat_name, pattern in old_cat_patterns:
        match = pattern.search(new_text)
        if match:
            removed.append(match.group(0).strip())
            new_text = pattern.sub('', new_text)

    if not removed:
        continue

    print(f'{title}:')
    for r in removed:
        print(f'  REMOVE: {r}')

    if not DRY_RUN:
        page.text = new_text
        page.save(summary='\u05d4\u05e1\u05e8\u05ea \u05ea\u05d2 \u05e7\u05d8\u05d2\u05d5\u05e8\u05d9\u05d4 \u05d9\u05d3\u05e0\u05d9 \u2014 \u05de\u05d5\u05d7\u05dc\u05e3 \u05d0\u05d5\u05d8\u05d5\u05de\u05d8\u05d9\u05ea \u05e2\u05dc \u05d9\u05d3\u05d9 \u05d4\u05ea\u05d1\u05e0\u05d9\u05ea', minor=True)
        print(f'  SAVED')
        saved += 1

print(f'\nDone. {"Would save" if DRY_RUN else "Saved"}: {saved if not DRY_RUN else "N/A"}, Total with old tags found: {saved if not DRY_RUN else "see above"}')
if DRY_RUN:
    print('Run with --save to apply changes.')
