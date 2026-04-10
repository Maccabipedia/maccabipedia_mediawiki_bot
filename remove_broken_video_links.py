import sys
sys.path.insert(0, "packages/maccabipediabot/src")

import logging
import mwparserfromhell as mw
import pywikibot as pw
from maccabipediabot.common.wiki_login import get_site

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)

TEMPLATE_NAME = "קטלוג משחקים"
FIELD_MAP = {
    "משחק מלא": "משחק מלא",
    "תקציר ראשי": "תקציר וידאו",
    "תקציר משני": "תקציר וידאו2",
}

TO_REMOVE = [
    ("משחק:05-10-2023 גנט נגד מכבי תל אביב - הליגה האזורית", "תקציר ראשי"),
    ("משחק:07-03-2024 אולימפיאקוס נגד מכבי תל אביב - הליגה האזורית", "תקציר ראשי"),
    ("משחק:13-07-2017 מכבי תל אביב נגד קיי.אר. רייקיאוויק - מוקדמות הליגה האירופית", "משחק מלא"),
    ("משחק:15-09-2004 מכבי תל אביב נגד באיירן מינכן - ליגת האלופות", "תקציר ראשי"),
    ("משחק:16-09-1999 מכבי תל אביב נגד לאנס - גביע אופא", "משחק מלא"),
    ("משחק:17-08-2017 ריינדורף אלטאך נגד מכבי תל אביב - הליגה האירופית", "משחק מלא"),
    ("משחק:20-02-2014 מכבי תל אביב נגד פ.צ. באזל - הליגה האירופית", "תקציר ראשי"),
    ("משחק:21-04-2021 מ.ס. אשדוד נגד מכבי תל אביב - גביע המדינה", "משחק מלא"),
    ("משחק:21-08-2025 מכבי תל אביב נגד דינמו קייב - מוקדמות הליגה האירופית", "משחק מלא"),
    ('משחק:22-12-2018 בית"ר ירושלים נגד מכבי תל אביב - גביע המדינה', "תקציר משני"),
    ("משחק:28-08-2025 דינמו קייב נגד מכבי תל אביב - מוקדמות הליגה האירופית", "משחק מלא"),
    ("משחק:31-08-2023 צליה נגד מכבי תל אביב - הליגה האזורית", "משחק מלא"),
]

site = get_site()

for page_title, video_type in TO_REMOVE:
    field = FIELD_MAP[video_type]
    page = pw.Page(site, page_title)

    if not page.exists():
        logging.warning(f"Page not found: {page_title}")
        continue

    parsed = mw.parse(page.text)
    templates = parsed.filter_templates(matches=lambda t: t.name.strip() == TEMPLATE_NAME)
    if not templates:
        logging.warning(f"Template not found in: {page_title}")
        continue

    tmpl = templates[0]
    if not tmpl.has(field):
        logging.info(f"Field '{field}' not present in: {page_title}")
        continue

    old_value = str(tmpl.get(field).value).strip()
    if not old_value:
        logging.info(f"Field '{field}' already empty in: {page_title}")
        continue

    tmpl.get(field).value = ""
    page.text = str(parsed)
    page.save(summary="MaccabiBot - Remove broken video link", bot=True)
    logging.info(f"Cleared '{field}' in: {page_title}  (was: {old_value})")
