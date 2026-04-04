"""Find all manual winning-related category tags on ALL winning game pages (all sports)."""
import re

import pywikibot as pw

from maccabipediabot.common.wiki_login import get_site

site = get_site()

sport_cats = [
    '\u05de\u05e9\u05d7\u05e7\u05d9 \u05d6\u05db\u05d9\u05d4 \u05d1\u05ea\u05d5\u05d0\u05e8 (\u05db\u05d3\u05d5\u05e8\u05d2\u05dc)',
    '\u05de\u05e9\u05d7\u05e7\u05d9 \u05d6\u05db\u05d9\u05d4 \u05d1\u05ea\u05d5\u05d0\u05e8 (\u05db\u05d3\u05d5\u05e8\u05e2\u05e3)',
    '\u05de\u05e9\u05d7\u05e7\u05d9 \u05d6\u05db\u05d9\u05d4 \u05d1\u05ea\u05d5\u05d0\u05e8 (\u05db\u05d3\u05d5\u05e8\u05e1\u05dc)',
]

all_pages = {}
for cat_name in sport_cats:
    cat = pw.Category(site, '\u05e7\u05d8\u05d2\u05d5\u05e8\u05d9\u05d4:' + cat_name)
    if cat.exists():
        members = list(cat.articles(recurse=True))
        print(f'{cat_name}: {len(members)} pages')
        for p in members:
            all_pages[p.title()] = cat_name

print(f'\nTotal winning game pages: {len(all_pages)}\n')

cat_pattern = re.compile(r'\[\[\u05e7\u05d8\u05d2\u05d5\u05e8\u05d9\u05d4:\s*[^\]]+\]\]')

# Known winning-related old category patterns (זכיות/זכיה in category name)
winning_pattern = re.compile(r'\[\[\u05e7\u05d8\u05d2\u05d5\u05e8\u05d9\u05d4:\s*[^\]]*\u05d6\u05db\u05d9[^\]]*\]\]')

found = {}
for title in sorted(all_pages.keys()):
    page = pw.Page(site, title)
    text = page.text

    last_template_end = text.rfind('}}')
    if last_template_end == -1:
        continue
    after_template = text[last_template_end + 2:]
    matches = cat_pattern.findall(after_template)
    if matches:
        found[title] = {'sport': all_pages[title], 'cats': matches}

print(f'Pages with ANY manual category tags after template: {len(found)}\n')

unique_cats = set()
for title, info in sorted(found.items()):
    print(f'[{info["sport"]}] {title}:')
    for c in info['cats']:
        print(f'  {c}')
        cat_name = c.split('|')[0] + ']]'
        unique_cats.add(cat_name)

print(f'\nAll unique manual categories found ({len(unique_cats)}):')
for c in sorted(unique_cats):
    print(f'  {c}')
