"""
Find and auto-fix illegal player events on football game pages.

Pages land in the tracking category "אירועי שחקנים לא חוקיים" when their
|אירועי שחקנים= parameter contains an invalid event type or malformed row.

This module runs daily:
  1. Fetches all pages currently in the tracking category
  2. Auto-fixes the "single-colon trap" (e.g. `גול-נגיחה:67` → `גול-נגיחה::67`)
     using a structural regex that doesn't require knowing valid event types
  3. Reports fixed pages + pages still needing manual review to stdout
  4. The GH Actions workflow forwards stdout to Telegram, if non-empty
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import date
from urllib.parse import quote

import mwparserfromhell as mw
import pywikibot as pw
from pywikibot import pagegenerators

from maccabipediabot.common.maccabistats_player_event import PlayerEvent

logger = logging.getLogger(__name__)

WIKI_BASE_URL = "https://www.maccabipedia.co.il"
TRACKING_CATEGORY = "משחקים המכילים אירוע לא תקין"
FOOTBALL_TEMPLATE = "קטלוג משחקים"
EVENTS_PARAM = "אירועי שחקנים"

# Matches `<type>:<minute>` sandwiched between `::` separators.
# This is the single-colon trap — missing one colon between the event
# type and the minute field. We fix it structurally without needing
# to know which event types are valid.
SINGLE_COLON_TRAP = re.compile(r"(?<=::)([^:,\n]+):(\d+)(?=::)")

# Row separator in the |אירועי שחקנים= parameter value.
# Confirmed via sort_players_events.py which splits on "," when reading.
ROW_SEPARATOR = ","


@dataclass
class AutoFixedPage:
    """A page where the single-colon trap was fixed automatically."""
    page_name: str
    fixes_count: int = 0


@dataclass
class NeedsManualReviewPage:
    """A page in the tracking category that could not be auto-fixed.

    `malformed_rows` contains rows with wrong `::` field count. If the
    page has no malformed rows (just unknown event types that we can't
    detect structurally), `events_param_value` holds the full events
    parameter value for the human reviewer to scan.
    """
    page_name: str
    malformed_rows: list[str] = field(default_factory=list)
    events_param_value: str = ""


def _page_url(page_name: str) -> str:
    return f"{WIKI_BASE_URL}/{quote(page_name.replace(' ', '_'), safe='/:')}"


def fetch_category_pages(site: pw.Site, category: str) -> list[pw.Page]:
    """Return all pages currently in the given MediaWiki category."""
    cat = pw.Category(site, category)
    return list(pagegenerators.CategorizedPageGenerator(cat))


def fix_single_colon_trap(text: str) -> tuple[str, int]:
    """Fix `::<type>:<minute>::` → `::<type>::<minute>::`.

    Uses a purely structural regex: it matches any text fragment that
    looks like `<something>:<digits>` sandwiched between `::` separators.
    Does not need to know which event types are valid — the `::` sandwich
    is specific enough that it only fires on real event rows.

    Returns (new_text, number_of_replacements_made).
    """
    new_text, count = SINGLE_COLON_TRAP.subn(r"\1::\2", text)
    return new_text, count


def get_events_param_value(wikitext: str) -> str:
    """Return the |אירועי שחקנים= parameter value from קטלוג משחקים, or ""."""
    parsed = mw.parse(wikitext)
    templates = parsed.filter_templates(
        matches=lambda t: t.name.strip() == FOOTBALL_TEMPLATE
    )
    if not templates:
        return ""

    template = templates[0]
    if not template.has(EVENTS_PARAM):
        return ""

    return str(template.get(EVENTS_PARAM).value)


def find_malformed_rows(events_value: str) -> list[str]:
    """Return event rows that PlayerEvent.from_maccabipedia_format can't parse.

    Delegates validation to the existing parser — it raises TypeError for
    wrong field count and ValueError for non-integer minute. Both conditions
    mean the row is malformed.

    Rows are separated by `,` (same as sort_players_events.py).
    """
    malformed: list[str] = []
    for raw_row in events_value.split(ROW_SEPARATOR):
        row = raw_row.strip()
        if not row:
            continue
        try:
            PlayerEvent.from_maccabipedia_format(row)
        except (TypeError, ValueError):
            malformed.append(row)

    return malformed


def format_report(
    fixed: list[AutoFixedPage],
    needs_review: list[NeedsManualReviewPage],
    report_date: date,
) -> str:
    """Build the Telegram HTML report.

    Returns empty string if both lists are empty — the workflow uses
    this as the gate for "don't send a Telegram message at all".

    RTL handling mirrors the broken videos report: \u200f at line start,
    \u200b at line end. Documented in memory: feedback_telegram_html_rtl.md.
    """
    if not fixed and not needs_review:
        return ""

    lines: list[str] = []

    if fixed:
        lines.append(f"תוקנו אוטומטית {len(fixed)} עמודים — {report_date}")
        for page in fixed:
            page_url = _page_url(page.page_name)
            lines.append(
                f'\u200f<a href="{page_url}">{page.page_name}</a> '
                f'({page.fixes_count} תיקונים)\u200b'
            )

    if needs_review:
        if fixed:
            lines.append("")
        lines.append(f"⚠️ דורש בדיקה ידנית — {len(needs_review)} עמודים")
        for page in needs_review:
            page_url = _page_url(page.page_name)
            lines.append(f'\u200f<a href="{page_url}">{page.page_name}</a>\u200b')
            if page.malformed_rows:
                for row in page.malformed_rows:
                    lines.append(f"  {row}")
            elif page.events_param_value:
                # No malformed shape found — surface full events value
                # so the human can scan for unknown event types.
                lines.append(f"  {page.events_param_value}")

    return "\n".join(lines)


def process_page(
    page: pw.Page,
    *,
    page_name: str,
) -> AutoFixedPage | NeedsManualReviewPage:
    """Auto-fix the single-colon trap on a page and classify the outcome.

    Returns:
      - AutoFixedPage if the auto-fix was applied and the page was saved
      - NeedsManualReviewPage otherwise (with malformed rows if any, or
        the full events param value as a fallback so a human can scan)

    Precedence: auto-fix wins. If a page has BOTH single-colon traps AND
    unknown event types, we fix the colons this run; the unknown types
    keep the page in the tracking category and surface on the next run.
    """
    original_text = page.text
    fixed_text, fix_count = fix_single_colon_trap(original_text)

    if fix_count > 0:
        page.text = fixed_text
        page.save(
            summary="MaccabiBot - תיקון פסיק בודד באירועי שחקנים",
            bot=True,
        )
        return AutoFixedPage(page_name=page_name, fixes_count=fix_count)

    events_value = get_events_param_value(original_text)
    malformed = find_malformed_rows(events_value)
    return NeedsManualReviewPage(
        page_name=page_name,
        malformed_rows=malformed,
        events_param_value=events_value,
    )


def main() -> None:
    """Entry point used by the `find_illegal_events.yaml` workflow.

    1. Fetch all pages in the tracking category
    2. Process each: auto-fix if possible, else collect for manual review
    3. Print the report to stdout (captured by the workflow, sent to Telegram
       only if non-empty)
    """
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(message)s",
        level=logging.INFO,
    )

    from maccabipediabot.common.wiki_login import get_site
    pw.config.verbose_output = False
    site = get_site()

    pages = fetch_category_pages(site, TRACKING_CATEGORY)
    logger.info("Found %d pages in tracking category", len(pages))

    if not pages:
        return

    fixed: list[AutoFixedPage] = []
    needs_review: list[NeedsManualReviewPage] = []

    for page in pages:
        result = process_page(page, page_name=page.title())
        if isinstance(result, AutoFixedPage):
            fixed.append(result)
        else:
            needs_review.append(result)

    report = format_report(fixed, needs_review, date.today())
    if report:
        print(report)


if __name__ == "__main__":
    main()
