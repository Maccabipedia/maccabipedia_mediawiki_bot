import pywikibot as pw

from maccabipediabot.common.wiki_login import get_site

site = get_site()

page = pw.Page(site, '\u05de\u05e9\u05d7\u05e7:02-02-1999 \u05d1\u05d9\u05ea"\u05e8 \u05d9\u05e8\u05d5\u05e9\u05dc\u05d9\u05dd \u05e0\u05d2\u05d3 \u05de\u05db\u05d1\u05d9 \u05ea\u05dc \u05d0\u05d1\u05d9\u05d1 - \u05d2\u05d1\u05d9\u05e2 \u05d4\u05d8\u05d5\u05d8\u05d5')
print(page.text[-500:])
