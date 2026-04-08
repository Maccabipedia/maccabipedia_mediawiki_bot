"""Tests for MaccabiGamesPlayersCategoriesStats.

This module depends on MaccabiPediaPlayers which crawls the live API.
We mock it to define which players are "home players" for testing.
"""
from sys import maxsize
from unittest.mock import patch, PropertyMock

import pytest

from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats

from game_fixtures import GAMES


@pytest.fixture
def games_with_home_players():
    """Fresh MaccabiGamesStats with mocked home players data.

    We declare the first two players in the fixture as "home players"
    and the rest as foreign, so we can test the ratio calculations.
    """
    # Read actual player names from the fixture to stay in sync
    first_game = GAMES[0]
    all_player_names = {p.name for g in GAMES for p in g.maccabi_team.players}
    maccabi_players = list(first_game.maccabi_team.players)
    home_player_names = {maccabi_players[0].name, maccabi_players[1].name}

    mock_players_data = type('MockPlayersData', (), {
        'home_players': home_player_names,
    })()

    with patch('maccabistats.stats.players_categories.MaccabiPediaPlayers') as mock_cls:
        mock_cls.get_players_data.return_value = mock_players_data
        stats = MaccabiGamesStats(GAMES)
        yield stats, home_player_names


class TestPlayersCategoriesStats:
    def test_home_players_goals_count(self, games_with_home_players):
        stats, home_names = games_with_home_players
        count = stats.players_categories.home_players_goals_count()
        assert isinstance(count, int)
        assert count >= 0

    def test_home_players_goals_ratio(self, games_with_home_players):
        stats, home_names = games_with_home_players
        ratio = stats.players_categories.home_players_goals_ratio()
        assert 0 <= ratio <= 1

    def test_home_players_assists_count(self, games_with_home_players):
        stats, home_names = games_with_home_players
        count = stats.players_categories.home_players_assists_count()
        assert isinstance(count, int)

    def test_home_players_assists_ratio(self, games_with_home_players):
        stats, home_names = games_with_home_players
        ratio = stats.players_categories.home_players_assists_ratio()
        assert 0 <= ratio <= 1

    def test_home_players_goals_involved_count(self, games_with_home_players):
        stats, home_names = games_with_home_players
        count = stats.players_categories.home_players_goals_involved_count()
        assert isinstance(count, int)

    def test_home_players_goals_involved_ratio(self, games_with_home_players):
        stats, home_names = games_with_home_players
        ratio = stats.players_categories.home_players_goals_involved_ratio()
        assert 0 <= ratio <= 1


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
