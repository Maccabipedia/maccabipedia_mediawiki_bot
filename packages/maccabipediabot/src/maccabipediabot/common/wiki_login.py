import logging
from pathlib import Path

import pywikibot as pw
from pywikibot import config

MACCABIPEDIA_FAMILY_FILE = Path(__file__).absolute().parent.parent / 'pywikibot_configs' / 'maccabipedia_family.py'


def get_site() -> pw.Site:
    logging.info('Logging in to MaccabiPedia')
    config.family_files['maccabipedia'] = str(MACCABIPEDIA_FAMILY_FILE)

    site = pw.Site()
    site.login()

    return site
