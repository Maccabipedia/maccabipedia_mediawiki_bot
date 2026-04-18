import logging

import mwparserfromhell
import requests
from pywikibot import pagegenerators, Category

from maccabipediabot.common.logging_setup import setup_logging
from maccabipediabot.common.wiki_login import get_site

setup_logging(level=logging.DEBUG)

# We need to log before we run any of our maccabipedia (pywikibot or it's import) related code
site = get_site()

import pywikibot as pw

FOOTBALL_GAMES_CATEGORY_NAME = "קטגוריה:משחקים"
OLD_PREFIX = 'משחק: '


def update_games_prefixes() -> None:
    logging.info(f'Iterating game pages')
    category_iterator = pagegenerators.CategorizedPageGenerator(Category(site, FOOTBALL_GAMES_CATEGORY_NAME),
                                                                recurse=True)
    old = 0
    new = 0

    for game_page in category_iterator:
        if not game_page.title().startswith(OLD_PREFIX):
            logging.info(f'Skipping page: {game_page.title()}')
            new += 1
            continue

        old += 1

    logging.info(f"old: {old}, new: {new}")


if __name__ == '__main__':
    update_games_prefixes()
