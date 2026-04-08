from __future__ import annotations

import logging
import pprint
from collections import OrderedDict
from typing import TYPE_CHECKING, Union, Any, Callable

if TYPE_CHECKING:
    from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats

logger = logging.getLogger(__name__)


class MaccabiGamesSeasonsStats:
    """
    This class is responsible for maccabi seasons manipulating, such as sorting by wins count, goals for maccabi and so on.

    The pattern for adding "sort_by" function is to add lambda which receive just the season maccabi games stats object,
    inside the function itself you should set the key with lambda that 'removes' the season string.
    example function - sort_by_wins_count.
    """

    def __init__(self, maccabi_games_stats: MaccabiGamesStats):
        self.maccabi_games_stats = maccabi_games_stats

        # In order to avoid recursion, when we face one season ony, don't create new MaccabiGamesStats object
        if len(self.maccabi_games_stats.available_seasons) == 1:
            self._seasons_dict = {self.maccabi_games_stats.available_seasons[0]: self.maccabi_games_stats}
        else:
            self._seasons_dict = {season: self.maccabi_games_stats.get_games_by_season(season) for season in
                                  self.maccabi_games_stats.available_seasons}

        # sort attribute use to show the relevant data after sorting.
        self._current_sort_attribute_function = str  # Use empty str as default sort
        self._current_sort_attribute_description = "order by season number"

    def __repr__(self) -> str:
        # Pad the season representation to 7 chars, like '2015/16', to have one year seasons aligned (like '1955')
        ordered_seasons = pprint.pformat([f'{season: <7} ({self._current_sort_attribute_function(self[season])})'
                                          for season in self._seasons_dict.keys()])

        return f'{self._current_sort_attribute_description}: \n\n{ordered_seasons}'

    def __getitem__(self, item: Union[int, str]) -> MaccabiGamesStats:
        """
        :param item: Allow to use ['1990-91'] or by indexing [0]
        """
        if isinstance(item, int):
            return list(self._seasons_dict.values())[item]
        else:
            return self._seasons_dict[item]

    def __len__(self) -> int:
        return len(self._seasons_dict)

    def _refresh_sorting(self,
                         sort_attribute_function: Callable[[MaccabiGamesStats], Any],
                         sort_attribute_description: str) -> None:
        """
        Updates the current seasons sorting by the given callable (gets MaccabiGamesStats with a seasons games)
        :param sort_attribute_function: The callable to sort the seasons by (gets season item - MaccabiGamesStats)
        :param sort_attribute_description: The description of this current sorting, will be shown on the repr
        """
        self._current_sort_attribute_function = sort_attribute_function
        self._current_sort_attribute_description = sort_attribute_description

        self._seasons_dict = OrderedDict(
            sorted(self._seasons_dict.items(), key=lambda item: self._current_sort_attribute_function(item[1]),
                   reverse=True))

    # region Games Results
    def sort_by_games_count(self) -> None:
        self._refresh_sorting(sort_attribute_function=lambda s: len(s),
                              sort_attribute_description="sort by games count")

    def sort_by_wins_count(self) -> None:
        self._refresh_sorting(sort_attribute_function=lambda s: s.results.wins_count,
                              sort_attribute_description="sort by wins count")

    def sort_by_wins_percentage(self) -> None:
        self._refresh_sorting(sort_attribute_function=lambda s: s.results.wins_percentage,
                              sort_attribute_description="sort by wins percentage")

    def sort_by_losses_count(self) -> None:
        self._refresh_sorting(sort_attribute_function=lambda s: s.results.losses_count,
                              sort_attribute_description="sort by losses count")

    def sort_by_losses_percentage(self) -> None:
        self._refresh_sorting(sort_attribute_function=lambda s: s.results.losses_percentage,
                              sort_attribute_description="sort by losses percentage")

    def sort_by_ties_count(self) -> None:
        self._refresh_sorting(sort_attribute_function=lambda s: s.results.ties_count,
                              sort_attribute_description="sort by ties count")

    def sort_by_ties_percentage(self) -> None:
        self._refresh_sorting(sort_attribute_function=lambda s: s.results.ties_percentage,
                              sort_attribute_description="sort by ties percentage")

    # endregion

    # region Goals manipulations:

    def sort_by_total_goals_diff(self) -> None:
        self._refresh_sorting(sort_attribute_function=lambda s: s.results.total_goals_diff_for_maccabi,
                              sort_attribute_description="sort by total goals diff for maccabi")

    def sort_by_average_goals_diff_per_game(self) -> None:
        self._refresh_sorting(sort_attribute_function=lambda s: s.averages.maccabi_diff,
                              sort_attribute_description="sort by average (per game) goal diff for maccabi")

    def sort_by_total_goals_for_maccabi(self) -> None:
        self._refresh_sorting(sort_attribute_function=lambda s: s.results.total_goals_for_maccabi,
                              sort_attribute_description="sort by total goals for maccabi")

    def sort_by_average_goals_for_maccabi_per_game(self) -> None:
        self._refresh_sorting(sort_attribute_function=lambda s: s.averages.goals_for_maccabi,
                              sort_attribute_description="sort by average goals (per game) for maccabi")

    def sort_by_total_goals_against_maccabi(self) -> None:
        self._refresh_sorting(sort_attribute_function=lambda s: s.results.total_goals_against_maccabi,
                              sort_attribute_description="sort by total goals against maccabi")

    def sort_by_average_goals_against_maccabi_per_game(self) -> None:
        self._refresh_sorting(sort_attribute_function=lambda s: s.averages.goals_against_maccabi,
                              sort_attribute_description="sort by average goals (per game) against maccabi")

    def sort_by_clean_sheet_count(self) -> None:
        self._refresh_sorting(sort_attribute_function=lambda s: s.results.clean_sheets_count,
                              sort_attribute_description="sort by clean sheets count")

    def sort_by_clean_sheet_percentage(self) -> None:
        self._refresh_sorting(sort_attribute_function=lambda s: s.results.clean_sheets_percentage,
                              sort_attribute_description="sort by clean sheets percentage")

    def sort_by_goals_ratio(self) -> None:
        """
        Goals for maccabi / Goals against maccabi
        """
        self._refresh_sorting(sort_attribute_function=lambda s: s.results.goals_ratio,
                              sort_attribute_description=
                              "sort by goals ratio (Goals for maccabi / Goals against maccabi)")

    def sort_by_home_players_goals_count(self) -> None:
        self._refresh_sorting(sort_attribute_function=lambda s: s.players_categories.home_players_goals_count(),
                              sort_attribute_description="sort by home players goals count")

    def sort_by_home_players_goals_ratio(self) -> None:
        self._refresh_sorting(sort_attribute_function=lambda s: s.players_categories.home_players_goals_ratio(),
                              sort_attribute_description="sort by home players goals ratio")

    def sort_by_home_players_assists_count(self) -> None:
        self._refresh_sorting(sort_attribute_function=lambda s: s.players_categories.home_players_assists_count(),
                              sort_attribute_description="sort by home players assists count")

    def sort_by_home_players_assists_ratio(self) -> None:
        self._refresh_sorting(sort_attribute_function=lambda s: s.players_categories.home_players_assists_ratio(),
                              sort_attribute_description="sort by home players assists ratio")

    def sort_by_home_players_goals_involved_count(self) -> None:
        self._refresh_sorting(
            sort_attribute_function=lambda s: s.players_categories.home_players_goals_involved_count(),
            sort_attribute_description="sort by home players goals involved count")

    def sort_by_home_players_goals_involved_ratio(self) -> None:
        self._refresh_sorting(
            sort_attribute_function=lambda s: s.players_categories.home_players_goals_involved_ratio(),
            sort_attribute_description="sort by home players goals involved ratio")

    def sort_by_captains_count(self) -> None:
        self._refresh_sorting(sort_attribute_function=lambda s: len(s.players.most_captains),
                              sort_attribute_description="sort by the number of different players that were captains")

    def sort_by_played_players_count(self) -> None:
        self._refresh_sorting(sort_attribute_function=lambda s: len(s.players.most_played),
                              sort_attribute_description="sort by the number of different players that played")

    def sort_by_scored_players_count(self) -> None:
        self._refresh_sorting(sort_attribute_function=lambda s: len(s.players.best_scorers),
                              sort_attribute_description="sort by the number of different players that scored")

    def sort_by_assisted_players_count(self) -> None:
        self._refresh_sorting(sort_attribute_function=lambda s: len(s.players.best_assisters),
                              sort_attribute_description="sort by the number of different players that assisted")

    def sort_by_goal_involved_players_count(self) -> None:
        self._refresh_sorting(sort_attribute_function=lambda s: len(s.players.most_goals_involved),
                              sort_attribute_description=
                              "sort by the number of different players that were involved in a goal")

    def sort_by_penalties_scorers_amount(self) -> None:
        self._refresh_sorting(sort_attribute_function=lambda s: len(s.players.best_scorers_by_penalty),
                              sort_attribute_description=
                              "sort by the number of different penalties scorers")

    def sort_by_comebacks_to_win_amount(self) -> None:
        self._refresh_sorting(sort_attribute_function=lambda s: len(s.comebacks.won_from_any_goal_diff()),
                              sort_attribute_description=
                              "sort by the number of comebacks to winning")

    def sort_by_potential_comebacks_that_maccabi_didnt_win(self) -> None:
        self._refresh_sorting(
            sort_attribute_function=lambda s: len(s.comebacks.games_with_potential_comebacks_that_maccabi_didnt_win()),
            sort_attribute_description=
            "sort by the number of potential comebacks that maccabi didn't win")
    # endregion
