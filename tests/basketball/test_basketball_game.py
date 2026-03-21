from datetime import datetime

import pytest

from basketball.basketball_game import BasketballGame, PlayerSummary


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_player(**overrides) -> PlayerSummary:
    defaults = dict(
        name="ישראל ישראלי",
        is_starting_five=True,
        total_points=10,
        field_goals_attempts=5,
        field_goals_scored=3,
        three_scores_attempts=2,
        three_scores_scored=1,
        free_throws_attempts=2,
        free_throws_scored=2,
    )
    return PlayerSummary(**{**defaults, **overrides})


def _make_game(**overrides) -> BasketballGame:
    defaults = dict(
        home_team_name="מכבי תל אביב",
        away_team_name="הפועל ירושלים",
        competition="BSL",
        fixture="1",
        game_date=datetime(2024, 1, 15),
        home_team_score=90,
        away_team_score=80,
        game_url=[],
    )
    return BasketballGame(**{**defaults, **overrides})


# ---------------------------------------------------------------------------
# PlayerSummary
# ---------------------------------------------------------------------------

def test_player_summary_maccabipedia_contains_name():
    p = _make_player(name="ישראל ישראלי")
    assert "שם=ישראל ישראלי" in p.__maccabipedia__()


def test_player_summary_maccabipedia_contains_number():
    p = _make_player(number=7)
    assert "מספר=7" in p.__maccabipedia__()


def test_player_summary_maccabipedia_starting_five_yes():
    p = _make_player(is_starting_five=True)
    assert "חמישייה=כן" in p.__maccabipedia__()


def test_player_summary_maccabipedia_starting_five_no():
    p = _make_player(is_starting_five=False)
    assert "חמישייה=לא" in p.__maccabipedia__()


def test_player_summary_maccabipedia_template_wrapper():
    p = _make_player()
    result = p.__maccabipedia__()
    assert result.startswith("{{אירועי שחקן סל|")
    assert result.endswith("}}")


# ---------------------------------------------------------------------------
# BasketballGame — home game
# ---------------------------------------------------------------------------

def test_home_game_is_home():
    game = _make_game()
    assert game.is_home_game is True


def test_home_game_opponent_name():
    game = _make_game(away_team_name="הפועל ירושלים")
    assert game.opponent_name == "הפועל ירושלים"


def test_home_game_maccabi_points():
    game = _make_game(home_team_score=90, away_team_score=80)
    assert game.maccabi_points == 90


def test_home_game_opponent_points():
    game = _make_game(home_team_score=90, away_team_score=80)
    assert game.opponent_points == 80


# ---------------------------------------------------------------------------
# BasketballGame — away game
# ---------------------------------------------------------------------------

def test_away_game_is_not_home():
    game = _make_game(home_team_name="הפועל ירושלים", away_team_name="מכבי תל אביב")
    assert game.is_home_game is False


def test_away_game_opponent_name():
    game = _make_game(home_team_name="הפועל ירושלים", away_team_name="מכבי תל אביב")
    assert game.opponent_name == "הפועל ירושלים"


def test_away_game_maccabi_points():
    game = _make_game(home_team_name="הפועל ירושלים", away_team_name="מכבי תל אביב",
                      home_team_score=80, away_team_score=90)
    assert game.maccabi_points == 90


def test_away_game_opponent_points():
    game = _make_game(home_team_name="הפועל ירושלים", away_team_name="מכבי תל אביב",
                      home_team_score=80, away_team_score=90)
    assert game.opponent_points == 80


# ---------------------------------------------------------------------------
# BasketballGame.from_raw
# ---------------------------------------------------------------------------

def _raw_game(**overrides):
    defaults = dict(
        HomeAway="בית",
        Opponent="הפועל ירושלים",
        Competition="BSL",
        Date="15-01-2024",
        TotalPointsMaccabi=90,
        TotalPointsOpponent=80,
        GameUrl=["http://example.com"],
    )
    return {**defaults, **overrides}


def test_from_raw_home_sets_home_team():
    game = BasketballGame.from_raw(_raw_game(HomeAway="בית"))
    assert game.home_team_name == "מכבי תל אביב"
    assert game.away_team_name == "הפועל ירושלים"


def test_from_raw_away_sets_away_team():
    game = BasketballGame.from_raw(_raw_game(HomeAway="חוץ"))
    assert game.home_team_name == "הפועל ירושלים"
    assert game.away_team_name == "מכבי תל אביב"


def test_from_raw_home_scores():
    game = BasketballGame.from_raw(_raw_game(HomeAway="בית", TotalPointsMaccabi=90, TotalPointsOpponent=80))
    assert game.home_team_score == 90
    assert game.away_team_score == 80


def test_from_raw_away_scores():
    game = BasketballGame.from_raw(_raw_game(HomeAway="חוץ", TotalPointsMaccabi=90, TotalPointsOpponent=80))
    assert game.home_team_score == 80
    assert game.away_team_score == 90


def test_from_raw_date_parsed():
    game = BasketballGame.from_raw(_raw_game(Date="15-01-2024"))
    assert game.game_date == datetime(2024, 1, 15)
