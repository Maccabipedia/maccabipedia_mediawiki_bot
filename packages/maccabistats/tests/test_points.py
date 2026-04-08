"""Tests for league points calculation."""
import datetime

import pytest

from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats


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
        # All games includes cup and friendly, points should raise
        with pytest.raises(TypeError, match="league games"):
            maccabi_games.points


class TestPointsPrePost1982:
    def test_pre_1982_gives_2_points_for_win(self):
        """Before Sep 25 1982, wins gave 2 points instead of 3."""
        from maccabistats.models.team_in_game import TeamInGame
        from maccabistats.models.player_in_game import PlayerInGame
        from maccabistats.models.player_game_events import GameEvent, GameEventTypes
        from maccabistats.models.game_data import GameData

        lineup = GameEvent(GameEventTypes.LINE_UP, datetime.timedelta(minutes=0))
        maccabi = TeamInGame("מכבי תל אביב", "coach", 2, [
            PlayerInGame("player", 1, [lineup]),
        ])
        opponent = TeamInGame("opponent", "coach_b", 0, [
            PlayerInGame("opp", 1, [lineup]),
        ])

        old_game = GameData(
            competition="ליגת העל", fixture="מחזור1",
            date_as_hebrew_string="", stadium="s", crowd="0",
            referee="ref", home_team=maccabi, away_team=opponent,
            season_string="1981/82", half_parsed_events=[],
            date=datetime.datetime(1982, 1, 1),
        )

        stats = MaccabiGamesStats([old_game])
        # Pre-1982: win = 2 points
        assert stats.points == 2
