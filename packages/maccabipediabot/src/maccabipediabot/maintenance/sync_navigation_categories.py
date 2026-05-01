"""Sync DPL-based navigation templates onto trophy/seasons category pages.

Replaces the older `football/add_player_category_navbars.py` (which built a
different, now-superseded per-(sport,type) template system).

For every existing category page matching one of four patterns:
  - שחקני {sport} שזכו ב-{N} {trophy_type}
  - אנשי צוות {sport} שזכו ב-{N} {trophy_type}
  - שחקני {sport} ששיחקו {N} עונות במכבי
  - אנשי צוות {sport} שהיו {N} עונות במכבי

…install the canonical `{{ניווט קטגוריות …}}` invocation if missing, then
purge with forcelinkupdate=true so the DPL caches refresh.

Idempotent — safe to re-run.

Usage:
    # Dry-run (default; prints planned changes, makes no edits):
    uv run python -m maccabipediabot.maintenance.sync_navigation_categories

    # Live run (all sports):
    uv run python -m maccabipediabot.maintenance.sync_navigation_categories --live

    # Live run, single sport:
    uv run python -m maccabipediabot.maintenance.sync_navigation_categories --live --sport כדורסל
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

ALLOWED_SPORTS = {"כדורגל", "כדורסל", "כדורעף"}

_RE_TROPHY_PLAYERS = re.compile(r"^שחקני (\S+) שזכו ב-(\d+) (.+)$")
_RE_TROPHY_STAFF = re.compile(r"^אנשי צוות (\S+) שזכו ב-(\d+) (.+)$")
_RE_SEASONS_PLAYERS = re.compile(r"^שחקני (\S+) ששיחקו (\d+) עונות במכבי$")
_RE_SEASONS_STAFF = re.compile(r"^אנשי צוות (\S+) שהיו (\d+) עונות במכבי$")

TEMPLATE_TROPHY = "ניווט קטגוריות זכיה בתארים"
TEMPLATE_SEASONS = "ניווט קטגוריות עונות במכבי"


@dataclass(frozen=True)
class ParsedMatch:
    kind: Literal["trophy", "seasons"]
    sport: str
    role: Literal["players", "staff"]
    n: int
    trophy_type: str | None  # None for seasons


def parse_category_title(title: str) -> ParsedMatch | None:
    """Parse a category title into a ParsedMatch, or return None if it doesn't match.

    `title` is the page title without the `קטגוריה:` namespace prefix.
    Sports outside ALLOWED_SPORTS yield None.
    """
    for regex, kind, role in (
        (_RE_TROPHY_PLAYERS, "trophy", "players"),
        (_RE_TROPHY_STAFF, "trophy", "staff"),
    ):
        trophy_match = regex.match(title)
        if trophy_match:
            sport = trophy_match.group(1)
            if sport not in ALLOWED_SPORTS:
                return None
            return ParsedMatch(
                kind=kind,
                sport=sport,
                role=role,
                n=int(trophy_match.group(2)),
                trophy_type=trophy_match.group(3),
            )
    for regex, role in (
        (_RE_SEASONS_PLAYERS, "players"),
        (_RE_SEASONS_STAFF, "staff"),
    ):
        seasons_match = regex.match(title)
        if seasons_match:
            sport = seasons_match.group(1)
            if sport not in ALLOWED_SPORTS:
                return None
            return ParsedMatch(
                kind="seasons",
                sport=sport,
                role=role,
                n=int(seasons_match.group(2)),
                trophy_type=None,
            )
    return None


def build_canonical_wikitext(match: ParsedMatch) -> str:
    """Return the exact wikitext a category page should contain for this match."""
    staff_param = " |האם אנשי צוות=כן" if match.role == "staff" else ""
    if match.kind == "trophy":
        return (
            f"{{{{{TEMPLATE_TROPHY} |ענף={match.sport} "
            f"|תואר={match.trophy_type}{staff_param}}}}}"
        )
    return f"{{{{{TEMPLATE_SEASONS} |ענף={match.sport}{staff_param}}}}}"
