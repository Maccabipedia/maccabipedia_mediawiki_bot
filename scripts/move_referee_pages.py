import logging

from pywikibot import pagegenerators, Category

from pywikibot_boilerplate import run_boilerplate

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)

# We need to log before we run any of our maccabipedia (pywikibot or it's import) related code
site = run_boilerplate()
from mwparserfromhell.nodes.template import Template

import pywikibot as pw

REFEREE_CATEGORY_NAME = "שופטים ראשיים (כדורגל)"
NEW_PAGE_INDICATION = "(שופט)"
FOOTBALL_NAMESPACE = "כדורגל"


def update_referee_pages() -> None:
    logging.info(f'Iterating referee pages')
    category_iterator = pagegenerators.PrefixingPageGenerator("שופט:")

    for referee_page in category_iterator:
        if NEW_PAGE_INDICATION in referee_page.title():
            logging.info(f'Skipping page: {referee_page.title()}')
            continue

        referee_name = referee_page.title().replace("שופט:", "")

        new_title = f"{FOOTBALL_NAMESPACE}:{referee_name} {NEW_PAGE_INDICATION}"
        referee_page.move(newtitle=new_title, reason="Moving referee pages to new namespace (football)",
                          noredirect=True)
        logging.info(f"Moved page to: {new_title}")

        new_template = Template("שופט כדורגל\n")
        new_template.add("שם להצגה", f'{referee_name}\n')

        new_page = pw.Page(site, new_title)
        new_page.text = str(new_template)
        new_page.save(summary="MaccabiBot - Using new referee template (football)", botflag=True)


if __name__ == '__main__':
    update_referee_pages()
