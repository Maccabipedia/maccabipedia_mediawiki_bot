"""
Create missing football referee pages.

Scans every main and assistant referee referenced in ``Football_Games`` and
``Games_Referees`` on MaccabiPedia and creates a ``{{שופט כדורגל}}`` stub for
anyone who does not yet have a ``כדורגל:{name} (שופט)`` page.

This clears the tracking category ``משחקים המפנים לשופט ללא עמוד``, which is
emitted by ``תבנית:קטלוג משחקים`` when the template's ``#ifexist`` probe on
``כדורגל: {name} (שופט)`` fails for a main or assistant referee.

How to run
----------
    uv run python -m maccabipediabot.maintenance.football.create_missing_football_referee_pages

Set ``SHOULD_SAVE = True`` to actually create the pages (default is dry-run).
"""
import logging
import sys
from collections.abc import Iterable

import pywikibot as pw
import requests

from maccabipediabot.common.wiki_login import get_site

logging.basicConfig(format="%(asctime)s : %(levelname)s : %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

SHOULD_SAVE = False

CARGO_EXPORT_URL = "https://www.maccabipedia.co.il/index.php"
CARGO_LIMIT = 5000
REFEREE_TEMPLATE_NAME = "שופט כדורגל"
REFEREE_PAGE_TITLE_FORMAT = "כדורגל:{name} (שופט)"
# maccabistats writes this sentinel when the source had no referee; skip it.
SENTINEL_NO_REFEREE = "Cant found referee"


def _cargo_export(tables: str, fields: str) -> list[dict]:
    """Call ``Special:CargoExport`` and return the decoded JSON rows."""
    params = {
        "title": "Special:CargoExport",
        "format": "json",
        "tables": tables,
        "fields": fields,
        "limit": str(CARGO_LIMIT),
    }
    response = requests.get(CARGO_EXPORT_URL, params=params, timeout=60)
    if response.status_code != 200 or "application/json" not in response.headers.get("Content-Type", ""):
        raise RuntimeError(
            f"Unexpected Cargo response for tables={tables}: "
            f"status={response.status_code}\n{response.text[:500]}"
        )
    return response.json()


def _iter_assistant_names(raw_assistants: object) -> Iterable[str]:
    """Yield cleaned assistant-referee names from a Cargo list field.

    The Cargo list field comes through as a JSON array, but fall back to a
    comma-split for strings in case the format ever changes on the wire.
    """
    if raw_assistants is None:
        return
    if isinstance(raw_assistants, str):
        candidates: Iterable[str] = raw_assistants.split(",")
    elif isinstance(raw_assistants, list):
        candidates = raw_assistants
    else:
        return
    for candidate in candidates:
        if not isinstance(candidate, str):
            continue
        name = candidate.strip()
        if name:
            yield name


def collect_all_referee_names() -> list[str]:
    """Return a sorted de-duplicated list of every referee referenced on the wiki."""
    names: set[str] = set()

    logger.info("Fetching main referees from Football_Games ...")
    main_rows = _cargo_export("Football_Games", "_pageName,Refs")
    for row in main_rows:
        main_ref = (row.get("Refs") or "").strip()
        if main_ref and main_ref != SENTINEL_NO_REFEREE:
            names.add(main_ref)
    logger.info("  %d main referees in %d rows", len(names), len(main_rows))

    logger.info("Fetching assistant referees from Games_Referees ...")
    assist_rows = _cargo_export("Games_Referees", "_pageName,AssistantReferees")
    before = len(names)
    for row in assist_rows:
        for name in _iter_assistant_names(row.get("AssistantReferees")):
            if name != SENTINEL_NO_REFEREE:
                names.add(name)
    logger.info("  +%d unique assistants (total: %d)", len(names) - before, len(names))

    return sorted(names)


def build_referee_stub_wikitext(name: str) -> str:
    return f"{{{{{REFEREE_TEMPLATE_NAME}\n|שם להצגה={name}\n}}}}"


def create_referee_stub(site: pw.Site, name: str) -> str:
    """Create the stub for ``name`` if missing. Returns ``'created'``, ``'exists'``, or ``'skipped'``."""
    title = REFEREE_PAGE_TITLE_FORMAT.format(name=name)
    page = pw.Page(site, title)
    if page.exists():
        logger.debug("EXISTS  %s", title)
        return "exists"

    page.text = build_referee_stub_wikitext(name)
    if SHOULD_SAVE:
        page.save(summary="MaccabiBot - create missing football referee stub")
        logger.info("CREATED %s", title)
        return "created"

    logger.info("[DRY RUN] would create %s", title)
    return "skipped"


def main() -> None:
    site = get_site()
    names = collect_all_referee_names()
    logger.info("Found %d unique referee names", len(names))

    created = exists = skipped = 0
    for name in names:
        result = create_referee_stub(site, name)
        if result == "created":
            created += 1
        elif result == "exists":
            exists += 1
        else:
            skipped += 1

    logger.info(
        "Done. created=%d exists=%d dry-run-skipped=%d (SHOULD_SAVE=%s)",
        created,
        exists,
        skipped,
        SHOULD_SAVE,
    )
    if not SHOULD_SAVE:
        logger.info("Re-run with SHOULD_SAVE = True to actually create the pages.")


if __name__ == "__main__":
    sys.exit(main())
