import pywikibot as pw

from maccabipediabot.common.wiki_login import get_site

site = get_site()

categories = [
    (
        'קטגוריה:משחקי זכיה בתואר',
        'קטגוריה של כל משחקי הזכיה בתואר של מכבי תל אביב — כל הספורטים.\n\n[[קטגוריה:זכיות בתארים]]'
    ),
    (
        'קטגוריה:משחקי זכיה בתואר (כדורגל)',
        'קטגוריה של כל משחקי הזכיה בתואר של מכבי תל אביב בכדורגל.\n\n[[קטגוריה:משחקי זכיה בתואר]]'
    ),
    (
        'קטגוריה:משחקי זכיה בתואר (כדורעף)',
        'קטגוריה של כל משחקי הזכיה בתואר של מכבי תל אביב בכדורעף.\n\n[[קטגוריה:משחקי זכיה בתואר]]'
    ),
    (
        'קטגוריה:משחקי זכיה בתואר (כדורסל)',
        'קטגוריה של כל משחקי הזכיה בתואר של מכבי תל אביב בכדורסל.\n\n[[קטגוריה:משחקי זכיה בתואר]]'
    ),
]

for title, text in categories:
    page = pw.Page(site, title)
    if page.exists():
        print(f'SKIP (exists): {title}')
        continue
    page.text = text
    page.save(summary='יצירת קטגוריית משחקי זכיה בתואר', minor=False)
    print(f'CREATED: {title}')
