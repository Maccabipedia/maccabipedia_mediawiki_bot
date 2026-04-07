from __future__ import annotations

import logging
from itertools import chain
from typing import TYPE_CHECKING

from maccabistats.models.game_data import GameData
from maccabistats.models.player_game_events import GoalTypes

if TYPE_CHECKING:
    from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats

logger = logging.getLogger(__name__)


class MaccabiGamesComebacksStats(object):
    """
    This class will handle all comebacks statistics.
    """

    def __init__(self, maccabi_games_stats: MaccabiGamesStats) -> None:
        self.maccabi_games_stats = maccabi_games_stats
        self.games = maccabi_games_stats.games

    def won_from_exactly_one_goal_diff(self) -> MaccabiGamesStats:
        return self.won_from_exactly_x_goal_diff(1)

    def won_from_exactly_two_goal_diff(self) -> MaccabiGamesStats:
        return self.won_from_exactly_x_goal_diff(2)

    def won_from_exactly_x_goal_diff(self, winning_comeback_from_x_goals_disadvantage: int) -> MaccabiGamesStats:
        """
        Find the games which maccabi won them after was ahead by x goals (x=goals param).
        :param winning_comeback_from_x_goals_disadvantage: The number of goals advantage of the opponent.
        """

        # Opponent advantage should be negative, positive advantage means maccabi won.
        winning_comeback_from_x_goals_disadvantage *= -1

        crazy_maccabi_comebacks = []
        for game in self.games:
            if not game.is_maccabi_win:
                continue

            if self._conditions_for_winning_comeback_occur(game, winning_comeback_from_x_goals_disadvantage):
                crazy_maccabi_comebacks.append(game)

        return self.maccabi_games_stats.create_maccabi_stats_from_games(crazy_maccabi_comebacks)

    @property
    def total_comebacks_count(self) -> int:
        # TODO - count in one loop over games,
        # Fix this class - Comeback from 2 goals should count comeback from 1 goal as well
        return len(self.won_from_any_goal_diff())

    def won_from_any_goal_diff(self) -> MaccabiGamesStats:
        all_comebacks = [self.won_from_exactly_x_goal_diff(1),
                         self.won_from_exactly_x_goal_diff(2),
                         self.won_from_exactly_x_goal_diff(3),
                         self.won_from_exactly_x_goal_diff(4),
                         self.won_from_exactly_x_goal_diff(5)]

        return self.maccabi_games_stats.create_maccabi_stats_from_games(list(chain.from_iterable(all_comebacks)))

    def _conditions_for_winning_comeback_occur(self, game: GameData,
                                               winning_comeback_from_x_goals_disadvantage: int) -> bool:
        """
        Check whether the conditions for winning comeback exists in this game:
            * The total score should be at least as twice as the diff, +1 (for winning).
            * The opponent score should be at least the goals diff to check for.

        :param game: the game to check errors in.
        :param winning_comeback_from_x_goals_disadvantage: the goal diff to come from.
        """

        if not self._max_opponent_goals_advantage(game) == winning_comeback_from_x_goals_disadvantage:
            return False

        total_score = game.maccabi_team.score + game.not_maccabi_team.score
        if total_score < (2 * abs(winning_comeback_from_x_goals_disadvantage)) + 1:
            return False

        if game.not_maccabi_team.score < abs(winning_comeback_from_x_goals_disadvantage):
            return False

        return True

    def tie_from_exactly_one_goal_diff(self) -> MaccabiGamesStats:
        return self.tie_from_exactly_x_goal_diff(1)

    def tie_from_exactly_two_goal_diff(self) -> MaccabiGamesStats:
        return self.tie_from_exactly_x_goal_diff(2)

    def tie_from_exactly_x_goal_diff(self, tie_comeback_from_x_goals_disadvantage: int) -> MaccabiGamesStats:
        """
        Finds the games which maccabi ends with same score as opponent after was ahead by x goals (x=goals param).
        :param tie_comeback_from_x_goals_disadvantage: The number of goals advantage of the opponent.
        """

        # Opponent advantage should be negative, positive advantage means maccabi won.
        tie_comeback_from_x_goals_disadvantage *= -1

        crazy_maccabi_comebacks = []
        for game in self.games:
            if not game.maccabi_score_diff == 0:
                continue

            if self._conditions_for_tie_comeback_occur(game, tie_comeback_from_x_goals_disadvantage):
                crazy_maccabi_comebacks.append(game)

        return self.maccabi_games_stats.create_maccabi_stats_from_games(crazy_maccabi_comebacks)

    def games_with_potential_comebacks(self) -> MaccabiGamesStats:
        """
        Return a list of games that Maccabi could have comebacks at
        """
        return self.maccabi_games_stats.create_maccabi_stats_from_games(
            [game for game in self.games if self._max_opponent_goals_advantage(game) < -1])

    def games_with_potential_comebacks_that_maccabi_didnt_win(self) -> MaccabiGamesStats:
        """
        Return a list of games that Maccabi could have comebacks at
        """
        return self.maccabi_games_stats.create_maccabi_stats_from_games(
            [game for game in self.games if self._max_opponent_goals_advantage(game) < -1 and not game.is_maccabi_win])

    def _conditions_for_tie_comeback_occur(self, game: GameData, tie_comeback_from_x_goals_disadvantage: int) -> bool:
        """
        Check whether the conditions for tie comeback exists in this game:
            * The total score should be at least as twice as the diff.
            * The opponent score should be at least the goals diff to check for.

        :param game: the game to check errors in.
        :param tie_comeback_from_x_goals_disadvantage: the goal diff to come from.
        """

        if not self._max_opponent_goals_advantage(game) == tie_comeback_from_x_goals_disadvantage:
            return False

        total_score = game.maccabi_team.score + game.not_maccabi_team.score
        if total_score < 2 * abs(tie_comeback_from_x_goals_disadvantage):
            return False

        if game.not_maccabi_team.score < abs(tie_comeback_from_x_goals_disadvantage):
            return False

        return True

    @staticmethod
    def _max_opponent_goals_advantage(game: GameData) -> int:
        """
        Calc and return the max goals advantage for maccabi opponent for the given game.

        Examples:
            Maccabi (3) - (1) Opponent -> advantage=  2
            Maccabi (1) - (2) Opponent -> advantage= -1
        """

        game_goals = game.goals()

        # We save list of all goals timeline and find the minimum (max advantage for opponent).
        goals_diff = [0]
        for goal in game_goals:
            next_goal_status = 1 if goal['team'] == 'מכבי תל אביב' else -1

            if 'goal_type' in goal and goal['goal_type'] == GoalTypes.OWN_GOAL.value:
                next_goal_status *= -1

            # We add the last status + new goal (1 for maccabi, -1 for opponent).
            goals_diff.append(goals_diff[-1] + next_goal_status)

        return min(goals_diff)
