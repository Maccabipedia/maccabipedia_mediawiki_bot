import logging
from pathlib import Path
from typing import Dict

import pywikibot as pw
from pywikibot import config
from pywikibot.data.api import LoginManager

MACCABIPEDIA_FAMILY_FILE = Path(__file__).absolute().parent / 'pywikibot_configs' / 'maccabipedia_family.py'

old_pywikibot_login = LoginManager._login_parameters


def new_pywikibot_login(*args, **kwargs) -> Dict[str, str]:
    old_params = old_pywikibot_login(*args, **kwargs)

    old_params['loginreturnurl'] = 'https://maccabipedia.co.il'

    return old_params


def run_boilerplate() -> pw.Site:
    logging.info('Running pywikibot boilerplate code')
    config.family_files['maccabipedia'] = str(MACCABIPEDIA_FAMILY_FILE)

    LoginManager._login_parameters = new_pywikibot_login

    site = pw.Site()
    site.login()

    return site
