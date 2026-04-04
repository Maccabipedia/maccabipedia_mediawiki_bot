import pywikibot as pw

from maccabipediabot.common.wiki_login import get_site

site = get_site()

templates = [
    {
        'title': 'תבנית:קטלוג משחקים',
        'sport_cat': 'משחקי זכיה בתואר (כדורגל)',
        'existing_line': '-->{{#תנאי: {{{משחק זכיה|}}} |[[קטגוריה: משחקי זכיה ב{{{מפעל|}}} (כדורגל)]]}}<!--',
    },
    {
        'title': 'תבנית:משחק כדורעף',
        'sport_cat': 'משחקי זכיה בתואר (כדורעף)',
        'existing_line': '-->{{#תנאי: {{{משחק זכיה|}}} |[[קטגוריה: משחקי זכיה ב{{{מפעל|}}} (כדורעף)]]}}<!--',
    },
    {
        'title': 'תבנית:משחק כדורסל',
        'sport_cat': 'משחקי זכיה בתואר (כדורסל)',
        'existing_line': '-->{{#תנאי: {{{משחק זכיה|}}} |[[קטגוריה: משחקי זכיה ב{{{מפעל|}}} (כדורסל)]]}}<!--',
    },
]

GLOBAL_CAT = 'משחקי זכיה בתואר'

for tpl in templates:
    page = pw.Page(site, tpl['title'])
    text = page.text

    sport_line = f'-->{{{{#תנאי: {{{{{{משחק זכיה|}}}}}} |[[קטגוריה: {tpl["sport_cat"]}|{{{{{{עונה|}}}}}}]]}}}}<!--'
    global_line = f'-->{{{{#תנאי: {{{{{{משחק זכיה|}}}}}} |[[קטגוריה: {GLOBAL_CAT}|{{{{{{עונה|}}}}}}]]}}}}<!--'

    if GLOBAL_CAT + '|' in text:
        print(f'SKIP (already updated): {tpl["title"]}')
        continue

    existing = tpl['existing_line']
    if existing not in text:
        print(f'ERROR: could not find insertion point in {tpl["title"]}')
        print(f'Looking for: {existing!r}')
        continue

    replacement = existing + '\n' + sport_line + '\n' + global_line
    new_text = text.replace(existing, replacement, 1)

    print(f'\n--- {tpl["title"]} diff ---')
    print(f'BEFORE: {existing}')
    print(f'AFTER:  {replacement}')

    page.text = new_text
    page.save(summary='הוספת קטגוריות זכיה בתואר לתבנית', minor=False)
    print(f'SAVED: {tpl["title"]}')
