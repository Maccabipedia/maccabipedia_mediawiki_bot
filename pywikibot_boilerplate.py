import logging
from pathlib import Path
from typing import Dict

import pywikibot as pw
from pywikibot import config

MACCABIPEDIA_FAMILY_FILE = Path(__file__).absolute().parent / 'pywikibot_configs' / 'maccabipedia_family.py'

# We can't send the get param 'loginreturnurl' with example.com, and it's hardcoded, so have to replace it
from pywikibot.data.api import LoginManager

old_pywikibot_login = LoginManager._login_parameters


def new_pywikibot_login(*args, **kwargs) -> Dict[str, str]:
    old_params = old_pywikibot_login(*args, **kwargs)

    old_params['loginreturnurl'] = 'https://maccabipedia.co.il'

    return old_params


def run_boilerplate() -> pw.Site:
    logging.info('Running pywikibot boilerplate code')
    config.family_files['maccabipedia'] = str(MACCABIPEDIA_FAMILY_FILE)

    LoginManager._login_parameters = new_pywikibot_login

    # We need to have the url to api.php due to the fact we don't have w/api.php
    site = pw.Site()
    site.logout()
    site.login()

    return site
