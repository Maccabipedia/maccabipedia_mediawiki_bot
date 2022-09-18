import logging
from pathlib import Path

import pywikibot as pw
from pywikibot import config

MACCABIPEDIA_FAMILY_FILE = Path(__file__).absolute().parent / 'pywikibot_configs' / 'maccabipedia_family.py'


def run_boilerplate() -> pw.Site:
    logging.info('Running pywikibot boilerplate code')
    config.family_files['maccabipedia'] = str(MACCABIPEDIA_FAMILY_FILE)

    # We need to have the url to api.php due to the fact we don't have w/api.php
    site = pw.Site()
    site.login()

    return site
