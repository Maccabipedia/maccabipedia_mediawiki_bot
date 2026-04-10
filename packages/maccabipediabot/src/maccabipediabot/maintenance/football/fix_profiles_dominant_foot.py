"""
Apply missing dominant foot to football player profile pages.

Reads docs/profiles_missing_dominant_foot.csv (with ProposedFoot filled in)
and sets the ``רגל`` parameter on each wiki profile page via mwparserfromhell.

How to run
----------
    uv run python -m maccabipediabot.maintenance.football.fix_profiles_dominant_foot

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
INPUT_CSV = "docs/profiles_missing_dominant_foot.csv"
PROFILE_TEMPLATE_NAME = "פרופיל כדורגל"
VALID_FEET = {"ימין", "שמאל", "שתיים"}


def update_dominant_foot(site: pw.Site, page_name: str, foot: str) -> None:
    if foot not in VALID_FEET:
        logger.error(
            "Invalid foot value '%s' for %s — skipping (use ימין/שמאל/שתיים)", foot, page_name
        )
        return

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
    if template.has("רגל"):
        template.get("רגל").value = f"{foot}"
    else:
        template.add("רגל", f"{foot}")

    page.text = str(wikicode)

    if SHOULD_SAVE:
        page.save(summary=f"MaccabiBot - Add missing dominant foot: {foot}")
        logger.info("Updated %s: רגל = %s", page_name, foot)
    else:
        logger.info("[DRY RUN] would update %s: רגל = %s", page_name, foot)


def main() -> None:
    site = get_site()
    updated = 0
    with open(INPUT_CSV, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            foot = row.get("ProposedFoot", "").strip()
            if not foot:
                continue
            update_dominant_foot(site, row["pageName"], foot)
            updated += 1

    logger.info(
        "Done. processed=%d (SHOULD_SAVE=%s)", updated, SHOULD_SAVE
    )
    if not SHOULD_SAVE:
        logger.info("Re-run with SHOULD_SAVE = True to actually save the pages.")


if __name__ == "__main__":
    sys.exit(main())
