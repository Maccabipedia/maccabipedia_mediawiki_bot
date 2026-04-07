from __future__ import annotations

from enum import Enum
from typing import Callable

from maccabistats.models.game_data import GameData


class PlayerAging(Enum):
    YOUNGEST_PLAYERS = "youngest"
    OLDEST_PLAYERS = "oldest"


class PlayerGameMatcher(Enum):
    FIRST_GAME = "first_game"
    LAST_GAME = "last_game"


class PlayerGamesCondition:

    @staticmethod
    def play_in_game(game: GameData, player_name: str) -> bool:
        return player_name in [p.name for p in game.maccabi_team.played_players]

    @staticmethod
    def create_score_x_goals_in_game__condition(goals_at_least) -> Callable[[GameData, str], bool]:
        def scored_in_game_x_goals(game: GameData, player_name: str) -> bool:
            return game.maccabi_team.scored_players_with_amount.get(player_name, 0) >= goals_at_least

        return scored_in_game_x_goals

    @staticmethod
    def create_assist_x_goals_in_game__condition(assist_at_least) -> Callable[[GameData, str], bool]:
        def assists_in_game_x_goals(game: GameData, player_name: str) -> bool:
            return game.maccabi_team.assist_players_with_amount.get(player_name, 0) >= assist_at_least

        return assists_in_game_x_goals

    @staticmethod
    def create_involved_in_x_goals_in_game__condition(involved_at_least) -> Callable[[GameData, str], bool]:
        def involved_in_game_x_goals(game: GameData, player_name: str) -> bool:
            assists = game.maccabi_team.assist_players_with_amount.get(player_name, 0)
            scored = game.maccabi_team.scored_players_with_amount.get(player_name, 0)

            return assists + scored >= involved_at_least

        return involved_in_game_x_goals
