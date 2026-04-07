from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Tuple, List, Optional

from maccabistats.models.game_data import GameData

if TYPE_CHECKING:
    from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats

_ZERO_TIME = datetime.strptime("0:00:00", "%H:%M:%S")
_TOP_GAMES_NUMBER = 5

GameGoalTiming = Tuple[GameData, int]  # The game and the time it took to score the required goals number


class MaccabiGamesGoalsTiming(object):
    """
    This class will handle all goals timing statistics.
    """

    def __init__(self, maccabi_games_stats: MaccabiGamesStats):
        self.maccabi_games_stats = maccabi_games_stats
        self.games = maccabi_games_stats.games

    def fastest_two_goals(self, top_games_number=_TOP_GAMES_NUMBER) -> List[GameGoalTiming]:
        return self._top_games_with_minimum_goals_time_frame(2)[:top_games_number]

    def fastest_three_goals(self, top_games_number=_TOP_GAMES_NUMBER) -> List[GameGoalTiming]:
        return self._top_games_with_minimum_goals_time_frame(3)[:top_games_number]

    def fastest_four_goals(self, top_games_number=_TOP_GAMES_NUMBER) -> List[GameGoalTiming]:
        return self._top_games_with_minimum_goals_time_frame(4)[:top_games_number]

    def _top_games_with_minimum_goals_time_frame(self, goals_number: int) -> List[GameGoalTiming]:
        games_with_enough_goals = [game for game in self.maccabi_games_stats if game.maccabi_score >= goals_number]

        games_goals_timings = [(game, _minimum_goals_time_frame_for_a_game(game, goals_number)) for game in
                               games_with_enough_goals]
        games_goals_timings_without_errors = [item for item in games_goals_timings if item[1] is not None]

        return sorted(games_goals_timings_without_errors, key=lambda item: item[1])


def _maccabi_goals_minutes_for_game(goals):
    minutes = []

    for current_goal in goals:
        goal_time = datetime.strptime(current_goal['time_occur'], "%H:%M:%S") - _ZERO_TIME
        minutes.append(int(goal_time.total_seconds() / 60))

    return minutes


def _minimum_goals_time_frame_for_a_game(maccabi_game: GameData, goals_number: int) -> Optional[int]:
    maccabi_goals_time = _maccabi_goals_minutes_for_game(maccabi_game.maccabi_goals())

    # We might miss some data on the actual scorers and time (even if we have the final result)
    if len(maccabi_goals_time) < goals_number:
        return None

    return min([maccabi_goals_time[i + goals_number - 1] - maccabi_goals_time[i] for i in
                range(len(maccabi_goals_time) - goals_number + 1)])
