"""Tests for league points calculation."""
import datetime

import pytest

from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats

from players_data_fixtures import create_stub_players_data
from game_fixtures import _game, _player, _lineup, TeamInGame


@pytest.fixture
def pre_1982_game():
    """A single league game from before the 3-point rule (Sep 25, 1982)."""
    return _game(
        competition="ליגת העל", fixture="מחזור1", season="1981/82",
        date=datetime.datetime(1982, 1, 1),
        stadium="בלומפילד", referee="שופט",
        home_team=TeamInGame("מכבי תל אביב", "מאמן", 2, [
            _player("שחקן", 1, [_lineup()]),
        ]),
        away_team=TeamInGame("יריב", "מאמן_יריב", 0, [
            _player("יריב", 1, [_lineup()]),
        ]),
    )


@pytest.fixture
def pre_1982_tie_game():
    """A tied league game from before the 3-point rule."""
    return _game(
        competition="ליגת העל", fixture="מחזור2", season="1981/82",
        date=datetime.datetime(1982, 2, 1),
        stadium="בלומפילד", referee="שופט",
        home_team=TeamInGame("מכבי תל אביב", "מאמן", 1, [
            _player("שחקן", 1, [_lineup()]),
        ]),
        away_team=TeamInGame("יריב", "מאמן_יריב", 1, [
            _player("יריב", 1, [_lineup()]),
        ]),
    )


class TestPointsCalculation:
    def test_points_for_league_games(self, maccabi_games):
        league = maccabi_games.league_games
        # All league games are post-1982, so 3 points for win, 1 for tie
        # League games results: W, L, T, W, W, L, T, W
        # Points: 3+0+1+3+3+0+1+3 = 14
        assert league.points == 14

    def test_success_rate(self, maccabi_games):
        league = maccabi_games.league_games
        # 14 points out of 8*3=24 possible
        assert league.success_rate == round(14 / 24, 3)

    def test_points_raises_for_non_league(self, maccabi_games):
        with pytest.raises(TypeError, match="league games"):
            maccabi_games.points


class TestPointsPrePost1982:
    def test_pre_1982_win_gives_2_points(self, pre_1982_game):
        stats = MaccabiGamesStats([pre_1982_game], players_data=create_stub_players_data())
        assert stats.points == 2

    def test_pre_1982_tie_gives_1_point(self, pre_1982_tie_game):
        stats = MaccabiGamesStats([pre_1982_tie_game], players_data=create_stub_players_data())
        assert stats.points == 1

    def test_pre_1982_possible_points_is_2_per_game(self, pre_1982_game, pre_1982_tie_game):
        from maccabistats.stats_utilities.points_calculator import calculate_possible_points_for_games
        stats = MaccabiGamesStats([pre_1982_game, pre_1982_tie_game], players_data=create_stub_players_data())
        assert calculate_possible_points_for_games(stats) == 4  # 2 games * 2 points each

    def test_mixed_eras_points(self, maccabi_games, pre_1982_game):
        league = maccabi_games.league_games
        mixed = MaccabiGamesStats(league.games + [pre_1982_game], players_data=create_stub_players_data())
        # 14 (post-1982 league) + 2 (pre-1982 win) = 16
        assert mixed.points == 16
