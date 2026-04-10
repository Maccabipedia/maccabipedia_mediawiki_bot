"""
Apply missing Latin names to football player profile pages.

Reads docs/profiles_missing_latin_name.csv (with ProposedLatinName filled in)
and sets the ``שם בלועזית`` parameter on each wiki profile page via mwparserfromhell.

How to run
----------
    uv run python -m maccabipediabot.maintenance.football.fix_profiles_latin_names

Set SHOULD_SAVE = True to actually save pages (default is dry-run).
"""
import csv
import logging
import sys

import mwparserfromhell
import pywikibot as pw

from maccabipediabot.common.wiki_login import get_site

logging.basicConfig(format="%(asctime)s : %(levelname)s : %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

SHOULD_SAVE = False
INPUT_CSV = "docs/profiles_missing_latin_name.csv"
PROFILE_TEMPLATE_NAME = "פרופיל כדורגל"


def update_latin_name(site: pw.Site, page_name: str, latin_name: str) -> None:
    page = pw.Page(site, page_name)
    if not page.exists():
        logger.warning("Page not found: %s", page_name)
        return

    wikicode = mwparserfromhell.parse(page.text)
    templates = wikicode.filter_templates(matches=PROFILE_TEMPLATE_NAME)
    if not templates:
        logger.warning("No {{%s}} template in: %s", PROFILE_TEMPLATE_NAME, page_name)
        return

    template = templates[0]
    if template.has("שם בלועזית"):
        template.get("שם בלועזית").value = f"{latin_name}"
    else:
        template.add("שם בלועזית", f"{latin_name}")

    page.text = str(wikicode)

    if SHOULD_SAVE:
        page.save(summary=f"MaccabiBot - Add missing Latin name: {latin_name}")
        logger.info("Updated %s: שם בלועזית = %s", page_name, latin_name)
    else:
        logger.info("[DRY RUN] would update %s: שם בלועזית = %s", page_name, latin_name)


def main() -> None:
    site = get_site()
    updated = 0
    with open(INPUT_CSV, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            latin_name = row.get("ProposedLatinName", "").strip()
            if not latin_name:
                continue
            update_latin_name(site, row["pageName"], latin_name)
            updated += 1

    logger.info(
        "Done. processed=%d (SHOULD_SAVE=%s)", updated, SHOULD_SAVE
    )
    if not SHOULD_SAVE:
        logger.info("Re-run with SHOULD_SAVE = True to actually save the pages.")


if __name__ == "__main__":
    sys.exit(main())
