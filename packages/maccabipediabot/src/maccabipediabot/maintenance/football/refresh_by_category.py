"""Reparse profile pages so their live-computed title/season categories refresh.

A player's "won N titles" / "played N seasons" categories are computed inside the
profile template from Cargo data (the player's Maccabi seasons intersected with
Maccabi's title-winning seasons). MediaWiki does NOT re-parse those pages when the
underlying Cargo data changes, so after a new title or season is recorded the counts
stay frozen at the old value. New milestone categories — e.g.
`שחקני כדורגל שזכו ב-18 תארים` — therefore never gain members: they stay red-linked
and invisible in the DPL navigation strips.

This job bulk-purges every member of the profiles category with
`forcelinkupdate=true`, forcing each page's categorylinks to refresh against the
current Cargo data. Run `sync_navigation_categories` afterwards to create the
freshly-populated milestone category pages and install their navigation templates
(the scheduled workflow chains both).

Idempotent — safe to re-run.

Usage:
    # Dry-run (default; counts members, purges nothing):
    uv run python -m maccabipediabot.maintenance.football.refresh_by_category

    # Live run (football profiles):
    uv run python -m maccabipediabot.maintenance.football.refresh_by_category --live

    # Live run, a different profiles category:
    uv run python -m maccabipediabot.maintenance.football.refresh_by_category \
        --live --category "פרופילי כדורסל"
"""
from __future__ import annotations

import logging

import pywikibot
from pywikibot.exceptions import ServerError, TimeoutError as PwbTimeoutError

from maccabipediabot.common.logging_setup import setup_logging
from maccabipediabot.common.wiki_login import get_site
from maccabipediabot.common.wiki_purge import purge_pages

logger = logging.getLogger(__name__)

DEFAULT_CATEGORY = "פרופילי כדורגל"

# Profile pages are expensive to re-parse (each runs several Cargo/stats queries,
# ~2-3s per page), and `forcelinkupdate` makes the server do that work inline.
# wiki_purge's default of 50 titles/request overshoots the 45s read timeout and
# aborts the whole sweep, so batch far smaller here.
BATCH_SIZE = 10


def collect_members(site: pywikibot.Site, category: str) -> list[pywikibot.Page]:
    """Return the article members of `category` (excludes subcategories)."""
    return list(pywikibot.Category(site, category).articles(recurse=False))


def main(dry_run: bool, category: str) -> int:
    """Purge every member of `category` so its live categorylinks refresh.

    Batches are purged independently: a batch that times out is logged and
    skipped rather than aborting the sweep, so one slow request can't cost us
    the remaining profiles. Returns 1 if any batch failed so CI surfaces it.
    """
    setup_logging(level=logging.INFO)
    site = get_site()

    pages = collect_members(site, category)
    logger.info("Found %d member pages in category %r", len(pages), category)

    purged = 0
    failed_batches = 0
    for start in range(0, len(pages), BATCH_SIZE):
        batch = pages[start:start + BATCH_SIZE]
        try:
            purged += purge_pages(site, batch, dry_run=dry_run, chunk_size=BATCH_SIZE)
        except (ServerError, PwbTimeoutError) as exc:
            # The server is just slow on these re-parses; the next scheduled run
            # retries this batch. Keep going so one batch can't sink the sweep.
            failed_batches += 1
            logger.warning(
                "Batch %d-%d failed (%s: %s) — continuing",
                start, start + len(batch) - 1, type(exc).__name__, exc,
            )

    logger.info(
        "Done: %d/%d pages %s, %d batches failed",
        purged, len(pages), "would be purged" if dry_run else "purged", failed_batches,
    )
    return 1 if failed_batches else 0


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--live", action="store_true", default=False,
        help="Actually purge the pages (default: dry-run)",
    )
    parser.add_argument(
        "--category", default=DEFAULT_CATEGORY,
        help=f"Profiles category whose members to refresh (default: {DEFAULT_CATEGORY})",
    )
    args = parser.parse_args()
    sys.exit(main(dry_run=not args.live, category=args.category))
