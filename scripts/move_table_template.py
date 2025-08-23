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


def update_table_template() -> None:
    logging.info(f'Iterating referee pages')
    template = pw.Page(site, "תבנית:טבלת ליגה")
    for page in template.getReferences():
        if page.namespace().custom_name != 'תבנית':
            logging.info(f'Skipping non template page: {page.title()}')
            continue

        if 'ליגה' not in page.title():
            logging.info(f'Skipping fixed template page: {page.title()}')
            continue

        new_page_name = page.title().replace("ליגה", "ליגת כדורגל")

        page.move(newtitle=new_page_name, reason="Fixing football table pages name",
                          noredirect=True)
        logging.info(f"Moved page to: {new_page_name}")

if __name__ == '__main__':
    update_table_template()
