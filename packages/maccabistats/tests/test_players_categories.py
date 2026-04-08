"""Tests for MaccabiGamesPlayersCategoriesStats.

This module depends on MaccabiPediaPlayers which crawls the live API.
We mock it to define which players are "home players" for testing.
We declare אבי נמני and אלי דריקס as "home players".
"""
from sys import maxsize
from unittest.mock import patch

import pytest

from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats

from game_fixtures import GAMES

HOME_PLAYER_NAMES = {"אבי נמני", "אלי דריקס"}


@pytest.fixture
def games_with_home_players():
    """Fresh MaccabiGamesStats with mocked home players data."""
    mock_data = type('MockPlayersData', (), {'home_players': HOME_PLAYER_NAMES})()

    with patch('maccabistats.stats.players_categories.MaccabiPediaPlayers') as mock_cls:
        mock_cls.get_players_data.return_value = mock_data
        stats = MaccabiGamesStats(GAMES)
        yield stats


class TestPlayersCategoriesStats:
    def test_home_players_goals_count(self, games_with_home_players):
        # אבי נמני: 8 goals, אלי דריקס: 2 goals = 10 home player goals
        assert games_with_home_players.players_categories.home_players_goals_count() == 10

    def test_home_players_goals_ratio(self, games_with_home_players):
        # 10 home / (10 home + 2 non-home) = 0.833
        assert games_with_home_players.players_categories.home_players_goals_ratio() == 0.833

    def test_home_players_assists_count(self, games_with_home_players):
        # Neither אבי נמני nor אלי דריקס have assists; חיים רביבו (non-home) has all 8
        assert games_with_home_players.players_categories.home_players_assists_count() == 0

    def test_home_players_assists_ratio(self, games_with_home_players):
        # 0 home / (0 + 8) = 0.0
        assert games_with_home_players.players_categories.home_players_assists_ratio() == 0.0

    def test_home_players_goals_involved_count(self, games_with_home_players):
        # Goals involved = goals + assists: home = 10 + 0 = 10
        assert games_with_home_players.players_categories.home_players_goals_involved_count() == 10

    def test_home_players_goals_involved_ratio(self, games_with_home_players):
        # 10 home / (10 home + 10 non-home) = 0.5
        assert games_with_home_players.players_categories.home_players_goals_involved_ratio() == 0.5


class TestPlayersCategoriesEdgeCases:
    def test_ratio_when_no_goals(self):
        """When no goals scored, ratio should be maxsize."""
        from game_fixtures import _game, _player, _lineup, TeamInGame
        import datetime

        game = _game(
            competition="ליגת העל", fixture="מחזור1", season="2020/21",
            date=datetime.datetime(2020, 1, 1),
            stadium="s", referee="r",
            home_team=TeamInGame("מכבי תל אביב", "c", 0, [
                _player("home_player", 1, [_lineup()]),
            ]),
            away_team=TeamInGame("opp", "c2", 0, [
                _player("o", 1, [_lineup()]),
            ]),
        )

        mock_data = type('MockPlayersData', (), {'home_players': {'home_player'}})()
        with patch('maccabistats.stats.players_categories.MaccabiPediaPlayers') as mock_cls:
            mock_cls.get_players_data.return_value = mock_data
            stats = MaccabiGamesStats([game])
            assert stats.players_categories.home_players_goals_ratio() == maxsize
