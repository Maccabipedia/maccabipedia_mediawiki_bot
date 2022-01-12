import logging
import re
from datetime import datetime
from typing import Iterable, Optional

import mwparserfromhell
import pywikibot as pw
import sys
from pywikibot import Category, pagegenerators

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))

site = pw.Site()
site.login()

maariv_papers_category = 'קטעי עיתונות מ-"מעריב"'
mark_as_paper_template_name = 'תיוג עיתונים'
publish_date_param_name = 'תאריך פרסום'

SHOULD_SAVE = True


def maariv_papers_pages() -> Iterable[pw.Page]:
    maariv_papers = Category(site, maariv_papers_category)
    return pagegenerators.CategorizedPageGenerator(maariv_papers)


def _extract_paper_page_from_title(page_title: str) -> Optional[str]:
    maybe_brackets = re.search('\([\d.]*\)', page_title)
    if not maybe_brackets:
        return None

    try:
        maybe_publish_date = maybe_brackets.group()[1:-1]
        return datetime.strptime(maybe_publish_date,"%d.%m.%Y").strftime("%d-%m-%Y")
    except Exception:
        logger.exception(f'Could not parse date from: {maybe_brackets.group()}, page title: {page_title}')

    return None


def handle_maariv_paper_page(paper_page: pw.Page) -> None:
    publish_date = _extract_paper_page_from_title(paper_page.title())
    if publish_date is None:
        return

    parsed_mw_text = mwparserfromhell.parse(paper_page.text)
    paper_template = parsed_mw_text.filter_templates(mark_as_paper_template_name)[0]

    if publish_date_param_name in paper_template:
        logger.info(f'Page: {paper_page} is already marked with publish date, skipping this paper')
        return

    paper_template.add(publish_date_param_name, publish_date)
    logger.info(f'Added publish date: {publish_date} for page: {paper_page.title()}')

    paper_page.text = parsed_mw_text
    if SHOULD_SAVE:
        paper_page.save(summary="MaccabiBotAdd publish dates for maariv papers", botflag=True)


# Assuming that the date is in the page title with this format: (31-12-1970)
if __name__ == '__main__':

    for page in maariv_papers_pages():
        logger.info(f'handling page: {page.title()}')

        handle_maariv_paper_page(page)

    logger.info(f'Finished')
