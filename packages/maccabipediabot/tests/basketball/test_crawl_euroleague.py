"""Parser tests for crawl_euroleague."""
from datetime import datetime
from pathlib import Path

from maccabipediabot.basketball.crawl_euroleague import (
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
        page_title="",
        game_date=datetime(2025, 9, 30, 20, 30),
        is_maccabi_home=False,
        opponent_name_eng="Anadolu Efes Istanbul",
        home_team_score=85,
        away_team_score=78,
        fixture="1",
    )


def test_extract_next_data_returns_dict():
    data = extract_next_data(GAME_HTML)
    assert isinstance(data, dict)
    assert "props" in data


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
