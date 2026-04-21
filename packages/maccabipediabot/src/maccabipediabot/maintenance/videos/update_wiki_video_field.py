"""Set a video-link field (משחק מלא / תקציר וידאו / תקציר וידאו2) on a football game page."""
import argparse
import logging

import mwparserfromhell as mw
import pywikibot as pw

from maccabipediabot.common.logging_setup import setup_logging
from maccabipediabot.common.wiki_login import get_site

logger = logging.getLogger(__name__)

TEMPLATE_NAME = "קטלוג משחקים"
ALLOWED_FIELDS = {"משחק מלא", "תקציר וידאו", "תקציר וידאו2"}


def default_summary(video_url: str) -> str:
    return f"MaccabiBot - Restore video link from backup upload ({video_url})"


def set_video_field(site: pw.Site, page_title: str, field: str, url: str, summary: str | None = None) -> None:
    if field not in ALLOWED_FIELDS:
        raise ValueError(f"field must be one of {sorted(ALLOWED_FIELDS)}, got {field!r}")

    page = pw.Page(site, page_title)
    if not page.exists():
        raise LookupError(f"Page not found: {page_title}")

    parsed = mw.parse(page.text)
    templates = parsed.filter_templates(matches=lambda t: t.name.strip() == TEMPLATE_NAME)
    if not templates:
        raise LookupError(f"Template '{TEMPLATE_NAME}' not found on {page_title}")
    tmpl = templates[0]

    existing = str(tmpl.get(field).value).strip() if tmpl.has(field) else ""
    if existing:
        raise ValueError(f"Field '{field}' already has a value on {page_title}: {existing}")

    if tmpl.has(field):
        tmpl.get(field).value = f"{url}\n"
    else:
        tmpl.add(field, f"{url}\n")

    page.text = str(parsed)
    page.save(summary=summary or default_summary(url), bot=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--page", required=True, help="Full page title incl. namespace (e.g. 'משחק:16-02-2009 ...')")
    parser.add_argument("--field", required=True, choices=sorted(ALLOWED_FIELDS))
    parser.add_argument("--url", required=True, help="YouTube URL to set")
    parser.add_argument("--summary", default=None, help="Edit summary (default: auto-generated from URL)")
    args = parser.parse_args()

    setup_logging(level=logging.INFO)
    pw.config.verbose_output = False
    site = get_site()
    set_video_field(site, args.page, args.field, args.url, args.summary)
    logger.info("Updated %s on %s", args.field, args.page)


if __name__ == "__main__":
    main()
