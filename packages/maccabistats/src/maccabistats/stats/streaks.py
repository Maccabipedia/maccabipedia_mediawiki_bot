from __future__ import annotations

from collections.abc import Callable
from itertools import groupby, takewhile
from typing import List, TYPE_CHECKING

from maccabistats.models.game_data import GameData

if TYPE_CHECKING:
    from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats


class MaccabiGamesStreaksStats(object):
    """
    This class will handle all streaks statistics.
    """

    def __init__(self, maccabi_games_stats: MaccabiGamesStats):
        self.maccabi_games_stats = maccabi_games_stats
        self.games = maccabi_games_stats.games

    # region Internal game filtering functions

    def _get_longest_streak_by_condition(self, condition: Callable[[GameData], bool]) -> MaccabiGamesStats:
        """
        :param condition: Function that gets a game and return bool regarding the condition being checked
        """
        games_fulfill_condition = [condition(game) for game in self.games]
        streak_by_condition = [len(list(streak_list)) for condition_fulfill, streak_list in
                               groupby(games_fulfill_condition) if condition_fulfill]

        if not streak_by_condition:  # In case were handling empty streak, just return empty list of games.
            return self.maccabi_games_stats.create_maccabi_stats_from_games([])

        max_streak_by_condition = max(streak_by_condition)

        games_before_streak = 0
        for condition_fulfill, streak_list in groupby(games_fulfill_condition):
            # Count only if condition is true, if we reach the max streak we should stop!
            current_results_length = len(list(streak_list))
            if condition_fulfill and max_streak_by_condition == current_results_length:
                break
            else:
                games_before_streak += current_results_length

        return self.maccabi_games_stats.create_maccabi_stats_from_games(
            self.games[games_before_streak: games_before_streak + max_streak_by_condition])

    def _get_similar_streaks(self, condition: Callable[[GameData], bool], minimum_streak_length: int = 0) \
            -> List[MaccabiGamesStats]:
        """
        :param condition: Function that gets a game and return bool regarding the condition being checked
        :param minimum_streak_length: the size of the minimum streak to search for.
        """
        games_fulfill_condition = [condition(game) for game in self.games]

        similar_streaks = []
        games_before_streak = 0

        for condition_fulfill, streak_list in groupby(games_fulfill_condition):
            # Count only if condition is true, if we reach the max streak we should stop!
            current_results_length = len(list(streak_list))
            if condition_fulfill and current_results_length >= minimum_streak_length:
                similar_streaks.append(self.maccabi_games_stats.create_maccabi_stats_from_games(
                    self.games[games_before_streak: games_before_streak + current_results_length]))

            games_before_streak += current_results_length

        return similar_streaks

    def _get_current_streak_by_condition(self, condition: Callable[[GameData], bool]) -> MaccabiGamesStats:
        """
        Returns the current streak of games which satisfies the condition

        :param condition: Function that gets a game and return bool regarding the condition being checked
        """
        current_streak = list(takewhile(condition, self.games[::-1]))
        return self.maccabi_games_stats.create_maccabi_stats_from_games(current_streak)

    # endregion

    # region Streak of game results

    def get_longest_wins_streak_games(self) -> MaccabiGamesStats:
        return self._get_longest_streak_by_condition(lambda g: g.is_maccabi_win)

    def get_similar_wins_streak_by_length(self, minimum_streak_length: int = 0) -> List[MaccabiGamesStats]:
        return self._get_similar_streaks(lambda g: g.is_maccabi_win, minimum_streak_length=minimum_streak_length)

    def get_current_wins_streak(self) -> MaccabiGamesStats:
        return self._get_current_streak_by_condition(lambda g: g.is_maccabi_win)

    def get_longest_ties_streak_games(self) -> MaccabiGamesStats:
        return self._get_longest_streak_by_condition(lambda g: g.maccabi_score_diff == 0)

    def get_similar_ties_streak_by_length(self, minimum_streak_length: int = 0) -> List[MaccabiGamesStats]:
        return self._get_similar_streaks(lambda g: g.maccabi_score_diff == 0,
                                         minimum_streak_length=minimum_streak_length)

    def get_current_ties_streak(self) -> MaccabiGamesStats:
        return self._get_current_streak_by_condition(lambda g: g.maccabi_score_diff == 0)

    def get_longest_losses_streak_games(self) -> MaccabiGamesStats:
        return self._get_longest_streak_by_condition(lambda g: g.maccabi_score_diff < 0)

    def get_similar_losses_streak_by_length(self, minimum_streak_length: int = 0) -> List[MaccabiGamesStats]:
        return self._get_similar_streaks(lambda g: g.maccabi_score_diff < 0,
                                         minimum_streak_length=minimum_streak_length)

    def get_similar_not_win_streak_by_length(self, minimum_streak_length: int = 0) -> List[MaccabiGamesStats]:
        return self._get_similar_streaks(lambda g: g.maccabi_score_diff <= 0,
                                         minimum_streak_length=minimum_streak_length)

    def get_current_losses_streak(self) -> MaccabiGamesStats:
        return self._get_current_streak_by_condition(lambda g: g.maccabi_score_diff < 0)

    # endregion

    def get_longest_unbeaten_streak_games(self) -> MaccabiGamesStats:
        return self._get_longest_streak_by_condition(lambda g: g.maccabi_score_diff >= 0)

    def get_similar_unbeaten_streak_by_length(self, minimum_streak_length: int = 0) -> List[MaccabiGamesStats]:
        return self._get_similar_streaks(lambda g: g.maccabi_score_diff >= 0,
                                         minimum_streak_length=minimum_streak_length)

    def get_current_unbeaten_streak(self) -> MaccabiGamesStats:
        return self._get_current_streak_by_condition(lambda g: g.maccabi_score_diff >= 0)

    def get_longest_score_at_least_games(self, minimum_maccabi_score) -> MaccabiGamesStats:
        return self._get_longest_streak_by_condition(lambda g: g.maccabi_score >= minimum_maccabi_score)

    def get_similar_score_at_least_streak_by_length(self, minimum_maccabi_score: int, minimum_streak_length: int = 0) \
            -> List[MaccabiGamesStats]:
        return self._get_similar_streaks(lambda g: g.maccabi_score >= minimum_maccabi_score,
                                         minimum_streak_length=minimum_streak_length)

    def get_current_score_at_least_streak(self, minimum_maccabi_score) -> MaccabiGamesStats:
        return self._get_current_streak_by_condition(lambda g: g.maccabi_score >= minimum_maccabi_score)

    def get_longest_score_exactly_games(self, maccabi_score) -> MaccabiGamesStats:
        return self._get_longest_streak_by_condition(lambda g: g.maccabi_score == maccabi_score)

    def get_current_score_exactly_streak(self, maccabi_score) -> MaccabiGamesStats:
        return self._get_current_streak_by_condition(lambda g: g.maccabi_score == maccabi_score)

    def get_similar_score_exactly_streak_by_length(self, maccabi_score: int, minimum_streak_length: int = 0) \
            -> List[MaccabiGamesStats]:
        return self._get_similar_streaks(lambda g: g.maccabi_score == maccabi_score,
                                         minimum_streak_length=minimum_streak_length)

    def get_longest_score_diff_at_least_games(self, minimum_maccabi_score_diff: int) -> MaccabiGamesStats:
        return self._get_longest_streak_by_condition(lambda g: g.maccabi_score_diff >= minimum_maccabi_score_diff)

    def get_similar_score_diff_at_least_streak_by_length(self, minimum_maccabi_score_diff: int,
                                                         minimum_streak_length: int = 0) -> List[MaccabiGamesStats]:
        return self._get_similar_streaks(lambda g: g.maccabi_score_diff >= minimum_maccabi_score_diff,
                                         minimum_streak_length=minimum_streak_length)

    def get_current_score_diff_at_least_streak(self, minimum_maccabi_score_diff: int) -> MaccabiGamesStats:
        return self._get_current_streak_by_condition(lambda g: g.maccabi_score_diff >= minimum_maccabi_score_diff)

    def get_longest_score_diff_exactly_games(self, maccabi_score_diff: int) -> MaccabiGamesStats:
        return self._get_longest_streak_by_condition(lambda g: g.maccabi_score_diff == maccabi_score_diff)

    def get_similar_score_diff_exactly_streak_by_length(self, maccabi_score_diff: int,
                                                        minimum_streak_length: int = 0) -> List[MaccabiGamesStats]:
        return self._get_similar_streaks(lambda g: g.maccabi_score_diff == maccabi_score_diff,
                                         minimum_streak_length=minimum_streak_length)

    def get_current_score_diff_exactly_streak(self, maccabi_score_diff: int) -> MaccabiGamesStats:
        return self._get_current_streak_by_condition(lambda g: g.maccabi_score_diff == maccabi_score_diff)

    def get_longest_clean_sheet_games(self) -> MaccabiGamesStats:
        return self._get_longest_streak_by_condition(lambda g: g.not_maccabi_team.score == 0)

    def get_similar_clean_sheet_streak_by_length(self, minimum_streak_length: int = 0) -> List[MaccabiGamesStats]:
        return self._get_similar_streaks(lambda g: g.not_maccabi_team.score == 0,
                                         minimum_streak_length=minimum_streak_length)

    def get_current_clean_sheet_streak(self) -> MaccabiGamesStats:
        return self._get_current_streak_by_condition(lambda g: g.not_maccabi_team.score == 0)

    def get_longest_scored_against_maccabi_not_more_than_games(self, not_maccabi_score: int) -> MaccabiGamesStats:
        return self._get_longest_streak_by_condition(lambda g: g.not_maccabi_team.score <= not_maccabi_score)

    def get_similar_scored_against_maccabi_not_more_than_streak_by_length(
            self, not_maccabi_score: int, minimum_streak_length: int = 0) -> List[MaccabiGamesStats]:
        return self._get_similar_streaks(lambda g: g.not_maccabi_team.score <= not_maccabi_score,
                                         minimum_streak_length=minimum_streak_length)

    def get_current_scored_against_maccabi_not_more_than_streak(self, not_maccabi_score: int) -> MaccabiGamesStats:
        return self._get_current_streak_by_condition(lambda g: g.not_maccabi_team.score <= not_maccabi_score)

    def get_longest_goals_from_bench_games(self) -> MaccabiGamesStats:
        return self._get_longest_streak_by_condition(lambda g: g.maccabi_team.has_goal_from_bench)

    def get_similar_goals_from_bench_streak_by_length(self, minimum_streak_length: int = 0) -> List[MaccabiGamesStats]:
        return self._get_similar_streaks(lambda g: g.maccabi_team.has_goal_from_bench,
                                         minimum_streak_length=minimum_streak_length)

    def get_current_goals_from_bench_streak(self) -> MaccabiGamesStats:
        return self._get_current_streak_by_condition(lambda g: g.maccabi_team.has_goal_from_bench)

    def get_longest_player_played_in_game(self, player_name: str) -> MaccabiGamesStats:
        return self._get_longest_streak_by_condition(lambda g: player_name in g.maccabi_team.played_players_with_amount)

    def get_similar_player_played_in_game_streak_by_length(self, player_name: int,
                                                           minimum_streak_length: int = 0) -> List[MaccabiGamesStats]:
        return self._get_similar_streaks(lambda g: player_name in g.maccabi_team.played_players_with_amount,
                                         minimum_streak_length=minimum_streak_length)

    def get_current_player_played_in_game_streak(self, player_name: str) -> MaccabiGamesStats:
        return self._get_current_streak_by_condition(lambda g: player_name in g.maccabi_team.played_players_with_amount)
