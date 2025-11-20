import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)

from datetime import datetime
from typing import List

import pandas as pd
import requests

from volleyball_common import TEAM_NAMES_REPLACER, STADIUMS_NAMES
from gamesbot_volleyball import VolleyballGame, create_or_update_volleyball_game_pages

WEB_ADDRESS_FOR_MACCABI_LEAGUE_GAMES = 'https://iva.org.il/team/?TeamId=34149&cYear=2026'
MACCABI_NAMES = ['מכבי יעדים תל-אביב']
LEAGUE_NAME_AS_IT_DISPLAYED_IN_IVA_SITE = 'ליגת על גברים'
TROPHY_NAME_AS_IT_DISPLAYED_IN_IVA_SITE = 'גביע המדינה לגברים'
LEAGUE_NAME = 'ליגת העל'
TROPHY_NAME = 'גביע המדינה'
CURRENT_SEASON = '2025/26'


def create_volleyball_game_from_dataframe_row(row: pd.Series) -> VolleyballGame:
    raw_date_parts = row["תאריך"].split()
    game_date = datetime.strptime(f'{raw_date_parts[0]} {raw_date_parts[3]}', '%d/%m/%Y %H:%M')

    is_home_game = row["מארחת"] in MACCABI_NAMES
    opponent_name = row["אורחת"] if is_home_game else row["מארחת"]
    stadium = row["אולם"]

    # The result can be float (NaN) for future games, or string with "-" in case of a played game
    if isinstance(row["תוצאה"], str) and "-" in row["תוצאה"]:
        maccabi_result, opponent_result = (row["תוצאה"].split('-')[::-1]) if is_home_game else row["תוצאה"].split('-')
    else:
        maccabi_result, opponent_result = None, None  # Future game

    if LEAGUE_NAME_AS_IT_DISPLAYED_IN_IVA_SITE in row["מסגרת"]:
        fixture = row["מסגרת"].replace(LEAGUE_NAME_AS_IT_DISPLAYED_IN_IVA_SITE, '')
        competition = LEAGUE_NAME
    elif TROPHY_NAME_AS_IT_DISPLAYED_IN_IVA_SITE in row["מסגרת"]:
        fixture = row["מסגרת"].replace(TROPHY_NAME_AS_IT_DISPLAYED_IN_IVA_SITE, '')
        competition = TROPHY_NAME
    else:
        raise RuntimeError(f'Could not find matching competition: {row["מסגרת"]}')


    return VolleyballGame(date=game_date,
                          fixture=fixture,
                          opponent=opponent_name,
                          home_game=is_home_game,
                          competition=competition,
                          season=CURRENT_SEASON,
                          stadium=stadium,
                          maccabi_result=maccabi_result,
                          opponent_result=opponent_result
                          )


def _correct_team_name(volleyball_game: VolleyballGame) -> None:
    corrected_opponent_name = TEAM_NAMES_REPLACER.get(volleyball_game.opponent, volleyball_game.opponent)
    if corrected_opponent_name == volleyball_game.opponent:
        return

    logging.info(f'Changed team name from: {volleyball_game.opponent} to: {corrected_opponent_name}')
    volleyball_game.opponent = corrected_opponent_name
    return


def _correct_stadium_name(volleyball_game: VolleyballGame) -> None:
    corrected_stadium_name = STADIUMS_NAMES.get(volleyball_game.stadium, volleyball_game.stadium)
    if corrected_stadium_name == volleyball_game.stadium:
        return

    logging.info(f'Changed stadium name from: {volleyball_game.stadium} to: {corrected_stadium_name}')
    volleyball_game.stadium = corrected_stadium_name
    return


def correct_volleyball_namings(volleyball_game: VolleyballGame):
    _correct_team_name(volleyball_game)
    _correct_stadium_name(volleyball_game)


def extract_games_metadata(include_future_games: bool = False) -> List[VolleyballGame]:
    logging.info(f'Fetching games from: {WEB_ADDRESS_FOR_MACCABI_LEAGUE_GAMES}')
    maccabi_main_page_response = requests.get(WEB_ADDRESS_FOR_MACCABI_LEAGUE_GAMES, timeout=120)

    tables = pd.read_html(maccabi_main_page_response.content, flavor="html5lib")

    if len(tables) > 1:
        raise RuntimeError("Something changed, we've found more than one table, need to be examined manually")

    games_table = tables[0]

    finished_games_count = games_table['תוצאה'].notna().sum()
    logging.info(f'Found {len(games_table)} games records, out of them we found {finished_games_count} finished games')

    all_games = []
    if include_future_games:
        games_to_fetch = games_table.iterrows()
    else:
        games_to_fetch = games_table[games_table['תוצאה'].notna()].iterrows()

    for _, game_row in games_to_fetch:
        game = create_volleyball_game_from_dataframe_row(game_row)
        correct_volleyball_namings(game)
        all_games.append(game)

    return all_games


def upload_games_from_iva_to_maccabipedia() -> None:
    games_pages = extract_games_metadata()

    create_or_update_volleyball_game_pages(games_pages)


if __name__ == '__main__':
    upload_games_from_iva_to_maccabipedia()
