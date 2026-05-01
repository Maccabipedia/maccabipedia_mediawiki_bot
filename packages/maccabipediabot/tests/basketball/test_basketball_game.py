from datetime import datetime

import pytest

from maccabipediabot.basketball.basketball_game import BasketballGame, PlayerSummary


def _make_player(**overrides) -> PlayerSummary:
    defaults = dict(
        name="ישראל ישראלי",
        is_starting_five=True,
        total_points=10,
        field_goals_attempts=10,   # 2pt: distinct from free_throws to detect a swap
        field_goals_scored=5,
        three_scores_attempts=4,
        three_scores_scored=2,
        free_throws_attempts=8,    # 1pt
        free_throws_scored=6,
    )
    return PlayerSummary(**{**defaults, **overrides})


def _raw_game(**overrides):
    defaults = dict(
        HomeAway="בית", Opponent="הפועל ירושלים", Competition="BSL", Date="15-01-2024",
        TotalPointsMaccabi=90, TotalPointsOpponent=80, GameUrl=["http://example.com"],
    )
    return {**defaults, **overrides}


# ---------------------------------------------------------------------------
# PlayerSummary template — one comprehensive render check + the bug-fix guard
# ---------------------------------------------------------------------------

def test_player_summary_renders_full_template_correctly():
    """Single render check covering: wrapper, field order (2pt before 3pt), label
    correctness (free_throws → עונשין, field_goals → שתי נק), is_starting_five mapping,
    no trailing space before }}."""
    p = _make_player(name="טל ברודי", is_starting_five=True)
    rendered = p.__maccabipedia__()
    assert rendered.startswith("{{אירועי שחקן סל |")
    assert rendered.endswith("}}")
    assert " }}" not in rendered  # no extra space before closing braces

    # Bug-fix guard: 2pt and free-throw labels not swapped.
    assert "זריקות שתי נק=10" in rendered    # field_goals_attempts (2pt)
    assert "קליעות שתי נק=5" in rendered     # field_goals_scored
    assert "זריקות עונשין=8" in rendered     # free_throws_attempts (1pt)
    assert "קליעות עונשין=6" in rendered     # free_throws_scored

    # Field order: 2pt block must appear before 3pt block.
    assert 0 < rendered.find("זריקות שתי נק") < rendered.find("זריקות שלוש נק")


@pytest.mark.parametrize("starting_five, expected_text", [
    (True, "חמישייה=כן |"),
    (False, "חמישייה=לא |"),     # confirmed non-starter → "לא"
    (None, "חמישייה= |"),         # unknown → empty
])
def test_player_summary_starting_five_three_states(starting_five, expected_text):
    assert expected_text in _make_player(is_starting_five=starting_five).__maccabipedia__()


def test_player_summary_zero_points_renders_as_empty():
    """Wiki convention: a player who scored 0 (or DNP) shows 'נק=' not 'נק=0'."""
    assert "|נק= |" in _make_player(total_points=0).__maccabipedia__()


@pytest.mark.parametrize("field", [
    "number", "minutes_played",
    "defensive_rebounds", "offensive_rebounds", "personal_total_fouls",
    "steals", "turnovers", "assists", "blocks",
])
def test_player_summary_optional_int_none_never_renders_as_literal_None(field):
    """Catches the whole class of 'leaks Python None into the wiki' bug —
    the originator of which was `מספר=None` for two #0-jersey players on the
    29-04-2026 Maccabi vs Netanya page (Lundberg, Cameron Oliver)."""
    rendered = _make_player(**{field: None}).__maccabipedia__()
    assert "=None" not in rendered


# ---------------------------------------------------------------------------
# BasketballGame — home/away logic + from_raw
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("home, away, home_score, away_score, expected_opp, expected_maccabi_pts", [
    ("מכבי תל אביב", "הפועל ירושלים", 90, 80, "הפועל ירושלים", 90),  # home game
    ("הפועל ירושלים", "מכבי תל אביב", 80, 90, "הפועל ירושלים", 90),  # away game
])
def test_basketball_game_opponent_and_maccabi_points(home, away, home_score, away_score,
                                                     expected_opp, expected_maccabi_pts):
    game = BasketballGame(
        home_team_name=home, away_team_name=away, competition="BSL", fixture="1",
        game_date=datetime(2024, 1, 15), home_team_score=home_score,
        away_team_score=away_score, game_url=[],
    )
    assert game.opponent_name == expected_opp
    assert game.maccabi_points == expected_maccabi_pts


@pytest.mark.parametrize("home_away, expected_home, expected_away, expected_home_score, expected_away_score", [
    ("בית", "מכבי תל אביב", "הפועל ירושלים", 90, 80),
    ("חוץ", "הפועל ירושלים", "מכבי תל אביב", 80, 90),
])
def test_basketball_game_from_raw(home_away, expected_home, expected_away,
                                  expected_home_score, expected_away_score):
    game = BasketballGame.from_raw(_raw_game(HomeAway=home_away))
    assert game.home_team_name == expected_home
    assert game.away_team_name == expected_away
    assert game.home_team_score == expected_home_score
    assert game.away_team_score == expected_away_score
    assert game.game_date == datetime(2024, 1, 15)
