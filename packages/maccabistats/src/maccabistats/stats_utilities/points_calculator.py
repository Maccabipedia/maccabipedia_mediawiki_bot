from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from maccabistats.models.game_data import GameData

if TYPE_CHECKING:
    from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats

_AFTER_THIS_DATE_3_POINTS_WERE_GIVEN = datetime(year=1982, month=9, day=25)


def calculate_possible_points_for_games(games: MaccabiGamesStats) -> int:
    games_3_points = games.played_after(_AFTER_THIS_DATE_3_POINTS_WERE_GIVEN)

    return (3 * len(games_3_points)) + (2 * (len(games) - len(games_3_points)))


def calculate_points_for_games(games: MaccabiGamesStats) -> int:
    return sum(_point_for_specific_game(game) for game in games)


def _point_for_specific_game(game: GameData) -> int:
    if game.played_after(_AFTER_THIS_DATE_3_POINTS_WERE_GIVEN):
        return _point_by_result(game=game, win_points=3, tie_points=1, lose_points=0)
    else:
        return _point_by_result(game=game, win_points=2, tie_points=1, lose_points=0)


def _point_by_result(game: GameData, win_points: int, tie_points: int, lose_points: int) -> int:
    if game.is_maccabi_win:
        return win_points
    elif game.maccabi_score_diff == 0:
        return tie_points
    elif game.maccabi_score_diff < 0:
        return lose_points
    else:
        raise TypeError(f'Could not identify the result of this game: {game}')
