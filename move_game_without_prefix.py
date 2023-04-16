import logging

import mwparserfromhell
import requests
from pywikibot import pagegenerators, Category

from pywikibot_boilerplate import run_boilerplate

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)

# We need to log before we run any of our maccabipedia (pywikibot or it's import) related code
site = run_boilerplate()

import pywikibot as pw

FOOTBALL_GAMES_CATEGORY_NAME = "קטגוריה:משחקים"
OLD_PREFIX = 'משחק: '


def update_games_prefixes() -> None:
    logging.info(f'Iterating game pages')
    category_iterator = pagegenerators.CategorizedPageGenerator(Category(site, FOOTBALL_GAMES_CATEGORY_NAME),
                                                                recurse=True)

    for game_page in category_iterator:
        if not game_page.title().startswith(OLD_PREFIX):
            logging.info(f'Skipping page: {game_page.title()}')
            continue

        new_title = game_page.title().replace(OLD_PREFIX, "משחק:")
        game_page.move(newtitle=new_title, reason="MaccabiBot Fix Whatsapp page name bug")
        
        game_page.purge(forcelinkupdate=True, forcerecursivelinkupdate=True)
        game_page.touch(botflag=True)

        logging.info(f"Moved page to: {new_title}")


if __name__ == '__main__':
    update_games_prefixes()
