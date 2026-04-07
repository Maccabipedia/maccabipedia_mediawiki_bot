from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats

from sys import maxsize


class MaccabiGamesResultsStats(object):
    """
    This class will handle all results statistics.
    """

    def __init__(self, maccabi_games_stats: MaccabiGamesStats):
        self.games = maccabi_games_stats.games

    @property
    def total_goals_against_maccabi(self) -> int:
        return sum([game.not_maccabi_team.score for game in self.games])

    @property
    def total_goals_for_maccabi(self) -> int:
        return sum([game.maccabi_score for game in self.games])

    @property
    def total_goals_diff_for_maccabi(self) -> int:
        return self.total_goals_for_maccabi - self.total_goals_against_maccabi

    @property
    def goals_ratio(self) -> float:
        """
        Goals for maccabi / Goals against maccabi
        """
        if self.total_goals_against_maccabi == 0:
            return maxsize

        return round(self.total_goals_for_maccabi / self.total_goals_against_maccabi, 3)

    @property
    def total_games_count(self) -> int:
        return len(self.games)

    @property
    def wins_count(self) -> int:
        return len([game for game in self.games if game.is_maccabi_win])

    @property
    def wins_percentage(self) -> float:
        if len(self.games) == 0:
            return maxsize

        return round(self.wins_count / len(self.games), 3)

    @property
    def losses_count(self) -> int:
        return len([game for game in self.games if game.maccabi_score_diff < 0])

    @property
    def losses_percentage(self) -> float:
        if len(self.games) == 0:
            return maxsize

        return round(self.losses_count / len(self.games), 3)

    @property
    def ties_count(self) -> int:
        return len([game for game in self.games if game.maccabi_score_diff == 0])

    @property
    def ties_percentage(self) -> float:
        if len(self.games) == 0:
            return maxsize

        return round(self.ties_count / len(self.games), 3)

    @property
    def clean_sheets_count(self) -> int:
        return len([game for game in self.games if game.not_maccabi_team.score == 0])

    @property
    def clean_sheets_percentage(self) -> float:
        if len(self.games) == 0:
            return maxsize

        return round(self.clean_sheets_count / len(self.games), 3)

    def json_dict(self) -> Dict[str, Any]:
        return dict(total_games_count=self.total_games_count,
                    wins_count=self.wins_count,
                    losses_count=self.losses_count,
                    ties_count=self.ties_count,
                    clean_sheets_count=self.clean_sheets_count,
                    wins_percentage=self.wins_percentage,
                    losses_percentage=self.losses_percentage,
                    ties_percentage=self.ties_percentage,
                    clean_sheets_percentage=self.clean_sheets_percentage,
                    total_goals_for_maccabi=self.total_goals_for_maccabi,
                    total_goals_against_maccabi=self.total_goals_against_maccabi,
                    total_goals_diff_for_maccabi=self.total_goals_diff_for_maccabi,
                    goals_ratio=self.goals_ratio
                    )
