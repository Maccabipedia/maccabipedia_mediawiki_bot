"""
Basketball Referees Bot
=======================
Creates a Maccabipedia page for each basketball referee who appears in the
Basketball_Games Cargo table (fields: MainReferee, AssistantReferees).

Page title format : כדורסל:NAME (שופט)
Template used     : {{שופט כדורסל |שם להצגה=NAME}}

How to run
----------
    source ~/.secrets && MACCABIPEDIA_UA_SCRIPT=gamesbot_basketball python basketball/refereesbot_basketball.py

Dependencies
------------
    pywikibot, requests  (see requirements.txt)
    pywikibot_boilerplate must be importable (run from repo root or add it to PYTHONPATH)
"""

import logging
import sys

import requests

from maccabipediabot.pywikibot_boilerplate import run_boilerplate

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

CARGO_EXPORT_URL = (
    'https://www.maccabipedia.co.il/index.php'
    '?title=Special:CargoExport'
    '&tables=Basketball_Games'
    '&fields=MainReferee,AssistantReferees'
    '&format=json'
    '&limit=5000'
)

BASKETBALL_REFEREE_TEMPLATE = '{{{{שופט כדורסל |שם להצגה={name}}}}}'

SHOULD_SAVE = True


def fetch_all_referee_names():
    """Query Cargo and return a sorted list of unique non-empty referee names."""
    resp = requests.get(CARGO_EXPORT_URL)

    if resp.status_code != 200 or 'application/json' not in resp.headers.get('Content-Type', ''):
        raise RuntimeError(
            f'Unexpected Cargo response: status={resp.status_code}\n{resp.text[:500]}'
        )

    rows = resp.json()
    names = set()

    for row in rows:
        main = row.get('MainReferee') or ''
        if main.strip():
            names.add(main.strip())

        assistants = row.get('AssistantReferees') or []
        if isinstance(assistants, str):
            assistants = [assistants]
        for name in assistants:
            if name and name.strip():
                names.add(name.strip())

    return sorted(names)


def page_title(referee_name):
    return f'כדורסל:{referee_name} (שופט)'


def create_referee_page(site, referee_name):
    import pywikibot as pw

    title = page_title(referee_name)
    page = pw.Page(site, title)

    if page.exists():
        logger.info('EXISTS   %s', title)
        return

    page.text = BASKETBALL_REFEREE_TEMPLATE.format(name=referee_name)
    logger.info('CREATING %s', title)

    if SHOULD_SAVE:
        page.save(summary='MaccabiBot - Add basketball referee page')
    else:
        logger.info('DRY RUN  — page text would be:\n%s', page.text)


def main():
    site = run_boilerplate()

    logger.info('Fetching referee names from Cargo...')
    referee_names = fetch_all_referee_names()
    logger.info('Found %d unique referee names', len(referee_names))

    for name in referee_names:
        create_referee_page(site, name)

    logger.info('Done.')


if __name__ == '__main__':
    main()
