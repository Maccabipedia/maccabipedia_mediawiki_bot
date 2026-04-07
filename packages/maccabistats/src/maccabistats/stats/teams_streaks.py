from __future__ import annotations

import logging
from collections import defaultdict
from typing import TYPE_CHECKING, Callable, Tuple, List, Dict

if TYPE_CHECKING:
    from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats

    TeamAndGames = Tuple[str, MaccabiGamesStats]

logger = logging.getLogger(__name__)


class MaccabiGamesTeamsStreaksStats(object):
    """
    This class will handle all teams streaks statistics.
    """

    def __init__(self, maccabi_games_stats: MaccabiGamesStats):
        self.maccabi_games_stats = maccabi_games_stats
        self.games = maccabi_games_stats.games

    def _get_team_streak_by_condition(self, streak_condition: Callable[[MaccabiGamesStats], MaccabiGamesStats],
                                      top_teams_count: int = 20) -> List[TeamAndGames]:
        """
        Creates a MaccabiGamesStats for each team, Then calculate the longest streak length

        :param streak_condition: Gets the Team's MaccabiGamesStats and return the streak as MaccabiGamesStats
        """
        teams_games = defaultdict(list)

        for game in self.games:
            teams_games[game.not_maccabi_team.current_name].append(game)

        teams_maccabi_games_stats: Dict[str, MaccabiGamesStats] = dict()
        for team_name in teams_games.keys():
            teams_maccabi_games_stats[team_name] = streak_condition(
                self.maccabi_games_stats.create_maccabi_stats_from_games(teams_games[team_name]))

        return sorted(teams_maccabi_games_stats.items(),
                      key=lambda team_name_to_games: len(team_name_to_games[1]), reverse=True)[:top_teams_count]

    # region Best team streak

    def get_teams_with_best_unbeaten_streak(self) -> List[TeamAndGames]:
        return self._get_team_streak_by_condition(lambda games: games.streaks.get_longest_unbeaten_streak_games())

    def get_teams_with_best_win_streak(self) -> List[TeamAndGames]:
        return self._get_team_streak_by_condition(lambda games: games.streaks.get_longest_wins_streak_games())

    def get_teams_with_best_ties_streak(self) -> List[TeamAndGames]:
        return self._get_team_streak_by_condition(lambda games: games.streaks.get_longest_ties_streak_games())

    def get_teams_with_best_losses_streak(self) -> List[TeamAndGames]:
        return self._get_team_streak_by_condition(lambda games: games.streaks.get_longest_losses_streak_games())

    def get_teams_with_best_maccabi_score_goal_streak(self) -> List[TeamAndGames]:
        return self._get_team_streak_by_condition(lambda games: games.streaks.get_longest_score_at_least_games(1))

    def get_teams_with_best_maccabi_score_at_least_goals_streak(self, goals_amount: int):
        """
        :param goals_amount: Goals amount that maccabi scored (at least)
        """
        return self._get_team_streak_by_condition(
            lambda games: games.streaks.get_longest_score_at_least_games(goals_amount))

    def get_teams_with_best_maccabi_score_no_goal_streak(self) -> List[TeamAndGames]:
        return self._get_team_streak_by_condition(lambda games: games.streaks.get_longest_score_exactly_games(0))

    def get_teams_with_best_maccabi_score_exactly_goals_streak(self, goals_amount: int):
        """
        :param goals_amount: Goals amount that maccabi scored (exactly)
        """
        return self._get_team_streak_by_condition(
            lambda games: games.streaks.get_longest_score_exactly_games(goals_amount))

    def get_teams_with_best_clean_sheets_streak(self) -> List[TeamAndGames]:
        return self._get_team_streak_by_condition(lambda games: games.streaks.get_longest_clean_sheet_games())

    def get_teams_with_best_scored_against_maccabi_not_more_than_streak(self, not_maccabi_score: int):
        return self._get_team_streak_by_condition(
            lambda games: games.streaks.get_longest_scored_against_maccabi_not_more_than_games(not_maccabi_score))

    # endregion

    # region Current team streaks

    def get_teams_with_current_unbeaten_streak(self) -> List[TeamAndGames]:
        return self._get_team_streak_by_condition(lambda games: games.streaks.get_current_unbeaten_streak())

    def get_teams_with_current_win_streak(self) -> List[TeamAndGames]:
        return self._get_team_streak_by_condition(lambda games: games.streaks.get_current_wins_streak())

    def get_teams_with_current_ties_streak(self) -> List[TeamAndGames]:
        return self._get_team_streak_by_condition(lambda games: games.streaks.get_current_ties_streak())

    def get_teams_with_current_losses_streak(self) -> List[TeamAndGames]:
        return self._get_team_streak_by_condition(lambda games: games.streaks.get_current_losses_streak())

    def get_teams_with_current_maccabi_score_goal_streak(self) -> List[TeamAndGames]:
        return self._get_team_streak_by_condition(lambda games: games.streaks.get_current_score_at_least_streak(1))

    def get_teams_with_current_maccabi_score_at_least_goals_streak(self, goals_amount: int):
        """
        :param goals_amount: Goals amount that maccabi scored (at least)
        """
        return self._get_team_streak_by_condition(
            lambda games: games.streaks.get_current_score_at_least_streak(goals_amount))

    def get_teams_with_current_maccabi_score_no_goal_streak(self) -> List[TeamAndGames]:
        return self._get_team_streak_by_condition(lambda games: games.streaks.get_current_score_exactly_streak(0))

    def get_teams_with_current_maccabi_score_exactly_goals_streak(self, goals_amount: int):
        """
        :param goals_amount: Goals amount that maccabi scored (exactly)
        """
        return self._get_team_streak_by_condition(
            lambda games: games.streaks.get_current_score_exactly_streak(goals_amount))

    def get_teams_with_current_clean_sheets_streak(self) -> List[TeamAndGames]:
        return self._get_team_streak_by_condition(lambda games: games.streaks.get_current_clean_sheet_streak())

    def get_teams_with_current_scored_against_maccabi_not_more_than_streak(self, not_maccabi_score: int):
        return self._get_team_streak_by_condition(
            lambda games: games.streaks.get_current_scored_against_maccabi_not_more_than_streak(not_maccabi_score))

    # endregion
