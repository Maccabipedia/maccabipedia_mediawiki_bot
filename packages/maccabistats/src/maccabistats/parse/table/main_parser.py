# -*- coding: utf-8 -*-

from pathlib import Path
import json
from dateutil.parser import parse as datetime_parser
from maccabistats.models.game_data import GameData
from maccabistats.models.team_in_game import TeamInGame

root_folder = Path.home()

# TODO: make that better (maybe from config).
jsoned_games_path = root_folder / "maccabistats" / "sources" / "table-games.json"

"""
 Jsoned game format:

        "referee": str,
        "away_team": str,
        "away_team_score": int,
        "home_team_score": int,
        "home_team": str,
        "stadium": str,
        "date": str date :"1955-02-05 00:00:00",
        "fixture": int,
        "season": str
"""


def get_jsoned_table_games():
    with open(jsoned_games_path, 'rb') as f:
        return json.load(f)


def parse_to_maccabistats_game(jsoned_game):
    """
    Parse jsoned game to maccabistats game format (GameData).
    :param jsoned_game: the game to parse.
    :type jsoned_game: dict
    :return: maccabistats.models.game_data.GameData
    """

    home_team = TeamInGame(jsoned_game['home_team'], None, jsoned_game['home_team_score'], [])
    away_team = TeamInGame(jsoned_game['away_team'], None, jsoned_game['away_team_score'], [])
    date = datetime_parser(jsoned_game['date'])
    game = GameData("ליגת העל", jsoned_game["fixture"], "", jsoned_game["stadium"], "", jsoned_game["referee"], home_team, away_team,
                    jsoned_game["season"], [], date)

    return game


def get_parsed_maccabi_games_from_json():
    jsoned_table_games = get_jsoned_table_games()

    maccabistats_format_games = [parse_to_maccabistats_game(game) for game in jsoned_table_games]

    return maccabistats_format_games
