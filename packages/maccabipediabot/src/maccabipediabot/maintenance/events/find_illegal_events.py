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
import requests

logger = logging.getLogger(__name__)

WIKI_BASE_URL = "https://www.maccabipedia.co.il"
API_URL = "https://www.maccabipedia.co.il/api.php"
TRACKING_CATEGORY = "אירועי שחקנים לא חוקיים"
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
