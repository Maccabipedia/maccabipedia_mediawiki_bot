from __future__ import annotations

import logging
from pprint import pformat
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats

logger = logging.getLogger(__name__)

_TOP_PLAYERS_COUNT = 6


class MaccabiGamesSummary(object):
    """
    This class will handle stats summary
    """

    def __init__(self, maccabi_games_stats: MaccabiGamesStats):
        self.maccabi_games_stats = maccabi_games_stats

        self._streaks = self.maccabi_games_stats.streaks
        self._players = self.maccabi_games_stats.players
        self._players_streaks = self.maccabi_games_stats.players_streaks

    def show_summary(self) -> None:
        self._show_home_away_total_streaks()
        self._show_home_away_total_top_players()

    def _show_home_away_total_top_players(self) -> None:
        print("----------------------------------------------------\n### Overall top players:\n\n")
        self.show_top_players()

        print("----------------------------------------------------\n### Home games top players:\n\n")
        self.maccabi_games_stats.home_games.summary.show_top_players()

        print("----------------------------------------------------\n### Away games top players:\n\n")
        self.maccabi_games_stats.away_games.summary.show_top_players()

    def show_top_players(self) -> None:
        print(f'Top players stats:\n'
              f'Most played: {pformat(self._players.most_played[:_TOP_PLAYERS_COUNT])}\n'
              f'Best scorers: {pformat(self._players.best_scorers[:_TOP_PLAYERS_COUNT])}\n'
              f'Best assisters: {pformat(self._players.best_assisters[:_TOP_PLAYERS_COUNT])}\n'
              f'Most goals involved: {pformat(self._players.most_goals_involved[:_TOP_PLAYERS_COUNT])}\n'
              f'Top winners: {pformat(self._players.most_winners[:_TOP_PLAYERS_COUNT])}\n'
              f'Never lost: {pformat(self._players.never_lost()[:_TOP_PLAYERS_COUNT])}\n'
              f'\n\n'
              f''
              f'Top players streaks:\n'
              f'Best winning streak: {pformat(self._players_streaks.get_players_with_best_win_streak()[:_TOP_PLAYERS_COUNT])}\n'
              f'Current winning streak: {pformat(self._players_streaks.get_players_with_current_win_streak()[:_TOP_PLAYERS_COUNT])}\n'
              f'Best unbeaten streak: {pformat(self._players_streaks.get_players_with_best_unbeaten_streak()[:_TOP_PLAYERS_COUNT])}\n'
              f'Current unbeaten streak: {pformat(self._players_streaks.get_players_with_current_unbeaten_streak()[:_TOP_PLAYERS_COUNT])}\n'
              f'Best goal involved streak: {pformat(self._players_streaks.get_players_with_best_goal_involving_streak()[:_TOP_PLAYERS_COUNT])}\n'
              f'Current goal involved streak: {pformat(self._players_streaks.get_players_with_current_goal_involving_streak()[:_TOP_PLAYERS_COUNT])}\n'
              )

    def _show_home_away_total_streaks(self) -> None:
        """
        Prints the best streak in many conditions (each functions of this class),
        For each streak show any similar streaks (if exists)
        """
        print("----------------------------------------------------\n### Overall streaks:\n\n")
        self.show_streaks_information()

        print("----------------------------------------------------\n### Home games streaks:\n\n")
        self.maccabi_games_stats.home_games.summary.show_streaks_information()

        print("----------------------------------------------------\n### Away games streaks:\n\n")
        self.maccabi_games_stats.away_games.summary.show_streaks_information()

    def show_streaks_information(self) -> None:
        # TODO: this should be change to better way to design the streaks and the str\repr
        print(f"Longest streaks:\n"
              f"Wins streak: {self._streaks.get_longest_wins_streak_games()}\n"
              f"Similar wins streaks: {pformat(self._streaks.get_similar_wins_streak_by_length(len(self._streaks.get_longest_wins_streak_games())))})\n\n"
              f"Ties streak: {self._streaks.get_longest_ties_streak_games()}\n"
              f"Similar ties streaks: {pformat(self._streaks.get_similar_ties_streak_by_length(len(self._streaks.get_longest_ties_streak_games())))})\n\n"
              f"Losses streak: {self._streaks.get_longest_losses_streak_games()}\n"
              f"Similar ties streaks: {pformat(self._streaks.get_similar_losses_streak_by_length(len(self._streaks.get_longest_losses_streak_games())))})\n\n"
              f"Unbeaten streak: {self._streaks.get_longest_unbeaten_streak_games()}\n"
              f"Similar unbeaten streaks: {pformat(self._streaks.get_similar_unbeaten_streak_by_length(len(self._streaks.get_longest_unbeaten_streak_games())))})\n\n"
              f"Score goal streak: {self._streaks.get_longest_score_at_least_games(1)}\n"
              f"Similar score goal streaks: {pformat(self._streaks.get_similar_score_at_least_streak_by_length(1, len(self._streaks.get_longest_score_at_least_games(1))))})\n\n"
              f"No goal score streak: {self._streaks.get_longest_score_exactly_games(0)}\n"
              f"Similar no goal score streaks: {pformat(self._streaks.get_similar_score_exactly_streak_by_length(0, len(self._streaks.get_longest_score_exactly_games(0))))})\n\n"
              f"Clean sheet streak: {self._streaks.get_longest_clean_sheet_games()}\n"
              f"Similar Clean sheet streaks: {pformat(self._streaks.get_similar_clean_sheet_streak_by_length(len(self._streaks.get_longest_clean_sheet_games())))})\n\n"
              f"Goals from bench streak: {self._streaks.get_longest_goals_from_bench_games()}\n"
              f"Similar goals from bench streaks: {pformat(self._streaks.get_similar_goals_from_bench_streak_by_length(len(self._streaks.get_longest_goals_from_bench_games())))})\n\n"
              f"\n\nCurrent streaks:\n"
              f"Wins streak: {self._streaks.get_current_wins_streak()}\n"
              f"Ties streak: {self._streaks.get_current_ties_streak()}\n"
              f"Losses streak: {self._streaks.get_current_losses_streak()}\n"
              f"Unbeaten streak: {self._streaks.get_current_unbeaten_streak()}\n"
              f"Score goal streak: {self._streaks.get_current_score_at_least_streak(1)}\n"
              f"No goal score streak: {self._streaks.get_current_score_exactly_streak(0)}\n"
              f"Clean sheet streak: {self._streaks.get_current_clean_sheet_streak()}\n"
              f"Goals from bench streak: {self._streaks.get_current_goals_from_bench_streak()}\n"
              )

    def __repr__(self) -> str:
        return f'Summary for maccabi games stats, including {len(self.maccabi_games_stats)} games'
