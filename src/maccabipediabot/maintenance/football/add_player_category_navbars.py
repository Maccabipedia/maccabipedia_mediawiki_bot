"""
Add pill-style navigation bars to player achievement category pages.

For each sport and competition-type series (e.g. "שחקני כדורגל שזכו ב-N אליפויות"),
this script:
  1. Discovers all existing numbered categories via the MediaWiki API.
  2. Creates (or updates) one navigation template per competition type,
     e.g. "תבנית:ניווט שחקני כדורגל - אליפויות".
  3. Edits each category page to prepend the template call so the nav bar
     appears above the member list.

Usage:
    # Dry-run (prints what would change, makes no edits):
    python -m maccabipediabot.maintenance.football.add_player_category_navbars

    # Live run:
    python -m maccabipediabot.maintenance.football.add_player_category_navbars --live

    # Single sport:
    python -m maccabipediabot.maintenance.football.add_player_category_navbars --live --sport כדורגל

Dependencies: pywikibot (configured for maccabipedia)
"""

import argparse
import logging
import re
from collections import defaultdict
from dataclasses import dataclass

import pywikibot

from maccabipediabot.common.wiki_login import get_site

logging.basicConfig(format="%(asctime)s : %(levelname)s : %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# CSS classes defined in MediaWiki:Common.css
_PILL_CLASS = "nmpAchievementsNavPill"
_PILL_ACTIVE_CLASS = "nmpAchievementsNavPillActive"


@dataclass
class SportConfig:
    name: str           # e.g. "כדורגל"
    category_prefix: str  # prefix for allcategories query
    template_prefix: str  # prefix for template titles
    type_labels: dict[str, str]  # type_name -> label shown above pills


SPORTS = [
    SportConfig(
        name="כדורגל",
        category_prefix="שחקני כדורגל שזכו ב-",
        template_prefix="ניווט שחקני כדורגל - ",
        type_labels={
            "אליפויות":             "זכיות באליפות:",
            "אלוף האלופים":         "זכיות באלוף האלופים:",
            "אלוף האליפיים":        "זכיות באלוף האלופים:",
            "גביעי מדינה":          "זכיות בגביע המדינה:",
            "גביעי טוטו":           "זכיות בגביע הטוטו:",
            "גביעי ליליאן":         "זכיות בגביע ליליאן:",
            "גביעי אסיה לאלופות":   "זכיות בגביע אסיה לאלופות:",
            "תאריים":               "סך כל התארים:",
        },
    ),
    SportConfig(
        name="כדורעף",
        category_prefix="שחקני כדורעף שזכו ב-",
        template_prefix="ניווט שחקני כדורעף - ",
        type_labels={
            "אליפויות":     "זכיות באליפות:",
            "גביעי אטקין":  "זכיות בגביע אטקין:",
            "גביעי מדינה":  "זכיות בגביע המדינה:",
            "תאריים":       "סך כל התארים:",
            "תארים":        "סך כל התארים:",
        },
    ),
]


def discover_categories(site: pywikibot.Site, sport: SportConfig) -> dict[str, list[int]]:
    """
    Query the wiki for all categories matching this sport's prefix.
    Returns a dict mapping type_name -> sorted list of numbers.
    """
    logger.info(f"[{sport.name}] Querying categories with prefix: {sport.category_prefix!r}")
    raw_cats = [
        cat.title(with_ns=False)
        for cat in site.allcategories(prefix=sport.category_prefix)
    ]
    logger.info(f"[{sport.name}] Found {len(raw_cats)} matching categories")

    pattern = re.compile(r"^.+שזכו ב-(\d+) (.+)$")
    grouped: dict[str, list[int]] = defaultdict(list)
    for cat in raw_cats:
        m = pattern.match(cat)
        if m:
            n, type_name = int(m.group(1)), m.group(2)
            grouped[type_name].append(n)
        else:
            logger.warning(f"Unexpected category name, skipping: {cat!r}")

    return {t: sorted(ns) for t, ns in grouped.items()}


def build_template_wikitext(
    sport: SportConfig, type_name: str, label: str, numbers: list[int]
) -> str:
    """Build the full wikitext for a pill-navigation template."""
    pills = []
    for n in numbers:
        cat_full = f"קטגוריה:{sport.category_prefix}{n} {type_name}"
        current_html = f'<span class="{_PILL_ACTIVE_CLASS}">{n}</span>'
        linked_html = f'[[:{ cat_full }|<span class="{_PILL_CLASS}">{n}</span>]]'
        pill = "{{#ifeq:{{{1}}}|" + str(n) + "|" + current_html + "|" + linked_html + "}}"
        pills.append(pill)

    pills_wikitext = "\n".join(pills)

    return (
        "<includeonly>\n"
        '<div style="text-align:center;padding:8px 12px;background:#f8f9fa;'
        'border:1px solid #a2a9b1;border-radius:4px;margin:4px 0 10px 0;">\n'
        f'<div style="font-size:12px;color:#72777d;margin-bottom:6px;">{label}</div>\n'
        "<div>\n"
        f"{pills_wikitext}\n"
        "</div>\n"
        "</div>\n"
        "</includeonly>\n"
        "<noinclude>[[קטגוריה:תבניות ניווט]]</noinclude>"
    )


def create_or_update_template(
    site: pywikibot.Site,
    sport: SportConfig,
    type_name: str,
    label: str,
    numbers: list[int],
    dry_run: bool,
) -> None:
    template_title = f"תבנית:{sport.template_prefix}{type_name}"
    page = pywikibot.Page(site, template_title)
    new_content = build_template_wikitext(sport, type_name, label, numbers)

    if page.exists() and page.text == new_content:
        logger.info(f"Template already up-to-date: {template_title}")
        return

    action = "CREATE" if not page.exists() else "UPDATE"
    logger.info(f"[{action}] Template: {template_title}")
    if dry_run:
        logger.info(f"  [DRY-RUN] Would set content:\n{new_content}\n")
        return

    page.text = new_content
    page.save(summary="בוט: הוספת תבנית ניווט לקטגוריות שחקנים לפי הישגים", minor=False)


def add_navbar_to_category_page(
    site: pywikibot.Site,
    sport: SportConfig,
    type_name: str,
    n: int,
    dry_run: bool,
) -> None:
    template_call = f"{{{{{sport.template_prefix}{type_name}|{n}}}}}"
    cat_title = f"קטגוריה:{sport.category_prefix}{n} {type_name}"
    page = pywikibot.Page(site, cat_title)

    existing = page.text  # '' for category pages with no explicit wikitext

    if template_call in existing:
        logger.info(f"Nav already present: {cat_title}")
        return

    new_content = template_call + ("\n" + existing if existing.strip() else "")

    logger.info(f"[EDIT] Category page: {cat_title}")
    if dry_run:
        logger.info(f"  [DRY-RUN] Would set content:\n{new_content}\n")
        return

    page.text = new_content
    page.save(summary="בוט: הוספת ניווט לקטגוריה", minor=True)


def process_sport(
    site: pywikibot.Site, sport: SportConfig, dry_run: bool, test: bool
) -> None:
    type_map = discover_categories(site, sport)
    logger.info(f"[{sport.name}] Types found: {list(type_map.keys())}")

    for type_name, numbers in sorted(type_map.items()):
        label = sport.type_labels.get(type_name, f"זכיות ב{type_name}:")
        logger.info(f"\n--- [{sport.name}] {type_name} ({numbers}) ---")

        create_or_update_template(site, sport, type_name, label, numbers, dry_run)

        for n in numbers:
            add_navbar_to_category_page(site, sport, type_name, n, dry_run)
            if test:
                logger.info("Test mode: stopping after first page.")
                return


def main(dry_run: bool = True, test: bool = False, sport_filter: str | None = None) -> None:
    site = get_site()

    sports = [s for s in SPORTS if sport_filter is None or s.name == sport_filter]
    if not sports:
        logger.error(f"Unknown sport: {sport_filter!r}. Available: {[s.name for s in SPORTS]}")
        return

    for sport in sports:
        process_sport(site, sport, dry_run, test)

    logger.info("\nDone.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Actually edit the wiki (default: dry-run)")
    parser.add_argument("--test", action="store_true", help="Only process one template and one category page")
    parser.add_argument("--sport", help="Only process this sport (e.g. כדורגל, כדורעף)")
    args = parser.parse_args()
    main(dry_run=not args.live, test=args.test, sport_filter=args.sport)
