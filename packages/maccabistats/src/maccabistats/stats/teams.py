from __future__ import annotations

import logging
from collections import Counter, defaultdict
from typing import TYPE_CHECKING, Callable, Tuple, List, Optional

if TYPE_CHECKING:
    from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats

logger = logging.getLogger(__name__)

TeamStats = Tuple[str, float]


class MaccabiGamesTeamsStats(object):
    """
    This class will handle all teams statistics.
    """

    def __init__(self, maccabi_games_stats: MaccabiGamesStats):
        self.games = maccabi_games_stats.games
        self.maccabi_games_stats = maccabi_games_stats

    def __get_teams_sorted_by_most_of_this_condition(self,
                                                     condition: Callable[[MaccabiGamesStats], float],
                                                     top_teams_count: Optional[int] = None,
                                                     minimum_games_against_team: Optional[int] = 0) -> List[TeamStats]:
        """
        Return Counter.most_common() of all the teams sorted by the results of this condition (Should be number) Desc.
        the condition receive MaccabiGamesStats which include only games against one team.

        :param condition: Functions that gets a MaccabiGameStats with a specific team games and returns a rank (int)
        """
        teams_games = defaultdict(list)
        top_teams_count = top_teams_count or 20
        minimum_games_against_team = minimum_games_against_team or 0

        for game in self.games:
            teams_games[game.not_maccabi_team.current_name].append(game)

        teams_with_condition = {}
        for team_name in teams_games.keys():
            if len(teams_games[team_name]) >= minimum_games_against_team:
                teams_with_condition[team_name] = condition(
                    self.maccabi_games_stats.create_maccabi_stats_from_games(teams_games[team_name]))
            else:
                logger.debug(f"Ignoring {team_name} in this calculation, "
                             f"required games length is: {minimum_games_against_team}, "
                             f"team games length: {len(teams_games[team_name])}")

        return Counter(teams_with_condition).most_common()[:top_teams_count]

    def teams_ordered_by_maccabi_wins(self,
                                      top_teams_count: Optional[int] = None,
                                      minimum_games_against_team: Optional[int] = None) -> List[TeamStats]:
        return self.__get_teams_sorted_by_most_of_this_condition(lambda t: t.results.wins_count, top_teams_count,
                                                                 minimum_games_against_team)

    def teams_ordered_by_games_played(self,
                                      top_teams_count: Optional[int] = None,
                                      minimum_games_against_team: Optional[int] = None) -> List[TeamStats]:
        return self.__get_teams_sorted_by_most_of_this_condition(lambda t: t.results.total_games_count, top_teams_count,
                                                                 minimum_games_against_team)

    def teams_ordered_by_maccabi_wins_percentage(self, top_teams_count: Optional[int] = None,
                                                 minimum_games_against_team: Optional[int] = None) -> List[TeamStats]:
        return self.__get_teams_sorted_by_most_of_this_condition(lambda t: t.results.wins_percentage, top_teams_count,
                                                                 minimum_games_against_team)

    def teams_ordered_by_maccabi_losses(self, top_teams_count: Optional[int] = None,
                                        minimum_games_against_team: Optional[int] = None) -> List[TeamStats]:
        return self.__get_teams_sorted_by_most_of_this_condition(lambda t: t.results.losses_count, top_teams_count,
                                                                 minimum_games_against_team)

    def teams_ordered_by_maccabi_losses_percentage(self, top_teams_count: Optional[int] = None,
                                                   minimum_games_against_team: Optional[int] = None) -> List[TeamStats]:
        return self.__get_teams_sorted_by_most_of_this_condition(lambda t: t.results.losses_percentage, top_teams_count,
                                                                 minimum_games_against_team)

    def teams_ordered_by_wins_minus_losses(self, top_teams_count: Optional[int] = None,
                                           minimum_games_against_team: Optional[int] = None) -> List[TeamStats]:
        return self.__get_teams_sorted_by_most_of_this_condition(
            lambda t: t.results.wins_count - t.results.losses_count,
            top_teams_count, minimum_games_against_team)

    def teams_ordered_by_maccabi_ties(self, top_teams_count: Optional[int] = None,
                                      minimum_games_against_team: Optional[int] = None) -> List[TeamStats]:
        return self.__get_teams_sorted_by_most_of_this_condition(lambda t: t.results.ties_count, top_teams_count,
                                                                 minimum_games_against_team)

    def teams_ordered_by_maccabi_ties_percentage(self, top_teams_count: Optional[int] = None,
                                                 minimum_games_against_team: Optional[int] = None) -> List[TeamStats]:
        return self.__get_teams_sorted_by_most_of_this_condition(lambda t: t.results.ties_percentage, top_teams_count,
                                                                 minimum_games_against_team)

    def teams_ordered_by_maccabi_clean_sheets_count(
            self, top_teams_count: Optional[int] = None,
            minimum_games_against_team: Optional[int] = None) -> List[TeamStats]:
        return self.__get_teams_sorted_by_most_of_this_condition(lambda t: t.results.clean_sheets_count,
                                                                 top_teams_count, minimum_games_against_team)

    def teams_ordered_by_maccabi_clean_sheets_percentage(
            self, top_teams_count: Optional[int] = None,
            minimum_games_against_team: Optional[int] = None) -> List[TeamStats]:
        return self.__get_teams_sorted_by_most_of_this_condition(lambda t: t.results.clean_sheets_percentage,
                                                                 top_teams_count, minimum_games_against_team)

    def teams_ordered_by_goals_ratio(self, top_teams_count: Optional[int] = None,
                                     minimum_games_against_team: Optional[int] = None) -> List[TeamStats]:
        return self.__get_teams_sorted_by_most_of_this_condition(lambda t: t.results.goals_ratio, top_teams_count,
                                                                 minimum_games_against_team)

    def teams_ordered_by_goals_diff(self, top_teams_count: Optional[int] = None,
                                    minimum_games_against_team: Optional[int] = None) -> List[TeamStats]:
        return self.__get_teams_sorted_by_most_of_this_condition(lambda t: t.results.total_goals_diff_for_maccabi,
                                                                 top_teams_count, minimum_games_against_team)

    def teams_ordered_by_total_goals_for_maccabi(
            self, top_teams_count: Optional[int] = None,
            minimum_games_against_team: Optional[int] = None) -> List[TeamStats]:
        return self.__get_teams_sorted_by_most_of_this_condition(lambda t: t.results.total_goals_for_maccabi,
                                                                 top_teams_count, minimum_games_against_team)

    def teams_ordered_by_total_goals_against_maccabi(
            self, top_teams_count: Optional[int] = None,
            minimum_games_against_team: Optional[int] = None) -> List[TeamStats]:
        return self.__get_teams_sorted_by_most_of_this_condition(lambda t: t.results.total_goals_against_maccabi,
                                                                 top_teams_count, minimum_games_against_team)
