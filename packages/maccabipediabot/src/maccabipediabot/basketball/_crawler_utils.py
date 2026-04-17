"""Shared helpers used by crawl_basket_co_il and crawl_euroleague."""
import json
import logging
from datetime import datetime
from pathlib import Path

from maccabipediabot.basketball.basketball_game import BasketballGame

logger = logging.getLogger(__name__)


def to_int(value) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def to_int_or_none(value) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
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
        json.dumps([g.model_dump(mode="json") for g in games], ensure_ascii=False),
        encoding="utf-8",
    )
    logger.info("Wrote %d games to %s", len(games), output_path)
