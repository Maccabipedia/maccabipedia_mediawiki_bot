import logging

import pywikibot as pw

from maccabipediabot.common.wiki_login import get_site

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

MAIN_PAGE_TITLE = "עמוד ראשי"


def purge_main_page() -> None:
    site = get_site()
    page = pw.Page(site, MAIN_PAGE_TITLE)
    logging.info(f'Purging page: {page.title()}')
    success = page.purge()
    if not success:
        raise RuntimeError(f'Failed to purge {page.title()}')
    logging.info('Purge successful')


if __name__ == '__main__':
    purge_main_page()
