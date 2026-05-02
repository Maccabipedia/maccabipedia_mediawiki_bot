# -*- coding: utf-8 -*-
"""Detect whether a maccabi-tlv.co.il match page represents a finished game.

The site publishes the same `/match/...` URL for upcoming, live and finished
games — only the page contents change. The reliable live marker is the
``live`` CSS class on ``div.site-top-banner.fixtures-list`` — set throughout
the match (including half-time and stoppage time) and stripped the moment the
final whistle is logged.

When the banner element is missing entirely we fail closed (treat the match
as unfinished). That makes a future site rename of the marker fail loudly via
the season crawl skipping all games rather than silently re-introduce the
mid-match-upload bug this guard exists to prevent.
"""

import logging

logger = logging.getLogger(__name__)


class MatchNotFinishedError(Exception):
    """Raised when a maccabi-tlv match page is for a not-yet-finished game."""


def is_match_finished(match_page_bs) -> bool:
    top_banner = match_page_bs.select_one("div.site-top-banner.fixtures-list")
    if top_banner is None:
        logger.warning("maccabi-tlv match page is missing the fixtures-list "
                       "top banner — treating as unfinished")
        return False
    return "live" not in (top_banner.get("class") or [])
