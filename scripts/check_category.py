import pywikibot as pw

from maccabipediabot.common.wiki_login import get_site

site = get_site()

cat = pw.Category(site, 'קטגוריה:משחקי אליפות')
print(f'Category exists: {cat.exists()}')
print(f'Category text:\n{cat.text}\n')

pages = list(cat.articles())
print(f'Number of pages: {len(pages)}')
for p in pages:
    print(f'  {p.title()}')
