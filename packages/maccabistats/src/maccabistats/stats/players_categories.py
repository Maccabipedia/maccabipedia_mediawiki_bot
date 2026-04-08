from __future__ import annotations

import logging
from collections import Counter
from sys import maxsize
from typing import Tuple, TYPE_CHECKING

from maccabistats.maccabipedia.players import MaccabiPediaPlayers

if TYPE_CHECKING:
    from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats

logger = logging.getLogger(__name__)


class MaccabiGamesPlayersCategoriesStats(object):
    """
    This class will handle the players categories stats.
    Players category are a group of players grouped by a condition, like: all home players.
    On this group we will ask some questions, like:
     * How many goals did they score? how much % of the goals did they score? and so on
    """

    def __init__(self, maccabi_games_stats: MaccabiGamesStats):
        self.maccabi_games_stats = maccabi_games_stats
        self.games = maccabi_games_stats.games
        self.maccabi_home_players_names = MaccabiPediaPlayers.get_players_data().home_players

    def _home_players_events(self, game_events_callable) -> Tuple[int, int]:
        """
        Calculate the events made by home player and by non home players.
        Use the given callable to choose which events to calculate

        :param game_events_callable: A callable that should return a counter,
               One of those as example: "scored_players_with_amount" and so on
        :return: The total goals from home players and total goals form non home players
        """
        total_home_players_events = 0
        total_non_home_players_events = 0

        goals_by_player_name = Counter()
        for game in self.maccabi_games_stats:
            goals_by_player_name += game_events_callable(game)

        for player_name, goals_count in goals_by_player_name.items():
            if player_name in self.maccabi_home_players_names:
                total_home_players_events += goals_count
            else:
                total_non_home_players_events += goals_count

        return total_home_players_events, total_non_home_players_events

    # home players scored

    def _home_players_goals_division(self) -> Tuple[int, int]:
        return self._home_players_events(game_events_callable=lambda game: game.maccabi_team.scored_players_with_amount)

    def home_players_goals_count(self) -> int:
        return self._home_players_goals_division()[0]

    def home_players_goals_ratio(self) -> float:
        home_players_goals, non_home_players_goals = self._home_players_goals_division()
        if home_players_goals + non_home_players_goals == 0:
            return maxsize

        return round(home_players_goals / (home_players_goals + non_home_players_goals), 3)

    # home players assists

    def _home_players_assists_division(self) -> Tuple[int, int]:
        return self._home_players_events(game_events_callable=lambda game: game.maccabi_team.assist_players_with_amount)

    def home_players_assists_count(self) -> int:
        return self._home_players_assists_division()[0]

    def home_players_assists_ratio(self) -> float:
        home_players_assists, non_home_players_assists = self._home_players_assists_division()

        if home_players_assists + non_home_players_assists == 0:
            return maxsize

        return round(home_players_assists / (home_players_assists + non_home_players_assists), 3)

    # home players goals involved

    def _home_players_goals_involved_division(self) -> Tuple[int, int]:
        return self._home_players_events(
            game_events_callable=lambda game: game.maccabi_team.goal_involved_players_with_amount)

    def home_players_goals_involved_count(self) -> int:
        return self._home_players_goals_involved_division()[0]

    def home_players_goals_involved_ratio(self) -> float:
        home_players_goals_involved, non_home_players_goals_involved = self._home_players_goals_involved_division()
        if home_players_goals_involved + non_home_players_goals_involved == 0:
            return maxsize

        return round(home_players_goals_involved / (home_players_goals_involved + non_home_players_goals_involved), 3)
