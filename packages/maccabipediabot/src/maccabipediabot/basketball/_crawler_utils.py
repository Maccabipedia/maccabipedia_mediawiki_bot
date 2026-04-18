"""Shared helpers used by crawl_basket_co_il and crawl_euroleague."""
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


# Box-score scrapers treat absent / None / "" / "-" as "0" deliberately —
# a player who didn't take any free throws genuinely has 0 attempts.
_NUMERIC_ABSENT = {None, "", "-"}


def to_int(value) -> int:
    """Coerce a stat value to int. Absent (None / "" / "-") → 0; anything
    else just goes through int() and propagates its own TypeError/ValueError
    on truly malformed input — so a schema-drift bug fails loudly instead of
    silently zeroing a column for every player."""
    if value in _NUMERIC_ABSENT:
        return 0
    return int(value)


def to_int_or_none(value) -> int | None:
    """Like to_int but returns None for absent values."""
    if value in _NUMERIC_ABSENT:
        return None
    return int(value)


def season_from_date(d: datetime) -> str:
    """Return season string like '2024/25'. Israeli basketball season runs Sep–Jun."""
    year = d.year
    if d.month >= 9:
        return f"{year}/{(year + 1) % 100:02d}"
    return f"{year - 1}/{year % 100:02d}"
