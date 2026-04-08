from __future__ import annotations

import datetime
import logging
from datetime import timedelta
from typing import TYPE_CHECKING, List, Callable

from maccabistats.maccabipedia.players import MaccabiPediaPlayers
from maccabistats.models.game_data import GameData
from maccabistats.stats.players_games_condition import PlayerAging
from maccabistats.stats.players_games_condition import PlayerGameMatcher, PlayerGamesCondition

if TYPE_CHECKING:
    from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats

logger = logging.getLogger(__name__)


class PlayerAgeAtSpecialGame(object):
    _days_in_year = 365.2425

    def __init__(self, player_name: str, player_birth_date: datetime.datetime, special_game: GameData):
        self.player_name = player_name
        self.birth_date = player_birth_date
        self.first_game = special_game

        self.time_in_days = special_game.date - player_birth_date
        self.time_in_years = self.time_in_days / timedelta(self._days_in_year)

    def __repr__(self) -> str:
        return f"{self.player_name} | {self.time_in_years:.2f} שנים --> המשחק: {self.first_game.date.date()} (נולד ב {self.birth_date.date()})"


class MaccabiGamesPlayersSpecialGamesStats(object):
    """
    This class will handle all players events and the first time they occur, like:
     * First time that a player score - who's the youngest?
    """

    def __init__(self, maccabi_games_stats: MaccabiGamesStats):
        self.maccabi_games_stats = maccabi_games_stats
        self.games = maccabi_games_stats.games
        self.players_birth_dates = MaccabiPediaPlayers.get_players_data().players_dates

    def _players_by_game_condition_ordered_by_age(self,
                                                  player_game_condition: Callable[[GameData, str], bool],
                                                  player_game_to_search_for: PlayerGameMatcher,
                                                  order_by_age_option: PlayerAging,
                                                  players_count: int) -> List[PlayerAgeAtSpecialGame]:
        """
        :param player_game_condition: A function that will check whether the given player satisfy a condition in a game
        :param player_game_to_search_for: Search for first/last game of this player (to satisfy the condition)
        :param order_by_age_option: Do we want the youngest or oldest players?
        :param: The amount of players we want to return
        :return: The players that satisfy the player game condition, from youngest and above
        """
        games_by_player_name = self.maccabi_games_stats.played_games_by_player_name()

        first_game_by_player_name = dict()
        for player_name, player_games in games_by_player_name.items():
            if player_game_to_search_for.value == PlayerGameMatcher.LAST_GAME.value:
                player_games = reversed(player_games)  # We should search for the player last game

            first_game = next((game for game in player_games if player_game_condition(game, player_name)), None)
            if first_game is None:
                continue  # This player does not satisfy the condition
            if MaccabiPediaPlayers.missing_birth_date_value == self.players_birth_dates[player_name]:
                continue  # This player does not have any birth date on our db

            first_game_by_player_name[player_name] = PlayerAgeAtSpecialGame(player_name,
                                                                            self.players_birth_dates[player_name],
                                                                            first_game)

        players_by_age = sorted(first_game_by_player_name.values(),
                                key=lambda player_first_game: player_first_game.time_in_days)
        if order_by_age_option.value == PlayerAging.OLDEST_PLAYERS.value:
            players_by_age = list(reversed(players_by_age))

        return players_by_age[:players_count]

    def youngest_players_by_first_time_to_play(self, players_count: int = 50):
        return self._players_by_game_condition_ordered_by_age(PlayerGamesCondition.play_in_game,
                                                              PlayerGameMatcher.FIRST_GAME,
                                                              PlayerAging.YOUNGEST_PLAYERS, players_count)

    def oldest_players_by_first_time_to_play(self, players_count: int = 50):
        return self._players_by_game_condition_ordered_by_age(PlayerGamesCondition.play_in_game,
                                                              PlayerGameMatcher.FIRST_GAME, PlayerAging.OLDEST_PLAYERS,
                                                              players_count)

    def oldest_players_by_last_time_to_play(self, players_count: int = 50):
        return self._players_by_game_condition_ordered_by_age(PlayerGamesCondition.play_in_game,
                                                              PlayerGameMatcher.LAST_GAME, PlayerAging.OLDEST_PLAYERS,
                                                              players_count)

    def youngest_players_by_first_time_to_score(self, score_at_least: int = 1, players_count: int = 50):
        return self._players_by_game_condition_ordered_by_age(
            PlayerGamesCondition.create_score_x_goals_in_game__condition(score_at_least),
            PlayerGameMatcher.FIRST_GAME, PlayerAging.YOUNGEST_PLAYERS, players_count)

    def youngest_players_by_first_time_to_goal_involved(self, involved_at_least: int = 1, players_count: int = 50):
        return self._players_by_game_condition_ordered_by_age(
            PlayerGamesCondition.create_involved_in_x_goals_in_game__condition(involved_at_least),
            PlayerGameMatcher.FIRST_GAME, PlayerAging.YOUNGEST_PLAYERS, players_count)

    def oldest_players_by_first_time_to_score(self, score_at_least: int = 1, players_count: int = 50):
        return self._players_by_game_condition_ordered_by_age(
            PlayerGamesCondition.create_score_x_goals_in_game__condition(score_at_least),
            PlayerGameMatcher.FIRST_GAME, PlayerAging.OLDEST_PLAYERS, players_count)

    def oldest_players_by_last_time_to_score(self, score_at_least: int = 1, players_count: int = 50):
        return self._players_by_game_condition_ordered_by_age(
            PlayerGamesCondition.create_score_x_goals_in_game__condition(score_at_least),
            PlayerGameMatcher.LAST_GAME, PlayerAging.OLDEST_PLAYERS, players_count)

    def youngest_players_by_first_time_to_assist(self, assist_at_least: int = 1, players_count: int = 50):
        return self._players_by_game_condition_ordered_by_age(
            PlayerGamesCondition.create_assist_x_goals_in_game__condition(assist_at_least),
            PlayerGameMatcher.FIRST_GAME, PlayerAging.YOUNGEST_PLAYERS, players_count)

    def oldest_players_by_first_time_to_assist(self, assist_at_least: int = 1, players_count: int = 50):
        return self._players_by_game_condition_ordered_by_age(
            PlayerGamesCondition.create_assist_x_goals_in_game__condition(assist_at_least),
            PlayerGameMatcher.FIRST_GAME, PlayerAging.OLDEST_PLAYERS, players_count)

    def oldest_players_by_last_time_to_assist(self, assist_at_least: int = 1, players_count: int = 50):
        return self._players_by_game_condition_ordered_by_age(
            PlayerGamesCondition.create_assist_x_goals_in_game__condition(assist_at_least),
            PlayerGameMatcher.LAST_GAME, PlayerAging.OLDEST_PLAYERS, players_count)

    def youngest_players_by_first_time_to_be_captain(self, players_count: int = 500):
        return self._players_by_game_condition_ordered_by_age(_player_was_captain_in_a_game,
                                                              PlayerGameMatcher.FIRST_GAME,
                                                              PlayerAging.YOUNGEST_PLAYERS, players_count)

    def oldest_players_by_first_time_to_be_captain(self, players_count: int = 500):
        return self._players_by_game_condition_ordered_by_age(_player_was_captain_in_a_game,
                                                              PlayerGameMatcher.FIRST_GAME, PlayerAging.OLDEST_PLAYERS,
                                                              players_count)

    def oldest_players_by_last_time_to_be_captain(self, players_count: int = 500):
        return self._players_by_game_condition_ordered_by_age(_player_was_captain_in_a_game,
                                                              PlayerGameMatcher.LAST_GAME, PlayerAging.OLDEST_PLAYERS,
                                                              players_count)


def _player_was_captain_in_a_game(game: GameData, player_name: str) -> bool:
    return player_name in game.maccabi_team.captains_players_with_amount
