import pywikibot as pw

from maccabipediabot.common.wiki_login import get_site

site = get_site()

page = pw.Page(site, 'משחק:08-06-1968 מכבי תל אביב נגד הפועל פתח תקווה - ליגה לאומית')
print(page.text)
