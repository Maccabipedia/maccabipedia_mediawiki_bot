"""Render tests for gamesbot_basketball."""
from datetime import datetime

from maccabipediabot.basketball.basketball_game import BasketballGame, PlayerSummary
from maccabipediabot.basketball.gamesbot_basketball import (
    render_basketball_game_to_wiki,
)


def _player(name: str, points: int) -> PlayerSummary:
    return PlayerSummary(
        name=name,
        is_starting_five=True,
        total_points=points,
        field_goals_attempts=10,
        field_goals_scored=4,
        three_scores_attempts=5,
        three_scores_scored=2,
        free_throws_attempts=4,
        free_throws_scored=4,
    )


def _game() -> BasketballGame:
    return BasketballGame(
        home_team_name="מכבי תל אביב",
        away_team_name="הפועל ירושלים",
        competition="ליגת העל",
        fixture="מחזור 5",
        game_date=datetime(2025, 1, 15, 20, 30),
        home_team_score=92,
        away_team_score=85,
        game_url=["https://basket.co.il/game-zone.asp?GameId=99999"],
        season="2024/25",
        arena="היכל מנורה מבטחים",
        crowd=11000,
        referee="עומר אסתרון",
        referee_assistants=["דן ילון", "אדר פאר"],
        maccabi_coach="עודד קטש",
        opponent_coach="יונתן אלון",
        maccabi_players=[_player("טל ברודי", 28), _player("מוטל'ה שפיגלר", 18)],
        opponent_players=[_player("ערן זהבי", 22)],
        first_quarter_maccabi_points=24,
        second_quarter_maccabi_points=21,
        third_quarter_maccabi_points=25,
        fourth_quarter_maccabi_points=22,
    )


def test_render_uses_basketball_template_name():
    text = render_basketball_game_to_wiki(_game())
    assert text.startswith("{{משחק כדורסל")
    assert text.endswith("}}")


def test_render_includes_iconic_players():
    text = render_basketball_game_to_wiki(_game())
    assert "טל ברודי" in text
    assert "מוטל'ה שפיגלר" in text


def test_render_includes_referees_joined():
    text = render_basketball_game_to_wiki(_game())
    assert "עומר אסתרון" in text
    assert "דן ילון, אדר פאר" in text


def test_render_includes_per_quarter_scores():
    text = render_basketball_game_to_wiki(_game())
    assert "נקודות מכבי רבע1=24" in text
    assert "נקודות מכבי רבע4=22" in text


def test_render_includes_arena_and_crowd():
    text = render_basketball_game_to_wiki(_game())
    assert "אולם=היכל מנורה מבטחים" in text
    assert "כמות קהל=11000" in text
