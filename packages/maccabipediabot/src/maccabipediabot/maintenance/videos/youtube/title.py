"""Title formatter for MaccabiPedia YouTube uploads.

Channel convention: teams listed with Maccabi first, score in parentheses at the end,
digits stored reversed. YouTube's BIDI renderer flips digit order inside parens in RTL
context; storing `(2-0)` causes the display to show `(0-2)`. Readers then interpret
`Maccabi - Hapoel (0-2)` as Maccabi=0, Hapoel=2 — the intended semantics.

Example:
    format_video_title(
        season="2008-09",
        competition="גביע המדינה",
        round_name="סיבוב ט",
        maccabi_score=0,
        opponent="הפועל תל אביב",
        opponent_score=2,
        video_type=HIGHLIGHTS,
    )
    → 'עונת 2008-09 גביע המדינה סיבוב ט מכבי תל אביב - הפועל תל אביב (2-0) תקציר'
"""
from typing import Literal

MACCABI_TEAM = "מכבי תל אביב"
FULL_MATCH = "משחק מלא"
HIGHLIGHTS = "תקציר"

VideoType = Literal["משחק מלא", "תקציר"]


def format_video_title(
    *,
    season: str,
    competition: str,
    round_name: str,
    maccabi_score: int,
    opponent: str,
    opponent_score: int,
    video_type: VideoType,
) -> str:
    score_in_storage = f"({opponent_score}-{maccabi_score})"
    return (
        f"עונת {season} {competition} {round_name} "
        f"{MACCABI_TEAM} - {opponent} {score_in_storage} {video_type}"
    )


def season_playlist_title(season: str) -> str:
    """`2008-09` → `מכביפדיה | עונת 2008/09`."""
    start, end = season.split("-")
    return f"מכביפדיה | עונת {start}/{end}"
