import pywikibot as pw

from maccabipediabot.common.wiki_login import get_site

site = get_site()

cat = pw.Category(site, '\u05e7\u05d8\u05d2\u05d5\u05e8\u05d9\u05d4:\u05d2\u05d1\u05d9\u05e2 \u05d4\u05de\u05d3\u05d9\u05e0\u05d4: \u05d6\u05db\u05d9\u05d5\u05ea')
pages = list(cat.articles())
print(f'{len(pages)} pages still in old category:')
for p in pages:
    print(f'  {p.title()}')
    # Check if page still has the old tag
    import re
    pattern = re.compile(r'\[\[\u05e7\u05d8\u05d2\u05d5\u05e8\u05d9\u05d4:\s*\u05d2\u05d1\u05d9\u05e2 \u05d4\u05de\u05d3\u05d9\u05e0\u05d4[^\]]*\]\]')
    match = pattern.search(p.text)
    if match:
        print(f'    STILL HAS TAG: {match.group(0)}')
    else:
        print(f'    Tag removed (cache stale)')
