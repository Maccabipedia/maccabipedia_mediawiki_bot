"""Parser tests for crawl_euroleague."""
from datetime import datetime
from pathlib import Path

import pytest

from maccabipediabot.basketball.basketball_game import BasketballGame
from maccabipediabot.basketball.crawl_euroleague import (
    MACCABI_TEAM_NAME_ENG,
    EuroleagueGameMeta,
    discover_games_from_html,
    extract_next_data,
    parse_game_page,
)

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_game_page_against_real_fixture():
    """Round-trip the captured Euroleague game-center page against a hand-verified
    expected BasketballGame snapshot. One assert covers everything."""
    meta = EuroleagueGameMeta(
        scrape_url="https://www.euroleaguebasketball.net/en/euroleague/game-center/2025-26/anadolu-efes-istanbul-maccabi-rapyd-tel-aviv/E2025/1/",
        game_date=datetime(2025, 9, 30, 20, 30),
        is_maccabi_home=False,
        opponent_name_eng="Anadolu Efes Istanbul",
        home_team_score=85,
        away_team_score=78,
        fixture_round=1,
    )
    html = (FIXTURES / "euroleague_game_E2025_R1.html").read_bytes().decode("utf-8")
    expected = BasketballGame.model_validate_json(
        (FIXTURES / "euroleague_game_E2025_R1.expected.json").read_text("utf-8")
    )
    actual = parse_game_page(extract_next_data(html), meta)
    assert actual.model_dump() == expected.model_dump()


def test_extract_next_data_raises_when_script_missing():
    with pytest.raises(RuntimeError, match="missing __NEXT_DATA__"):
        extract_next_data("<html><body>no script here</body></html>")


# ---------------------------------------------------------------------------
# Synthetic __NEXT_DATA__ — covers the home/away swap + overtime branches
# that the real fixture (Maccabi-away, regulation) doesn't exercise.
# ---------------------------------------------------------------------------

def _synthetic_next_data(*, home_quarters: dict, away_quarters: dict) -> dict:
    return {
        "props": {"pageProps": {"mappedData": {"rawGameInfo": {
            "venue": {"name": "MENORA MIVTACHIM ARENA"},
            "audience": 11000,
            "referees": [{"name": "JAVOR, DAMIR"}],
            "home": {
                "name": MACCABI_TEAM_NAME_ENG,
                "coach": {"name": "KATTASH, ODED"},
                "quarters": home_quarters,
                "players": [{"name": "BRODY, TAL", "dorsal": "5", "startFive": True,
                             "stats": {"timePlayed": 1800, "points": 22}}],
            },
            "away": {
                "name": "Olympiacos Piraeus",
                "coach": {"name": "BARTZOKAS, GEORGIOS"},
                "quarters": away_quarters,
                "players": [{"name": "SPIEGLER, MOTI", "dorsal": "9", "startFive": True,
                             "stats": {"timePlayed": 1700, "points": 18}}],
            },
        }}}},
    }


def _maccabi_home_meta() -> EuroleagueGameMeta:
    return EuroleagueGameMeta(
        scrape_url="https://www.euroleaguebasketball.net/test-game/",
        game_date=datetime(2025, 11, 1, 20, 30),
        is_maccabi_home=True,
        opponent_name_eng="Olympiacos Piraeus",
        home_team_score=85,
        away_team_score=80,
        fixture_round=7,
    )


def test_parse_game_page_swaps_home_data_to_maccabi_when_maccabi_is_home():
    next_data = _synthetic_next_data(
        home_quarters={"q1": 22, "q2": 21, "q3": 20, "q4": 22, "ot1": None, "ot2": None,
                       "ot3": None, "ot4": None, "ot5": None},
        away_quarters={"q1": 18, "q2": 19, "q3": 22, "q4": 21, "ot1": None, "ot2": None,
                       "ot3": None, "ot4": None, "ot5": None},
    )
    game = parse_game_page(next_data, _maccabi_home_meta())
    assert game.home_team_name == "מכבי תל אביב"
    assert game.first_quarter_maccabi_points == 22  # home values mapped to maccabi_*
    assert game.first_quarter_opponent_points == 18  # away values mapped to opponent_*
    assert any(player.number == 5 for player in game.maccabi_players)  # home player
    assert any(player.number == 9 for player in game.opponent_players)  # away player
    assert game.maccabi_coach == "עודד קטש"


def test_parse_game_page_extracts_overtime_periods():
    next_data = _synthetic_next_data(
        home_quarters={"q1": 25, "q2": 22, "q3": 18, "q4": 20, "ot1": 12, "ot2": 8,
                       "ot3": None, "ot4": None, "ot5": None},
        away_quarters={"q1": 24, "q2": 23, "q3": 19, "q4": 19, "ot1": 10, "ot2": 9,
                       "ot3": None, "ot4": None, "ot5": None},
    )
    game = parse_game_page(next_data, _maccabi_home_meta())
    assert (game.first_overtime_maccabi_points, game.second_overtime_maccabi_points,
            game.third_overtime_maccabi_points) == (12, 8, None)
    assert (game.first_overtime_opponent_points, game.second_overtime_opponent_points,
            game.third_overtime_opponent_points) == (10, 9, None)


# ---------------------------------------------------------------------------
# Discovery (fixture-based; no HTTP)
# ---------------------------------------------------------------------------

def test_discover_games_from_team_results_returns_finished_games_sorted_desc():
    html = (FIXTURES / "euroleague_team_results.html").read_bytes().decode("utf-8")
    metas = discover_games_from_html(html, limit=5)
    assert 1 <= len(metas) <= 5
    for meta in metas:
        assert meta.scrape_url.startswith("https://www.euroleaguebasketball.net/")
        assert meta.opponent_name_eng
    # Sorted descending by date — `>` is strict (no two games on the same instant)
    for earlier, later in zip(metas[1:], metas[:-1]):
        assert later.game_date >= earlier.game_date
