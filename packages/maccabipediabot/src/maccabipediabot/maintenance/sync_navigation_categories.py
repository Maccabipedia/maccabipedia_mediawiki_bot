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

import enum
import re
from dataclasses import dataclass
from typing import Iterator, Literal

import pywikibot

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


_STUB_BOILERPLATE_MARKER = "זהו דף קטגוריה"


class PageState(enum.Enum):
    CANONICAL = "canonical"
    EMPTY = "empty"
    STUB = "stub"
    OTHER = "other"


def _canonical_match_regex(match: ParsedMatch) -> re.Pattern[str]:
    """Whitespace-tolerant regex that matches the canonical invocation for *match*.

    Tolerates extra whitespace inside the braces but requires the right
    template name and parameter values.
    """
    template = TEMPLATE_TROPHY if match.kind == "trophy" else TEMPLATE_SEASONS
    pattern = (
        rf"\{{\{{\s*{re.escape(template)}\s*"
        rf"\|\s*ענף\s*=\s*{re.escape(match.sport)}\s*"
    )
    if match.kind == "trophy":
        assert match.trophy_type is not None
        pattern += rf"\|\s*תואר\s*=\s*{re.escape(match.trophy_type)}\s*"
    if match.role == "staff":
        pattern += r"\|\s*האם אנשי צוות\s*=\s*כן\s*"
    pattern += r"\}\}"
    return re.compile(pattern)


def classify_page_text(text: str, match: ParsedMatch) -> PageState:
    """Classify a category page's current wikitext for the given parsed match."""
    stripped = text.strip()
    if not stripped:
        return PageState.EMPTY
    if _canonical_match_regex(match).search(stripped):
        return PageState.CANONICAL
    if stripped.startswith(_STUB_BOILERPLATE_MARKER):
        return PageState.STUB
    return PageState.OTHER


_DISCOVERY_PREFIXES = ("שחקני ", "אנשי צוות ")


def discover_matches(
    site: pywikibot.Site, sport_filter: str | None = None
) -> Iterator[tuple[str, ParsedMatch]]:
    """Yield (title, ParsedMatch) for every category page matching the four patterns.

    Iterates `site.allcategories(prefix=...)` for the two role prefixes; sport_filter
    (if given) further narrows to a single sport.
    """
    for prefix in _DISCOVERY_PREFIXES:
        for cat in site.allcategories(prefix=prefix):
            title = cat.title(with_ns=False)
            match = parse_category_title(title)
            if match is None:
                continue
            if sport_filter is not None and match.sport != sport_filter:
                continue
            yield title, match
