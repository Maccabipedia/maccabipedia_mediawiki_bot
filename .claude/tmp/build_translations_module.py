"""Assemble translations.py by stitching the header, generated dict bodies, and helper functions."""
from pathlib import Path
from convert_ts_to_py_dict import (
    convert_int_dict,
    parse_ts_dict,
    render_int_dict,
    render_python_dict,
)

TS_DIR = Path(".claude/tmp/ts-source")
OUT_PATH = Path("packages/maccabipediabot/src/maccabipediabot/basketball/translations.py")

teams = parse_ts_dict(TS_DIR / "eng-to-heb-team-name-map.ts")
persons = parse_ts_dict(TS_DIR / "eng-to-heb-person-name-map.ts")
stadiums = parse_ts_dict(TS_DIR / "eng-to-heb-stadium-name-map.ts")
normalize = parse_ts_dict(TS_DIR / "heb-name-normalize-map.ts")
game_types = convert_int_dict(TS_DIR / "basket-game-type-heb-name.ts")

HEADER = '''"""Unified normalization for basketball data flowing into MaccabiPedia.

Contains:
- EN→HE translations for teams, people, stadiums (used by the live crawlers).
- HE→HE player-name normalization (e.g. stripping nicknames).
- basket.co.il game_type code → Hebrew competition name.
- Year-aware HE→HE legacy team-name canonicalization (canonical_team_name, Task 3).
"""
from datetime import datetime
from typing import Optional


'''

FOOTER = '''


def team_name_to_hebrew(name: str) -> str:
    """Translate an English team name to Hebrew. Pass through if unknown."""
    return _TEAM_NAMES.get(name, name)


def person_name_to_hebrew(name: str) -> str:
    """Translate an English person name to Hebrew. Pass through if unknown."""
    return _PERSON_NAMES.get(name, name)


def stadium_name_to_hebrew(name: str) -> str:
    """Translate an English stadium name to Hebrew. Pass through if unknown."""
    return _STADIUM_NAMES.get(name, name)


def normalize_player_name(name: str) -> str:
    """Normalize a Hebrew player name (e.g. strip nickname). Pass through if unknown."""
    return _PLAYER_NAME_NORMALIZE.get(name, name)


def basket_co_il_competition_name(game_type_code: int) -> Optional[str]:
    """Return the Hebrew competition name for a basket.co.il game_type code, or None if unknown."""
    return _BASKET_GAME_TYPE.get(game_type_code)


def canonical_team_name(name: str, game_date: datetime) -> str:
    """Year-aware canonical Hebrew team name. Implemented in Task 3."""
    raise NotImplementedError("Implemented in Task 3")
'''

body_chunks = [
    f"_TEAM_NAMES: dict[str, str] = {render_python_dict(teams)}",
    f"_PERSON_NAMES: dict[str, str] = {render_python_dict(persons)}",
    f"_STADIUM_NAMES: dict[str, str] = {render_python_dict(stadiums)}",
    f"_PLAYER_NAME_NORMALIZE: dict[str, str] = {render_python_dict(normalize)}",
    f"_BASKET_GAME_TYPE: dict[int, str] = {render_int_dict(game_types)}",
]

OUT_PATH.write_text(HEADER + "\n\n".join(body_chunks) + FOOTER, encoding="utf-8")
print(f"wrote {OUT_PATH} ({OUT_PATH.stat().st_size} bytes)")
