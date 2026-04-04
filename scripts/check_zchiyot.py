import pywikibot as pw

from maccabipediabot.common.wiki_login import get_site

site = get_site()

# Check זכיות בתארים category
cat = pw.Category(site, '\u05e7\u05d8\u05d2\u05d5\u05e8\u05d9\u05d4:\u05d6\u05db\u05d9\u05d5\u05ea \u05d1\u05ea\u05d0\u05e8\u05d9\u05dd')
print(f'Category: {cat.title()}')
print(f'Exists: {cat.exists()}')
print(f'Text:\n{cat.text}\n')

subcats = list(cat.subcategories())
print(f'Subcategories ({len(subcats)}):')
for sc in subcats:
    print(f'  {sc.title()}')
    sc_members = list(sc.articles())
    if sc_members:
        print(f'    Direct members: {len(sc_members)}')
    sc_subcats = list(sc.subcategories())
    if sc_subcats:
        for ssc in sc_subcats:
            print(f'    Sub: {ssc.title()}')

articles = list(cat.articles())
print(f'\nDirect articles ({len(articles)}):')
for a in articles:
    print(f'  {a.title()}')
