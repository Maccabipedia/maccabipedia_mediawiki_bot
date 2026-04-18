"""
Add pill-style navigation bars to player achievement category pages.

Auto-discovers all category series matching the pattern:
  "שחקני {sport} שזכו ב-{N} {type}"  (e.g. שחקני כדורגל שזכו ב-3 אליפויות)
  "שחקני {sport} שזכו {N} {type}"    (e.g. שחקני כדורגל שזכו 5 עונות במכבי)

For each discovered series this script:
  1. Creates (or updates) one navigation template per competition type,
     e.g. "תבנית:ניווט שחקני כדורגל - אליפויות".
  2. Edits each category page to prepend the template call so the nav bar
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

from maccabipediabot.common.logging_setup import setup_logging
from maccabipediabot.common.wiki_login import get_site

setup_logging(level=logging.INFO)
logger = logging.getLogger(__name__)

# CSS classes defined in MediaWiki:Common.css
_PILL_CLASS = "nmpAchievementsNavPill"
_PILL_ACTIVE_CLASS = "nmpAchievementsNavPillActive"

# Human-readable labels for known competition types.
# Fallback: "{type_name}:"
TYPE_LABELS = {
    "אליפויות":             "זכיות באליפות:",
    "אלוף האלופים":         "זכיות באלוף האלופים:",
    "אלוף האליפיים":        "זכיות באלוף האלופים:",
    "גביעי מדינה":          "זכיות בגביע המדינה:",
    "גביעי טוטו":           "זכיות בגביע הטוטו:",
    "גביעי ליליאן":         "זכיות בגביע ליליאן:",
    "גביעי אסיה לאלופות":   "זכיות בגביע אסיה לאלופות:",
    "גביעי אטקין":          "זכיות בגביע אטקין:",
    "תארים":                "סך כל התארים:",
    "תאריים":               "סך כל התארים:",
    "עונות במכבי":          "עונות במכבי:",
    "עונות":                "עונות במכבי:",
}

# Patterns to match category names (order matters — most specific first):
#   Pattern A:  "שחקני {sport} שזכו ב-{N} {type}"  e.g. שחקני כדורגל שזכו ב-3 אליפויות
#   Pattern B:  "שחקני {sport} שזכו {N} {type}"    e.g. שחקני כדורגל שזכו 5 תארים
#   Pattern C:  "שחקני {sport} ששיחקו {N} {type}"  e.g. שחקני כדורגל ששיחקו 7 עונות במכבי
#   Pattern D:  "שחקנים ששיחקו {N} {type}"          e.g. שחקנים ששיחקו 10 עונות
_PATTERN_A = re.compile(r"^שחקני (.+?) שזכו ב-(\d+) (.+)$")
_PATTERN_B = re.compile(r"^שחקני (.+?) שזכו (\d+) (.+)$")
_PATTERN_C = re.compile(r"^שחקני (.+?) ששיחקו (\d+) (.+)$")
_PATTERN_D = re.compile(r"^שחקנים ששיחקו (\d+) (.+)$")


@dataclass
class CategorySeries:
    sport: str        # e.g. "כדורגל"
    type_name: str    # e.g. "אליפויות"
    cat_prefix: str   # e.g. "שחקני כדורגל שזכו ב-" or "שחקני כדורגל שזכו "
    numbers: list[int]

    @property
    def template_name(self) -> str:
        return f"ניווט שחקני {self.sport} - {self.type_name}"

    def cat_title(self, n: int) -> str:
        # cat_prefix already ends with the right separator (e.g. "ב-" or " ")
        return f"קטגוריה:{self.cat_prefix}{n} {self.type_name}"

    def template_call(self, n: int) -> str:
        return f"{{{{{self.template_name}|{n}}}}}"


def discover_all_series(
    site: pywikibot.Site, sport_filter: str | None = None
) -> list[CategorySeries]:
    """
    Query all categories starting with 'שחקני' and parse them into series.
    Handles both 'שזכו ב-N' and 'שזכו N' patterns automatically.
    """
    logger.info("Querying all 'שחקני' categories from wiki...")
    grouped: dict[tuple, dict] = defaultdict(lambda: {"cat_prefix": None, "numbers": []})

    # "שחקני" covers both "שחקני {sport}" and "שחקנים" (since שחקנים starts with שחקני)
    for cat in site.allcategories(prefix="שחקני"):
            title = cat.title(with_ns=False)

            ma = _PATTERN_A.match(title)
            mb = _PATTERN_B.match(title)
            mc = _PATTERN_C.match(title)
            md = _PATTERN_D.match(title)

            if ma:
                sport, n, type_name = ma.group(1), int(ma.group(2)), ma.group(3)
                cat_prefix = f"שחקני {sport} שזכו ב-"
            elif mb:
                sport, n, type_name = mb.group(1), int(mb.group(2)), mb.group(3)
                cat_prefix = f"שחקני {sport} שזכו "
            elif mc:
                sport, n, type_name = mc.group(1), int(mc.group(2)), mc.group(3)
                cat_prefix = f"שחקני {sport} ששיחקו "
            elif md:
                sport, n, type_name = "כללי", int(md.group(1)), md.group(2)
                cat_prefix = "שחקנים ששיחקו "
            else:
                continue

            if sport_filter and sport != sport_filter:
                continue

            key = (sport, type_name)
            grouped[key]["cat_prefix"] = cat_prefix
            grouped[key]["numbers"].append(n)

    series = [
        CategorySeries(
            sport=key[0],
            type_name=key[1],
            cat_prefix=data["cat_prefix"],
            numbers=sorted(data["numbers"]),
        )
        for key, data in grouped.items()
    ]

    logger.info(f"Discovered {len(series)} category series")
    return series


def build_template_wikitext(series: CategorySeries, label: str) -> str:
    """Build the full wikitext for a pill-navigation template."""
    pills = []
    for n in series.numbers:
        cat_full = series.cat_title(n)
        current_html = f'<span class="{_PILL_ACTIVE_CLASS}">{n}</span>'
        linked_html = f'[[:{cat_full}|<span class="{_PILL_CLASS}">{n}</span>]]'
        pill = "{{#ifeq:{{{1}}}|" + str(n) + "|" + current_html + "|" + linked_html + "}}"
        pills.append(pill)

    return (
        "<includeonly>\n"
        '<div style="text-align:center;padding:8px 12px;background:#f8f9fa;'
        'border:1px solid #a2a9b1;border-radius:4px;margin:4px 0 10px 0;">\n'
        f'<div style="font-size:12px;color:#72777d;margin-bottom:6px;">{label}</div>\n'
        "<div>\n"
        + "\n".join(pills) + "\n"
        "</div>\n"
        "</div>\n"
        "</includeonly>\n"
        "<noinclude>[[קטגוריה:תבניות ניווט]]</noinclude>"
    )


def create_or_update_template(
    site: pywikibot.Site, series: CategorySeries, label: str, dry_run: bool
) -> None:
    template_title = f"תבנית:{series.template_name}"
    page = pywikibot.Page(site, template_title)
    new_content = build_template_wikitext(series, label)

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
    site: pywikibot.Site, series: CategorySeries, n: int, dry_run: bool
) -> None:
    template_call = series.template_call(n)
    cat_title = series.cat_title(n)
    page = pywikibot.Page(site, cat_title)
    existing = page.text

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


def main(dry_run: bool = True, test: bool = False, sport_filter: str | None = None) -> None:
    site = get_site()
    all_series = discover_all_series(site, sport_filter=sport_filter)

    unknown_types: list[str] = []

    for series in sorted(all_series, key=lambda s: (s.sport, s.type_name)):
        if series.type_name not in TYPE_LABELS:
            unknown_types.append(f"  [{series.sport}] {series.type_name!r} — e.g. {series.cat_title(series.numbers[0])}")
            logger.warning(f"Unknown type_name {series.type_name!r} for sport {series.sport!r} — skipping (add to TYPE_LABELS)")
            continue

        label = TYPE_LABELS[series.type_name]
        logger.info(f"\n--- [{series.sport}] {series.type_name} ({series.numbers}) ---")

        create_or_update_template(site, series, label, dry_run)

        for n in series.numbers:
            add_navbar_to_category_page(site, series, n, dry_run)
            if test:
                logger.info("Test mode: stopping after first page.")
                return

    if unknown_types:
        raise ValueError(
            "New competition type(s) found — add them to TYPE_LABELS with a human-readable label:\n"
            + "\n".join(unknown_types)
        )

    logger.info("\nDone.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Actually edit the wiki (default: dry-run)")
    parser.add_argument("--test", action="store_true", help="Only process one template and one category page")
    parser.add_argument("--sport", help="Only process this sport (e.g. כדורגל, כדורעף)")
    args = parser.parse_args()
    main(dry_run=not args.live, test=args.test, sport_filter=args.sport)
