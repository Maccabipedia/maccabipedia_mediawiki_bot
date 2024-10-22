import logging
from datetime import datetime
from typing import List

import pandas as pd
import requests

from gamesbot_volleyball import VolleyballGame, create_or_update_volleyball_game_pages

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)

WEB_ADDRESS_FOR_MACCABI_LEAGUE_GAMES = 'https://www.iva.org.il/team.asp?TeamId=17029&cYear=2025'
MACCABI_NAMES = 'מכבי יעדים תל-אביב'
LEAGUE_NAME_AS_IT_DISPLAYED_IN_IVA_SITE = 'ליגת על גברים'
LEAGUE_NAME_TO_UPLOAD = 'ליגת העל'
CURRENT_SEASON = '2024/25'


def create_volleyball_game_from_dataframe_row(row: pd.Series) -> VolleyballGame:
    raw_date_parts = row["תאריך"].split()
    game_date = datetime.strptime(f'{raw_date_parts[0]} {raw_date_parts[3]}', '%d/%m/%Y %H:%M')

    is_home_game = row["מארחת"] in MACCABI_NAMES
    opponent_name = row["אורחת"] if is_home_game else row["מארחת"]
    stadium = row["אולם"]
    fixture = row["מסגרת"].replace(LEAGUE_NAME_AS_IT_DISPLAYED_IN_IVA_SITE, '')
    maccabi_result, opponent_result = (row["תוצאה"].split('-')[::-1]) if is_home_game else row["תוצאה"].split('-')

    return VolleyballGame(date=game_date,
                          fixture=fixture,
                          opponent=opponent_name,
                          home_game=is_home_game,
                          competition=LEAGUE_NAME_TO_UPLOAD,
                          season=CURRENT_SEASON,
                          stadium=stadium,
                          maccabi_result=maccabi_result,
                          opponent_result=opponent_result
                          )


def extract_games_metadata() -> List[VolleyballGame]:
    logging.info(f'Fetching games from: {WEB_ADDRESS_FOR_MACCABI_LEAGUE_GAMES}')
    maccabi_main_page_response = requests.get(WEB_ADDRESS_FOR_MACCABI_LEAGUE_GAMES)

    tables = pd.read_html(maccabi_main_page_response.content)

    if len(tables) > 1:
        raise RuntimeError("Something changed, we've found more than one table, need to be examined manually")

    games_table = tables[0]

    finished_games_count = games_table['תוצאה'].notna().sum()
    logging.info(f'Found {len(games_table)} games records, out of them we found {finished_games_count} finished games')

    all_games = []
    for _, game_row in games_table[games_table['תוצאה'].notna()].iterrows():
        all_games.append(create_volleyball_game_from_dataframe_row(game_row))

    return all_games


def upload_games_from_iva_to_maccabipedia() -> None:
    games_pages = extract_games_metadata()

    create_or_update_volleyball_game_pages(games_pages)


if __name__ == '__main__':
    upload_games_from_iva_to_maccabipedia()