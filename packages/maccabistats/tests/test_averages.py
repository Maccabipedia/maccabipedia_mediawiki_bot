"""Tests for MaccabiGamesAverageStats."""
from sys import maxsize

from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats
from conftest import mock_players_data


class TestAverages:
    def test_goals_for_maccabi(self, maccabi_games):
        # 17 goals in 10 games = 1.70
        assert maccabi_games.averages.goals_for_maccabi == 1.7

    def test_goals_against_maccabi(self, maccabi_games):
        # 10 goals against in 10 games = 1.0
        assert maccabi_games.averages.goals_against_maccabi == 1.0

    def test_maccabi_diff(self, maccabi_games):
        # 17-10 = 7 diff in 10 games = 0.7
        assert maccabi_games.averages.maccabi_diff == 0.7

    def test_averages_for_subset(self, maccabi_games):
        wins = maccabi_games.maccabi_wins
        # Wins should have higher goals_for average
        assert wins.averages.goals_for_maccabi > maccabi_games.averages.goals_for_maccabi

    def test_averages_empty_games_raises_zero_division(self):
        """averages.py has no zero-division guard — this documents the production behavior."""
        import pytest
        empty = MaccabiGamesStats([], players_data=mock_players_data())
        with pytest.raises(ZeroDivisionError):
            empty.averages.goals_for_maccabi
        with pytest.raises(ZeroDivisionError):
            empty.averages.goals_against_maccabi
        with pytest.raises(ZeroDivisionError):
            empty.averages.maccabi_diff


class TestRatioEdgeCases:
    def test_goals_ratio_zero_against(self):
        """goals_ratio should return maxsize when no goals scored against."""
        empty = MaccabiGamesStats([], players_data=mock_players_data())
        assert empty.results.goals_ratio == maxsize

    def test_wins_percentage_no_games(self):
        empty = MaccabiGamesStats([], players_data=mock_players_data())
        assert empty.results.wins_percentage == maxsize
        assert empty.results.losses_percentage == maxsize
        assert empty.results.ties_percentage == maxsize
        assert empty.results.clean_sheets_percentage == maxsize

    def test_goals_ratio_with_clean_sheets_only(self, maccabi_games):
        """When filtering to games where opponent scored 0, ratio should be maxsize."""
        clean_only = MaccabiGamesStats(
            [g for g in maccabi_games if g.not_maccabi_team.score == 0],
            players_data=mock_players_data())
        assert len(clean_only) > 0
        assert clean_only.results.goals_ratio == maxsize

    def test_goals_ratio_normal(self, maccabi_games):
        # 17/10 = 1.7
        assert maccabi_games.results.goals_ratio == 1.7

    def test_zero_goals_for_zero_against(self):
        """0 goals for, 0 against: ratio should be maxsize (division by 0)."""
        from game_fixtures import _game, _player, _lineup, TeamInGame
        import datetime
        game = _game(
            competition="ליגת העל", fixture="מחזור1", season="2020/21",
            date=datetime.datetime(2020, 1, 1),
            stadium="s", referee="r",
            home_team=TeamInGame("מכבי תל אביב", "c", 0, [_player("p", 1, [_lineup()])]),
            away_team=TeamInGame("opp", "c2", 0, [_player("o", 1, [_lineup()])]),
        )
        stats = MaccabiGamesStats([game], players_data=mock_players_data())
        assert stats.results.goals_ratio == maxsize
