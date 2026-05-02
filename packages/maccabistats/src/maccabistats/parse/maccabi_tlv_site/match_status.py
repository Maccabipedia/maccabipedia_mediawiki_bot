# -*- coding: utf-8 -*-
"""Detect whether a maccabi-tlv.co.il match page represents a finished game.

The site publishes the same `/match/...` URL for upcoming, live and finished
games — only the page contents change. The reliable live marker is the
``live`` CSS class on ``div.site-top-banner.fixtures-list`` — set throughout
the match (including half-time and stoppage time) and stripped the moment the
final whistle is logged.
"""


class MatchNotFinishedError(Exception):
    """Raised when a maccabi-tlv match page is for a not-yet-finished game."""


def is_match_finished(match_page_bs) -> bool:
    top_banner = match_page_bs.select_one("div.site-top-banner.fixtures-list")
    is_live = top_banner is not None and "live" in (top_banner.get("class") or [])
    return not is_live
