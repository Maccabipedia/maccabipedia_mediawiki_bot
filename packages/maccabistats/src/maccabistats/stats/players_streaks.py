from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Callable, Tuple, List

from progressbar import ProgressBar

from .players_games_condition import PlayerGamesCondition

if TYPE_CHECKING:
    from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats

    PlayerAndGames = Tuple[str, MaccabiGamesStats]

logger = logging.getLogger(__name__)


class MaccabiGamesPlayersStreaksStats(object):
    """
    This class will handle all players streaks statistics.

    Every streak in this class is calculated from the player PLAYED games only.
    The only stat that calculated from the entire games (including these the players didn't took part it) is:
    get_players_with_current_played_in_game_streak
    """

    def __init__(self, maccabi_games_stats: MaccabiGamesStats):
        self.maccabi_games_stats = maccabi_games_stats
        self.games = maccabi_games_stats.games

    def _get_top_players_streaks_by_condition_from_games_they_played(
            self, streak_condition: Callable[[MaccabiGamesStats, str], MaccabiGamesStats],
            top_players_count: int = 10) -> List[PlayerAndGames]:
        """
        For each player, given his MaccabiGamesStats (means = ONLY the games he played) - calculate the relevant streak.
        For example: "streak_condition= lambda games, player_name: games.streaks.get_longest_unbeaten_streak_games())"

        :param streak_condition: callable that get (MaccabiGamesStats, player_name) as params and return streak
        """
        players_games = self.maccabi_games_stats.played_games_by_player_name()

        unsorted_players_streaks = {player_name: streak_condition(players_games[player_name], player_name) for
                                    player_name in self.maccabi_games_stats.available_players_names}

        return sorted(unsorted_players_streaks.items(), key=lambda kv: len(kv[1]), reverse=True)[:top_players_count]

    def _get_players_streak_by_condition_from_all_games(
            self, streak_condition: Callable[[MaccabiGamesStats, str], MaccabiGamesStats],
            top_players_count: int = 10) -> List[PlayerAndGames]:
        """
        Same as "_get_players_streak_by_condition", but we don't filters the games for each player.
        In this function the condition is check against all of the available games,
        even if the player didn't play in a game
        (useful for queries like "which player played the most games in a row?").
        """
        pbar = ProgressBar()
        unsorted_players_streaks = dict()
        for player in pbar(self.maccabi_games_stats.available_players):
            unsorted_players_streaks[player.name] = streak_condition(self.maccabi_games_stats, player.name)

        return sorted(unsorted_players_streaks.items(), key=lambda kv: len(kv[1]), reverse=True)[:top_players_count]

    # region Top players streaks

    def get_players_with_best_unbeaten_streak(self) -> List[PlayerAndGames]:
        return self._get_top_players_streaks_by_condition_from_games_they_played(
            lambda games, player_name: games.streaks.get_longest_unbeaten_streak_games())

    def get_players_with_best_win_streak(self) -> List[PlayerAndGames]:
        return self._get_top_players_streaks_by_condition_from_games_they_played(
            lambda games, player_name: games.streaks.get_longest_wins_streak_games())

    def get_players_with_best_ties_streak(self) -> List[PlayerAndGames]:
        return self._get_top_players_streaks_by_condition_from_games_they_played(
            lambda games, player_name: games.streaks.get_longest_ties_streak_games())

    def get_players_with_best_losses_streak(self) -> List[PlayerAndGames]:
        return self._get_top_players_streaks_by_condition_from_games_they_played(
            lambda games, player_name: games.streaks.get_longest_losses_streak_games())

    def get_players_with_best_maccabi_score_goal_streak(self) -> List[PlayerAndGames]:
        return self._get_top_players_streaks_by_condition_from_games_they_played(
            lambda games, player_name: games.streaks.get_longest_score_at_least_games(1))

    def get_players_with_best_maccabi_score_at_least_goals_streak(self, goals: int) -> List[PlayerAndGames]:
        """
        :param goals: Goals amount that maccabi scored (at least)
        """
        return self._get_top_players_streaks_by_condition_from_games_they_played(
            lambda games, player_name: games.streaks.get_longest_score_at_least_games(goals))

    def get_players_with_best_maccabi_score_no_goal_streak(self) -> List[PlayerAndGames]:
        return self._get_top_players_streaks_by_condition_from_games_they_played(
            lambda games, player_name: games.streaks.get_longest_score_exactly_games(0))

    def get_players_with_best_maccabi_score_exactly_goals_streak(self, goals: int) -> List[PlayerAndGames]:
        """
        :param goals: Goals amount that maccabi scored (exactly)
        """
        return self._get_top_players_streaks_by_condition_from_games_they_played(
            lambda games, player_name: games.streaks.get_longest_score_exactly_games(goals))

    def get_players_with_best_clean_sheets_streak(self) -> List[PlayerAndGames]:
        return self._get_top_players_streaks_by_condition_from_games_they_played(
            lambda games, player_name: games.streaks.get_longest_clean_sheet_games())

    def get_players_with_best_played_in_game_streak(self) -> List[PlayerAndGames]:
        return self._get_players_streak_by_condition_from_all_games(
            lambda games, player_name: games.streaks.get_longest_player_played_in_game(player_name))

    def get_players_with_best_goal_scoring_streak(self, goals: int = 1):
        goals_in_a_game = PlayerGamesCondition.create_score_x_goals_in_game__condition(goals)

        def _find_best_goal_scoring_streak_from_played_games(games: MaccabiGamesStats, player_name: str):
            return games.streaks._get_longest_streak_by_condition(lambda g: goals_in_a_game(g, player_name))

        return self._get_top_players_streaks_by_condition_from_games_they_played(
            _find_best_goal_scoring_streak_from_played_games)

    def get_players_with_best_goal_assisting_streak(self, assists: int = 1) -> List[PlayerAndGames]:
        assists_in_a_game = PlayerGamesCondition.create_assist_x_goals_in_game__condition(assists)

        def _find_best_goal_assisting_streak_from_played_games(games: MaccabiGamesStats, player_name: str):
            return games.streaks._get_longest_streak_by_condition(lambda g: assists_in_a_game(g, player_name))

        return self._get_top_players_streaks_by_condition_from_games_they_played(
            _find_best_goal_assisting_streak_from_played_games)

    def get_players_with_best_goal_involving_streak(self, goals_involved: int = 1) -> List[PlayerAndGames]:
        involved_in_a_game = PlayerGamesCondition.create_involved_in_x_goals_in_game__condition(goals_involved)

        def _find_best_goals_involved_streak_from_played_games(games: MaccabiGamesStats, player_name: str):
            return games.streaks._get_longest_streak_by_condition(lambda g: involved_in_a_game(g, player_name))

        return self._get_top_players_streaks_by_condition_from_games_they_played(
            _find_best_goals_involved_streak_from_played_games)

    def get_players_with_current_unbeaten_streak(self) -> List[PlayerAndGames]:
        return self._get_top_players_streaks_by_condition_from_games_they_played(
            lambda games, player_name: games.streaks.get_current_unbeaten_streak())

    # endregion

    # region Current streaks for players

    def get_players_with_best_scored_against_maccabi_not_more_than_streak(self, not_maccabi_score: int) \
            -> List[PlayerAndGames]:
        return self._get_top_players_streaks_by_condition_from_games_they_played(
            lambda games, player_name: games.streaks.get_longest_scored_against_maccabi_not_more_than_games(
                not_maccabi_score))

    def get_players_with_current_win_streak(self) -> List[PlayerAndGames]:
        return self._get_top_players_streaks_by_condition_from_games_they_played(
            lambda games, player_name: games.streaks.get_current_wins_streak())

    def get_players_with_current_ties_streak(self) -> List[PlayerAndGames]:
        return self._get_top_players_streaks_by_condition_from_games_they_played(
            lambda games, player_name: games.streaks.get_current_ties_streak())

    def get_players_with_current_losses_streak(self) -> List[PlayerAndGames]:
        return self._get_top_players_streaks_by_condition_from_games_they_played(
            lambda games, player_name: games.streaks.get_current_losses_streak())

    def get_players_with_current_maccabi_score_goal_streak(self) -> List[PlayerAndGames]:
        return self._get_top_players_streaks_by_condition_from_games_they_played(
            lambda games, player_name: games.streaks.get_current_score_at_least_streak(1))

    def get_players_with_current_maccabi_score_at_least_goals_streak(self, goals_amount: int) -> List[PlayerAndGames]:
        """
        :param goals_amount: Goals amount that maccabi scored (at least)
        """

        return self._get_top_players_streaks_by_condition_from_games_they_played(
            lambda games, player_name: games.streaks.get_current_score_at_least_streak(goals_amount))

    def get_players_with_current_maccabi_score_no_goal_streak(self) -> List[PlayerAndGames]:
        return self._get_top_players_streaks_by_condition_from_games_they_played(
            lambda games, player_name: games.streaks.get_current_score_exactly_streak(0))

    def get_players_with_current_maccabi_score_exactly_goals_streak(self, goals_amount: int) -> List[PlayerAndGames]:
        """
        :param goals_amount: Goals amount that maccabi scored (exactly)
        """

        return self._get_top_players_streaks_by_condition_from_games_they_played(
            lambda games, player_name: games.streaks.get_current_score_exactly_streak(goals_amount))

    def get_players_with_current_clean_sheets_streak(self) -> List[PlayerAndGames]:
        return self._get_top_players_streaks_by_condition_from_games_they_played(
            lambda games, player_name: games.streaks.get_current_clean_sheet_streak())

    def get_players_with_current_goal_scoring_streak(self, goals: int = 1) -> List[PlayerAndGames]:
        goals_in_a_game = PlayerGamesCondition.create_score_x_goals_in_game__condition(goals)

        def _find_current_goal_scoring_streak_from_played_games(games: MaccabiGamesStats, player_name: str):
            return games.streaks._get_current_streak_by_condition(lambda g: goals_in_a_game(g, player_name))

        return self._get_top_players_streaks_by_condition_from_games_they_played(
            _find_current_goal_scoring_streak_from_played_games)

    def get_players_with_current_goal_assisting_streak(self, assists: int = 1) -> List[PlayerAndGames]:
        assists_in_a_game = PlayerGamesCondition.create_assist_x_goals_in_game__condition(assists)

        def _find_current_goal_assisting_streak_from_played_games(games: MaccabiGamesStats, player_name: str):
            return games.streaks._get_current_streak_by_condition(lambda g: assists_in_a_game(g, player_name))

        return self._get_top_players_streaks_by_condition_from_games_they_played(
            _find_current_goal_assisting_streak_from_played_games)

    def get_players_with_current_goal_involving_streak(self, goals_involved: int = 1) -> List[PlayerAndGames]:
        involved_in_a_game = PlayerGamesCondition.create_involved_in_x_goals_in_game__condition(goals_involved)

        def _find_current_goals_involved_streak_from_played_games(games: MaccabiGamesStats, player_name: str):
            return games.streaks._get_current_streak_by_condition(lambda g: involved_in_a_game(g, player_name))

        return self._get_top_players_streaks_by_condition_from_games_they_played(
            _find_current_goals_involved_streak_from_played_games)

    def get_players_with_current_scored_against_maccabi_not_more_than_streak(self, not_maccabi_score: int) \
            -> List[PlayerAndGames]:
        return self._get_top_players_streaks_by_condition_from_games_they_played(
            lambda games, player_name: games.streaks.get_current_scored_against_maccabi_not_more_than_streak(
                not_maccabi_score))

    def get_players_with_current_played_in_game_streak(self) -> List[PlayerAndGames]:
        return self._get_players_streak_by_condition_from_all_games(
            lambda games, player_name: games.streaks.get_current_player_played_in_game_streak(player_name))

    # endregion
