"""Verify winning-games category hierarchy."""
import pywikibot as pw

from maccabipediabot.common.wiki_login import get_site

site = get_site()

CAT_PREFIX = '\u05e7\u05d8\u05d2\u05d5\u05e8\u05d9\u05d4:'

# Check global category
global_cat = pw.Category(site, CAT_PREFIX + '\u05de\u05e9\u05d7\u05e7\u05d9 \u05d6\u05db\u05d9\u05d4 \u05d1\u05ea\u05d5\u05d0\u05e8')
subcats = list(global_cat.subcategories())
print(f'Global category subcategories ({len(subcats)}):')
for sc in subcats:
    print(f'  {sc.title()}')

print()

# Check each sport category
for sport_name in [
    '\u05de\u05e9\u05d7\u05e7\u05d9 \u05d6\u05db\u05d9\u05d4 \u05d1\u05ea\u05d5\u05d0\u05e8 (\u05db\u05d3\u05d5\u05e8\u05d2\u05dc)',
    '\u05de\u05e9\u05d7\u05e7\u05d9 \u05d6\u05db\u05d9\u05d4 \u05d1\u05ea\u05d5\u05d0\u05e8 (\u05db\u05d3\u05d5\u05e8\u05e2\u05e3)',
    '\u05de\u05e9\u05d7\u05e7\u05d9 \u05d6\u05db\u05d9\u05d4 \u05d1\u05ea\u05d5\u05d0\u05e8 (\u05db\u05d3\u05d5\u05e8\u05e1\u05dc)',
]:
    cat = pw.Category(site, CAT_PREFIX + sport_name)
    subcats = list(cat.subcategories())
    articles = list(cat.articles(recurse=True))
    print(f'{sport_name}:')
    print(f'  Subcategories: {len(subcats)}')
    for sc in subcats:
        sc_articles = list(sc.articles())
        print(f'    {sc.title()} ({len(sc_articles)} pages)')
    print(f'  Total pages (recursive): {len(articles)}')
    print()

# Check old categories are empty
for old_cat_name in [
    '\u05de\u05e9\u05d7\u05e7\u05d9 \u05d0\u05dc\u05d9\u05e4\u05d5\u05ea',
    '\u05d2\u05d1\u05d9\u05e2 \u05d4\u05de\u05d3\u05d9\u05e0\u05d4: \u05d6\u05db\u05d9\u05d5\u05ea',
    '\u05d2\u05d1\u05d9\u05e2 \u05d4\u05d8\u05d5\u05d8\u05d5: \u05d6\u05db\u05d9\u05d5\u05ea',
    '\u05d0\u05dc\u05d5\u05e3 \u05d4\u05d0\u05dc\u05d5\u05e4\u05d9\u05dd: \u05d6\u05db\u05d9\u05d5\u05ea',
    '\u05d2\u05d1\u05d9\u05e2 \u05d0\u05e1\u05d9\u05d4 \u05dc\u05d0\u05dc\u05d5\u05e4\u05d5\u05ea: \u05d6\u05db\u05d9\u05d4',
]:
    cat = pw.Category(site, CAT_PREFIX + old_cat_name)
    if cat.exists():
        articles = list(cat.articles())
        print(f'OLD: {old_cat_name} — {len(articles)} pages remaining')
    else:
        print(f'OLD: {old_cat_name} — does not exist')
