"""Parser tests for crawl_euroleague."""
from datetime import datetime
from pathlib import Path

from maccabipediabot.basketball.crawl_euroleague import (
    MACCABI_TEAM_NAME_ENG,
    EuroleagueGameMeta,
    extract_next_data,
    parse_game_page,
)

FIXTURES = Path(__file__).parent / "fixtures"
GAME_HTML = (FIXTURES / "euroleague_game_E2025_R1.html").read_bytes().decode("utf-8")


def _meta() -> EuroleagueGameMeta:
    """Game E2025 R1: Anadolu Efes (home) vs Maccabi Tel Aviv (away)."""
    return EuroleagueGameMeta(
        scrape_url="https://www.euroleaguebasketball.net/en/euroleague/game-center/2025-26/anadolu-efes-istanbul-maccabi-rapyd-tel-aviv/E2025/1/",
        game_date=datetime(2025, 9, 30, 20, 30),
        is_maccabi_home=False,
        opponent_name_eng="Anadolu Efes Istanbul",
        home_team_score=85,
        away_team_score=78,
        fixture_round=1,
    )


def test_extract_next_data_returns_dict():
    data = extract_next_data(GAME_HTML)
    assert isinstance(data, dict)
    assert "props" in data


def test_extract_next_data_raises_when_script_missing():
    import pytest
    with pytest.raises(RuntimeError, match="missing __NEXT_DATA__"):
        extract_next_data("<html><body>no script here</body></html>")


def test_parse_game_page_extracts_player_lists():
    game = parse_game_page(extract_next_data(GAME_HTML), _meta())
    assert len(game.maccabi_players) >= 5
    assert len(game.opponent_players) >= 5
    assert any(p.name and p.total_points >= 0 for p in game.maccabi_players)


def test_parse_game_page_extracts_coaches():
    game = parse_game_page(extract_next_data(GAME_HTML), _meta())
    assert game.maccabi_coach
    assert game.opponent_coach


def test_parse_game_page_translates_team_names():
    game = parse_game_page(extract_next_data(GAME_HTML), _meta())
    assert "מכבי תל אביב" in (game.home_team_name, game.away_team_name)
    # Anadolu Efes Istanbul → אנאדולו אפס per translations map
    assert "אנאדולו אפס" in (game.home_team_name, game.away_team_name)


def test_parse_game_page_extracts_per_quarter_scores():
    game = parse_game_page(extract_next_data(GAME_HTML), _meta())
    # Maccabi was AWAY; per the JSON probe quarters were [19, 25, 15, 19]
    assert game.first_quarter_maccabi_points == 19
    assert game.second_quarter_maccabi_points == 25
    assert game.third_quarter_maccabi_points == 15
    assert game.fourth_quarter_maccabi_points == 19
    # Anadolu Efes HOME row was [21, 19, 20, 25]
    assert game.first_quarter_opponent_points == 21
    assert game.fourth_quarter_opponent_points == 25


def test_parse_game_page_extracts_venue_and_crowd():
    game = parse_game_page(extract_next_data(GAME_HTML), _meta())
    assert game.arena  # MORACA → "מוראבה" (per teams_names_changer entry)
    assert game.crowd == 2110


def test_parse_game_page_extracts_referee():
    game = parse_game_page(extract_next_data(GAME_HTML), _meta())
    assert game.referee  # main referee Damir Javor
    assert len(game.referee_assistants) == 2


def test_parse_game_page_sets_fixture_round_prefix():
    game = parse_game_page(extract_next_data(GAME_HTML), _meta())
    assert game.fixture == "מחזור 1"


# ---------------------------------------------------------------------------
# Discovery (fixture-based)
# ---------------------------------------------------------------------------

def test_discover_games_from_team_results_returns_metas():
    from maccabipediabot.basketball.crawl_euroleague import discover_games_from_html

    html = (FIXTURES / "euroleague_team_results.html").read_bytes().decode("utf-8")
    metas = discover_games_from_html(html, limit=3)
    assert 1 <= len(metas) <= 3
    for m in metas:
        assert m.scrape_url.startswith("https://www.euroleaguebasketball.net/")
        assert m.opponent_name_eng


def test_discover_games_from_team_results_no_limit():
    from maccabipediabot.basketball.crawl_euroleague import discover_games_from_html

    html = (FIXTURES / "euroleague_team_results.html").read_bytes().decode("utf-8")
    metas = discover_games_from_html(html, limit=None)
    assert len(metas) >= 30  # team-results fixture had 38 finished games


def test_discover_games_sorted_desc_by_date():
    from maccabipediabot.basketball.crawl_euroleague import discover_games_from_html

    html = (FIXTURES / "euroleague_team_results.html").read_bytes().decode("utf-8")
    metas = discover_games_from_html(html, limit=5)
    for earlier, later in zip(metas[1:], metas[:-1]):
        assert later.game_date >= earlier.game_date


# ---------------------------------------------------------------------------
# Home/away swap + overtime — synthetic fixtures so we don't depend on the
# real fixture happening to have an overtime Maccabi-home game.
# ---------------------------------------------------------------------------

def _synthetic_next_data(
    *,
    home_quarters: dict,
    away_quarters: dict,
    home_team_name: str = MACCABI_TEAM_NAME_ENG,
    away_team_name: str = "Olympiacos Piraeus",
    home_coach: str = "KATTASH, ODED",
    away_coach: str = "BARTZOKAS, GEORGIOS",
) -> dict:
    """Build a minimal __NEXT_DATA__-shaped dict for parse_game_page."""
    return {
        "props": {"pageProps": {"mappedData": {"rawGameInfo": {
            "venue": {"name": "MENORA MIVTACHIM ARENA"},
            "audience": 11000,
            "referees": [{"name": "JAVOR, DAMIR"}, {"name": "ALIAGA, JORDI"}],
            "home": {
                "name": home_team_name,
                "coach": {"name": home_coach},
                "quarters": home_quarters,
                "players": [
                    {"name": "BRODY, TAL", "dorsal": "5", "startFive": True,
                     "stats": {"timePlayed": 1800, "points": 22}},
                ],
            },
            "away": {
                "name": away_team_name,
                "coach": {"name": away_coach},
                "quarters": away_quarters,
                "players": [
                    {"name": "SPIEGLER, MOTI", "dorsal": "9", "startFive": True,
                     "stats": {"timePlayed": 1700, "points": 18}},
                ],
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


def test_parse_game_page_maccabi_home_assigns_home_data_to_maccabi():
    """Regression guard: when Maccabi is home, home_* fields must map to maccabi_*."""
    next_data = _synthetic_next_data(
        home_quarters={"q1": 22, "q2": 21, "q3": 20, "q4": 22,
                       "ot1": None, "ot2": None, "ot3": None, "ot4": None, "ot5": None},
        away_quarters={"q1": 18, "q2": 19, "q3": 22, "q4": 21,
                       "ot1": None, "ot2": None, "ot3": None, "ot4": None, "ot5": None},
    )
    game = parse_game_page(next_data, _maccabi_home_meta())
    assert game.home_team_name == "מכבי תל אביב"
    assert game.first_quarter_maccabi_points == 22  # home values
    assert game.first_quarter_opponent_points == 18  # away values
    # Players + coach should also follow the home/away swap.
    # The synthetic home player has dorsal=5 (Tal Brody), away has dorsal=9 (Spiegler).
    assert any(p.number == 5 for p in game.maccabi_players)
    assert any(p.number == 9 for p in game.opponent_players)
    assert game.maccabi_coach == "עודד קטש"


def test_parse_game_page_overtime_periods_populate_correctly():
    """Regression guard: ot1..ot4 fields must wire through to first/.../fourth_overtime_*_points."""
    next_data = _synthetic_next_data(
        home_quarters={"q1": 25, "q2": 22, "q3": 18, "q4": 20,
                       "ot1": 12, "ot2": 8, "ot3": None, "ot4": None, "ot5": None},
        away_quarters={"q1": 24, "q2": 23, "q3": 19, "q4": 19,
                       "ot1": 10, "ot2": 9, "ot3": None, "ot4": None, "ot5": None},
    )
    game = parse_game_page(next_data, _maccabi_home_meta())
    # Maccabi (home) overtime points
    assert game.first_overtime_maccabi_points == 12
    assert game.second_overtime_maccabi_points == 8
    assert game.third_overtime_maccabi_points is None
    # Opponent (away) overtime points
    assert game.first_overtime_opponent_points == 10
    assert game.second_overtime_opponent_points == 9
    assert game.third_overtime_opponent_points is None
