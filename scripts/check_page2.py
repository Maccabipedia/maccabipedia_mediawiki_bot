import pywikibot as pw

from maccabipediabot.common.wiki_login import get_site

site = get_site()

page = pw.Page(site, '\u05e7\u05d8\u05d2\u05d5\u05e8\u05d9\u05d4:\u05d2\u05d1\u05d9\u05e2 \u05d4\u05d8\u05d5\u05d8\u05d5: \u05d6\u05db\u05d9\u05d5\u05ea')
print(f'Title: {page.title()}')
print(f'Exists: {page.exists()}')
print(f'Text:\n{page.text}')
print()

cat = pw.Category(site, page.title())
members = list(cat.articles())
print(f'Members ({len(members)}):')
for m in members:
    print(f'  {m.title()}')
