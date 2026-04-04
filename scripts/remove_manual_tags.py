"""Remove manual [[קטגוריה:משחקי אליפות|...]] tags from football pages.

Usage:
  uv run python scripts/remove_manual_tags.py          # dry-run (default)
  uv run python scripts/remove_manual_tags.py --save    # actually save changes
"""
import re
import sys

import pywikibot as pw

from maccabipediabot.common.wiki_login import get_site

DRY_RUN = '--save' not in sys.argv

site = get_site()

cat = pw.Category(site, 'קטגוריה:משחקי אליפות')
pages = list(cat.articles())
print(f'Found {len(pages)} pages in משחקי אליפות')
print(f'Mode: {"DRY RUN" if DRY_RUN else "SAVING"}\n')

pattern = re.compile(r'\n?\[\[קטגוריה:\s*משחקי אליפות[^\]]*\]\]')

saved = 0
skipped = 0

for page in pages:
    original = page.text
    new_text = pattern.sub('', original)
    if new_text == original:
        print(f'SKIP (tag not in wikitext): {page.title()}')
        skipped += 1
        continue

    tag_match = pattern.search(original)
    print(f'{"WOULD REMOVE" if DRY_RUN else "REMOVING"}: {page.title()} — {tag_match.group(0).strip()!r}')

    if not DRY_RUN:
        page.text = new_text
        page.save(summary='הסרת תג קטגוריה ידני — מוחלף אוטומטית על ידי התבנית', minor=True)
        print(f'  SAVED: {page.title()}')
        saved += 1

print(f'\nDone. {"Would save" if DRY_RUN else "Saved"}: {saved}, Skipped: {skipped}')
if DRY_RUN:
    print('Run with --save to apply changes.')
