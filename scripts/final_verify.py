import pywikibot as pw

from maccabipediabot.common.wiki_login import get_site

site = get_site()

# Check parent category
cat = pw.Category(site, '\u05e7\u05d8\u05d2\u05d5\u05e8\u05d9\u05d4:\u05d6\u05db\u05d9\u05d5\u05ea \u05d1\u05ea\u05d0\u05e8\u05d9\u05dd')
subcats = list(cat.subcategories())
print(f'=== {cat.title()} ===')
print(f'Subcategories ({len(subcats)}):')
for sc in subcats:
    print(f'  {sc.title()}')

# Check new global
print()
global_cat = pw.Category(site, '\u05e7\u05d8\u05d2\u05d5\u05e8\u05d9\u05d4:\u05de\u05e9\u05d7\u05e7\u05d9 \u05d6\u05db\u05d9\u05d4 \u05d1\u05ea\u05d5\u05d0\u05e8')
subcats = list(global_cat.subcategories())
all_pages = list(global_cat.articles(recurse=True))
print(f'=== {global_cat.title()} ===')
print(f'Subcategories: {len(subcats)}')
for sc in subcats:
    sc_pages = list(sc.articles(recurse=True))
    print(f'  {sc.title()}: {len(sc_pages)} pages')
print(f'Total pages (recursive): {len(all_pages)}')
