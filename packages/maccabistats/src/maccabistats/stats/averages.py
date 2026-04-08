from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats


class MaccabiGamesAverageStats(object):
    """
    This class will handle all averages statistics.
    """

    def __init__(self, maccabi_games_stats: MaccabiGamesStats) -> None:
        self.games = maccabi_games_stats.games

    @staticmethod
    def _prettify_averages(average) -> float:
        return float("{0:.2f}".format(average))

    @property
    def goals_for_maccabi(self) -> float:
        return MaccabiGamesAverageStats._prettify_averages(
            sum(game.maccabi_score for game in self.games) / len(self.games))

    @property
    def goals_against_maccabi(self) -> float:
        return MaccabiGamesAverageStats._prettify_averages(
            sum(game.not_maccabi_team.score for game in self.games) / len(self.games))

    @property
    def maccabi_diff(self) -> float:
        return MaccabiGamesAverageStats._prettify_averages(
            sum(game.maccabi_score_diff for game in self.games) / len(self.games))
