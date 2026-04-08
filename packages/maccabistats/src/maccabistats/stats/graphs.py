from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats

import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from collections import Counter


class MaccabiGamesGraphsStats(object):
    """
    This class will handle all the graphs for maccabi games stats
    """

    def __init__(self, maccabi_games_stats: MaccabiGamesStats):
        self.maccabi_games_stats = maccabi_games_stats

    @staticmethod
    def _show_histogram_of_this_counter(data_counter) -> None:
        x, y = zip(*sorted(data_counter.items()))
        plt.plot(x, y)
        plt.show()

    @staticmethod
    def _show_bar_charts_of_this_counter(data_counter) -> None:
        x, y = zip(*sorted(data_counter.items()))
        plt.bar(x, y, width=0.5)
        plt.xticks(x)
        plt.show()

    def _get_all_goals_minutes_for_player(self, player_name: str):
        player_goals = [goal for game in self.maccabi_games_stats.games for goal in game.goals() if
                        goal['name'] == player_name]

        def convert_timedelta_str_to_minutes(t):
            full_datetime = datetime.strptime(t, "%H:%M:%S")
            delta = timedelta(hours=full_datetime.hour, minutes=full_datetime.minute)
            return int(delta.total_seconds() / 60)

        player_goals = [convert_timedelta_str_to_minutes(goal['time_occur']) for goal in player_goals]
        if not player_goals:
            raise RuntimeError(
                "Could not find any goals for this player, are you sure this is the player name : {name}?".format(
                    name=player_name))

        return player_goals

    def goals_distribution_for_player(self, player_name: str) -> Counter:
        """
        Return ths distribution of the given player goals by minutes
        """
        return Counter(self._get_all_goals_minutes_for_player(player_name))

    def show_histogram_for_player_goals(self, player_name) -> Counter:
        goals = self.goals_distribution_for_player(player_name)

        self._show_histogram_of_this_counter(goals)
        return goals

    def show_bar_chart_for_player_goals_by_thirds(self, player_name) -> Counter:
        """
        Show bar charts of player goals by thirds (0-30, 30-60, 60-90, 90-120)
        """

        all_goals_by_thirds = [int(goal_minute / 30) for goal_minute in
                               self._get_all_goals_minutes_for_player(player_name)]
        goals_by_thirds = Counter(all_goals_by_thirds)

        self._show_bar_charts_of_this_counter(goals_by_thirds)
        return goals_by_thirds
