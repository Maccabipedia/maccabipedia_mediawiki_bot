"""Shared helpers used by crawl_basket_co_il and crawl_euroleague."""
import json
import logging
from datetime import datetime
from pathlib import Path

from maccabipediabot.basketball.basketball_game import BasketballGame

logger = logging.getLogger(__name__)


# Box-score scrapers treat absent / None / "" / "-" as "0" deliberately —
# a player who didn't take any free throws genuinely has 0 attempts.
_NUMERIC_ABSENT = {None, "", "-"}


def to_int(value) -> int:
    if value in _NUMERIC_ABSENT:
        return 0
    try:
        return int(value)
    except (TypeError, ValueError):
        # Unexpected non-numeric, non-absent value — log so a future schema
        # drift (e.g. nested {"value": N}) is discoverable.
        logger.debug("to_int got unexpected value %r (%s); defaulting to 0",
                     value, type(value).__name__)
        return 0


def to_int_or_none(value) -> int | None:
    if value in _NUMERIC_ABSENT:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        logger.debug("to_int_or_none got unexpected value %r (%s); returning None",
                     value, type(value).__name__)
        return None


def season_from_date(d: datetime) -> str:
    """Return season string like '2024/25'. Israeli basketball season runs Sep–Jun."""
    year = d.year
    if d.month >= 9:
        return f"{year}/{(year + 1) % 100:02d}"
    return f"{year - 1}/{year % 100:02d}"


def write_results(games: list[BasketballGame], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps([game.model_dump(mode="json") for game in games], ensure_ascii=False),
        encoding="utf-8",
    )
    logger.info("Wrote %d games to %s", len(games), output_path)
