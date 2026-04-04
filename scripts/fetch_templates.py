import pywikibot as pw

from maccabipediabot.common.wiki_login import get_site

site = get_site()

for t in ['תבנית:קטלוג משחקים', 'תבנית:משחק כדורעף', 'תבנית:משחק כדורסל']:
    p = pw.Page(site, t)
    print(f'\n=== {t} ===')
    print(p.text)
