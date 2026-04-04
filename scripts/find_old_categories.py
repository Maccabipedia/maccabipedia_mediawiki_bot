"""Find all manual winning-related category tags on winning game pages."""
import re

import pywikibot as pw

from maccabipediabot.common.wiki_login import get_site

site = get_site()

# Get all winning game pages from the 3 sport categories
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

print(f'Total winning game pages: {len(all_pages)}\n')

# Find manual category tags (outside of template {{ }})
# Look for [[קטגוריה:...]] that appear after the template closing }}
cat_pattern = re.compile(r'\[\[\u05e7\u05d8\u05d2\u05d5\u05e8\u05d9\u05d4:\s*[^\]]+\]\]')

found = {}
for title in sorted(all_pages):
    page = pw.Page(site, title)
    text = page.text

    # Find categories after the last }}
    last_template_end = text.rfind('}}')
    if last_template_end == -1:
        continue
    after_template = text[last_template_end + 2:]
    matches = cat_pattern.findall(after_template)
    if matches:
        found[title] = matches

print(f'Pages with manual category tags: {len(found)}\n')

# Collect unique category names
unique_cats = set()
for title, cats in sorted(found.items()):
    print(f'{title}:')
    for c in cats:
        print(f'  {c}')
        unique_cats.add(c.split('|')[0] + ']]')

print(f'\nUnique manual categories found:')
for c in sorted(unique_cats):
    print(f'  {c}')
