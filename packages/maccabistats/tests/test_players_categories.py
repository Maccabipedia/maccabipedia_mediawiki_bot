"""Tests for MaccabiGamesPlayersCategoriesStats.

The players_data (home players list) is provided via the conftest fixture,
which declares אבי נמני and אלי דריקס as "home players".
"""
from collections import defaultdict
from datetime import datetime
from sys import maxsize

import pytest

from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats

from game_fixtures import GAMES


class TestPlayersCategoriesStats:
    def test_home_players_goals_count(self, maccabi_games):
        # אבי נמני: 8 goals, אלי דריקס: 2 goals = 10 home player goals
        assert maccabi_games.players_categories.home_players_goals_count() == 10

    def test_home_players_goals_ratio(self, maccabi_games):
        # 10 home / (10 home + 2 non-home) = 0.833
        assert maccabi_games.players_categories.home_players_goals_ratio() == 0.833

    def test_home_players_assists_count(self, maccabi_games):
        # Neither אבי נמני nor אלי דריקס have assists; חיים רביבו (non-home) has all 8
        assert maccabi_games.players_categories.home_players_assists_count() == 0

    def test_home_players_assists_ratio(self, maccabi_games):
        # 0 home / (0 + 8) = 0.0
        assert maccabi_games.players_categories.home_players_assists_ratio() == 0.0

    def test_home_players_goals_involved_count(self, maccabi_games):
        # Goals involved = goals + assists: home = 10 + 0 = 10
        assert maccabi_games.players_categories.home_players_goals_involved_count() == 10

    def test_home_players_goals_involved_ratio(self, maccabi_games):
        # 10 home / (10 home + 10 non-home) = 0.5
        assert maccabi_games.players_categories.home_players_goals_involved_ratio() == 0.5


class TestPlayersCategoriesEdgeCases:
    def test_ratio_when_no_goals(self):
        """When no goals scored, ratio should be maxsize."""
        from game_fixtures import _game, _player, _lineup, TeamInGame
        import datetime as dt

        game = _game(
            competition="ליגת העל", fixture="מחזור1", season="2020/21",
            date=dt.datetime(2020, 1, 1),
            stadium="s", referee="r",
            home_team=TeamInGame("מכבי תל אביב", "c", 0, [
                _player("home_player", 1, [_lineup()]),
            ]),
            away_team=TeamInGame("opp", "c2", 0, [
                _player("o", 1, [_lineup()]),
            ]),
        )

        mock_data = type('MockPlayersData', (), {
            'home_players': {'home_player'},
            'players_dates': defaultdict(lambda: datetime(1000, 1, 1)),
        })()
        stats = MaccabiGamesStats([game], players_data=mock_data)
        assert stats.players_categories.home_players_goals_ratio() == maxsize
