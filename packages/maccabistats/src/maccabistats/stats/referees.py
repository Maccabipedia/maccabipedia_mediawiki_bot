from __future__ import annotations

import typing
from typing import TYPE_CHECKING, Tuple, List

if TYPE_CHECKING:
    from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats

from collections import Counter

RefereeStats = Tuple[str, int]  # Referee name to the current stat (an int ranking)
RefereePercentageStats = Tuple[str, float]  # Referee name to the current stat percentage (float)


class MaccabiGamesRefereesStats(object):
    """
    This class will handle all referees statistics.
    """

    def __init__(self, maccabi_games_stats: MaccabiGamesStats) -> None:
        self.games = maccabi_games_stats.games

    @property
    def most_judged_referee(self) -> List[RefereeStats]:
        return Counter(game.referee for game in self.games).most_common()

    @property
    def best_referee(self) -> List[RefereeStats]:
        return Counter(game.referee for game in self.games if game.is_maccabi_win).most_common()

    @property
    def worst_referee(self) -> List[RefereeStats]:
        return Counter(game.referee for game in self.games if game.maccabi_score_diff < 0).most_common()

    @property
    def best_referee_by_percentage(self) -> List[RefereePercentageStats]:
        # Both return as Counter.most_common() which is list (of tuples)
        judged_games = Counter(dict(self.most_judged_referee))
        games_won_with_referees = Counter(dict(self.best_referee))

        best_referee: typing.Counter[str] = Counter()
        for referee_name, judged_times in judged_games.items():
            key_name = "{referee} - {judged}".format(referee=referee_name, judged=judged_times)
            best_referee[key_name] = round(games_won_with_referees[referee_name] / judged_times * 100, 2)

        return best_referee.most_common()

    @property
    def worst_referee_by_percentage(self) -> List[RefereePercentageStats]:
        # Both return as Counter.most_common() which is list (of tuples)
        judged_games = Counter(dict(self.most_judged_referee))
        games_lost_with_referees = Counter(dict(self.worst_referee))

        best_referee: typing.Counter[str] = Counter()
        for referee_name, judged_times in judged_games.items():
            key_name = "{referee} - {judged}".format(referee=referee_name, judged=judged_times)
            best_referee[key_name] = round(games_lost_with_referees[referee_name] / judged_times * 100, 2)

        return best_referee.most_common()
