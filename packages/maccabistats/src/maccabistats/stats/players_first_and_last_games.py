from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Callable, Tuple, List, Dict

from maccabistats.models.game_data import GameData

if TYPE_CHECKING:
    from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats

from maccabistats.stats.players_games_condition import PlayerGameMatcher, PlayerGamesCondition

logger = logging.getLogger(__name__)

PlayerAndGame = Tuple[str, GameData]


class MaccabiGamesPlayersFirstAndLastGamesStats(object):
    """
    This class will handle the players first and last games they participated in their career
    and checks whether a condition was satisfied in that game.
    For example, "Who are the players that score in their first game"?

    Don't be confused with 'MaccabiGamesPlayersSpecialGamesStats' which checks:
    WHEN every player did an event at the first time, like:
    "When every player scored his first goal?"
    Which ofc can be after the first game or before the last one.
    """

    def __init__(self, maccabi_games_stats: MaccabiGamesStats):
        self.maccabi_games_stats = maccabi_games_stats
        self.games = maccabi_games_stats.games

    def _players_that_satisfy_condition_at_their_first_or_last_game(
            self,
            player_game_condition: Callable[[GameData, str], bool],
            player_game_to_search_for: PlayerGameMatcher) -> List[PlayerAndGame]:
        """
        Check which players satisfy the given condition at their first or last game, like:
         * "which players score at their first game?"

        :param player_game_condition: A function that will check whether the given player satisfy a condition in a game
        :param player_game_to_search_for: Search for first/last game of this player (to satisfy the condition)
        :return: The players that satisfy the condition at their game + the first game, ordered by the game data ASC
        """
        games_by_player_name = self.maccabi_games_stats.played_games_by_player_name()
        players_that_satisfy_condition: Dict[str, GameData] = dict()

        for player_name, player_games in games_by_player_name.items():
            if player_game_to_search_for.value == PlayerGameMatcher.LAST_GAME.value:
                game_to_check = player_games[-1]
            elif player_game_to_search_for.value == PlayerGameMatcher.FIRST_GAME.value:
                game_to_check = player_games[0]
            else:
                raise TypeError("Unknown game matcher")

            if player_game_condition(game_to_check, player_name):
                players_that_satisfy_condition[player_name] = game_to_check

        return sorted(players_that_satisfy_condition.items(), key=lambda item: item[1].date)

    def players_that_scored_at_their_first_game(self, score_at_least: int = 1) -> List[PlayerAndGame]:
        return self._players_that_satisfy_condition_at_their_first_or_last_game(
            PlayerGamesCondition.create_score_x_goals_in_game__condition(score_at_least), PlayerGameMatcher.FIRST_GAME)

    def players_that_scored_at_their_last_game(self, score_at_least: int = 1) -> List[PlayerAndGame]:
        return self._players_that_satisfy_condition_at_their_first_or_last_game(
            PlayerGamesCondition.create_score_x_goals_in_game__condition(score_at_least), PlayerGameMatcher.LAST_GAME)

    def players_that_assisted_at_their_first_game(self, assist_at_least: int = 1) -> List[PlayerAndGame]:
        return self._players_that_satisfy_condition_at_their_first_or_last_game(
            PlayerGamesCondition.create_assist_x_goals_in_game__condition(assist_at_least),
            PlayerGameMatcher.FIRST_GAME)

    def players_that_assisted_at_their_last_game(self, assist_at_least: int = 1) -> List[PlayerAndGame]:
        return self._players_that_satisfy_condition_at_their_first_or_last_game(
            PlayerGamesCondition.create_assist_x_goals_in_game__condition(assist_at_least), PlayerGameMatcher.LAST_GAME)
