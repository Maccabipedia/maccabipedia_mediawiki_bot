import logging

import mwparserfromhell
import requests

from pywikibot_boilerplate import run_boilerplate

_LATEST_LEAGUE_TABLE_STATUS_URL = 'https://rona.sh/api/maccabipedia'
_LEAGUE_TABLE_TEMPLATE_ON_MACCABIPEDIA = 'תבנית:טבלת ליגה 2022/23'
_TABLE_STATUS_KEY = 'נתוני טבלה'

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)

# We need to log before we run any of our maccabipedia (pywikibot or it's import) related code
site = run_boilerplate()

import pywikibot as pw


def update_league_table_status() -> None:
    logging.info(f'Fetching current league table from: {_LATEST_LEAGUE_TABLE_STATUS_URL}')
    league_table_status = requests.get(_LATEST_LEAGUE_TABLE_STATUS_URL)

    league_table_template_page = pw.Page(site, _LEAGUE_TABLE_TEMPLATE_ON_MACCABIPEDIA)

    parsed_mw_text = mwparserfromhell.parse(league_table_template_page.text)
    table_template = parsed_mw_text.filter_templates(_LEAGUE_TABLE_TEMPLATE_ON_MACCABIPEDIA)[0]
    table_template.add(_TABLE_STATUS_KEY, league_table_status.text)

    league_table_template_page.text = parsed_mw_text

    league_table_template_page.save(summary="MaccabiBot - Update league table")


if __name__ == '__main__':
    update_league_table_status()
