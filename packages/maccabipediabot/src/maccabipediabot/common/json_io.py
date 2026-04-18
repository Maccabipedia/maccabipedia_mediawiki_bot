"""Generic JSON I/O helpers for pydantic models."""
import json
import logging
from pathlib import Path
from typing import Iterable

from pydantic import BaseModel

logger = logging.getLogger(__name__)


def write_pydantic_list_as_json(items: Iterable[BaseModel], output_path: Path) -> None:
    """Write a list of pydantic models to `output_path` as a single JSON array.

    UTF-8, no ASCII escaping (Hebrew/non-ASCII stays readable). Creates parent
    directories if needed. Logs a single info line with the count.
    """
    items_list = list(items)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps([item.model_dump(mode="json") for item in items_list], ensure_ascii=False),
        encoding="utf-8",
    )
    logger.info("Wrote %d items to %s", len(items_list), output_path)
