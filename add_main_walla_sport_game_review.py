import json
import logging
from pathlib import Path
from typing import Dict, Tuple

import mwparserfromhell as mw
import pywikibot as pw
import requests
from pyquery import PyQuery

from maccabistats import load_from_maccabipedia_source
from models.game_data import GameData
from stats.maccabi_games_stats import MaccabiGamesStats

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

site = pw.Site()

games_page_prefix = "משחק:"
games_template_name = "קטלוג משחקים"

SHOULD_SAVE = True
SHOULD_SHOW_DIFF = True

GameInformation = Tuple[str, str]  # Review, Hour
OneSeasonMapping = Dict[int, GameInformation]
SeasonToGameMapping = Dict[str, OneSeasonMapping]

_WALLA_BASE_URL = 'https://sports.walla.co.il'
_WALLA_SEASON_URL_UNFORMATTED = f'{_WALLA_BASE_URL}' + '/league/157?leagueId={league_id}'

_SEASON_TO_WALLA_LEAGUE_ID = {'2000/01': 17,
                              '2001/02': 86,
                              '2002/03': 188,
                              '2003/04': 243,
                              '2004/05': 300,
                              '2005/06': 361,
                              '2006/07': 1004,
                              '2007/08': 1184,
                              '2008/09': 1347,
                              '2009/10': 1482,
                              '2010/11': 1665,
                              '2011/12': 1802,
                              '2012/13': 1918,
                              '2013/14': 2019,
                              '2014/15': 2133,
                              '2015/16': 2231,
                              '2016/17': 2343,
                              '2017/18': 2437,
                              '2018/19': 2506,
                              '2019/20': 2568,
                              '2020/21': 2623
                              }


def _save_page_changes(game_page, new_text):
    """
    :type game_page: pywikibot.page.Page
    :type new_text: str
    """
    if game_page.text == new_text:
        logging.info(f'No changes detected, does not save this page: {game_page.title()}')
        return

    if SHOULD_SHOW_DIFF:
        pw.showDiff(game_page.text, new_text)
    if not SHOULD_SAVE:
        logging.info(f"SHOULD_SAVE=False, dont saving changes for page: {game_page.title()}")
        return

    game_page.text = new_text
    game_page.save(summary="MaccabiBot - Adding game reviews and hours", botflag=True)


def find_next_game_review_param(game_template) -> str:
    review_number_unformatted = 'כתבה{index}'

    for index in range(1, 100):
        current_review = review_number_unformatted.format(index=index)
        if not game_template.has(current_review):
            return current_review

    raise RuntimeError('Could not find game review')


def matches_games_template(*args, **kwargs):
    return args[0].name.strip() == games_template_name


def add_hour_and_game_review_to_game_page(game_page: pw.page.Page, game_information: GameInformation) -> None:
    parsed_mw_text = mw.parse(game_page.text)
    templates = parsed_mw_text.filter_templates(matches=matches_games_template)
    if not templates:
        logging.warning(f"Found no game template in this page: {game_page.title()}")
        return

    game_template = templates[0]

    if game_information[0]:
        if game_information[0] in game_template:
            logging.warning(f'This page already has this game review, skipping')
        else:
            next_review_param_name = find_next_game_review_param(game_template)
            add_before_this_param = 'מדים' if game_template.has('מדים') else 'אירועי שחקנים'

            logging.info(f'Adding game information at: {next_review_param_name}')
            game_review_with_link = f'[{game_information[0]} סיקור המשחק בWalla sport]'
            game_template.add(name=next_review_param_name, value=game_review_with_link, before=add_before_this_param)
    else:
        logging.info('Game review is empty, Skipping')

    if game_information[1]:
        game_hour_param = [param for param in game_template.params if param.name == 'שעת המשחק']
        if len(game_hour_param) != 1:
            raise RuntimeError('Too many game hour params!')
        game_hour_param = game_hour_param[0]

        # 0 indicates an unknown hour, lets replace it
        if not game_hour_param.value or game_hour_param.value.strip() == '0':
            logging.info(f'Game hour is empty, adding walla time: {game_information[1]}')
            game_hour_param.value = f'{game_information[1]}\n'

        elif game_hour_param.value.strip() != game_information[1]:
            logging.warning(f'Game named: {game_page.title()} having conflict in the hour.'
                            f'Walla: {game_information[1]}, current: {game_hour_param.value.strip()}')
            a = 6
        else:
            logging.info(f'Hours are equal!')

    else:
        logging.info('Game information hour is empty, skipping hour')

    _save_page_changes(game_page, parsed_mw_text)


def generate_page_name_from_game(game: GameData) -> str:
    football_games_prefix = "משחק"
    page_name = "{prefix}: {date} {home_team} נגד {away_team} - {competition}".format(prefix=football_games_prefix,
                                                                                      date=game.date.strftime('%d-%m-%Y'),
                                                                                      home_team=game.home_team.name,
                                                                                      away_team=game.away_team.name,
                                                                                      competition=game.competition)

    return page_name


def game_page_from_maccabipedia_game(maccabipedia_game: GameData) -> pw.Page:
    page_name = generate_page_name_from_game(maccabipedia_game)

    return pw.Page(site, page_name)


def readable_text(text):
    return text.encode('latin1').decode('utf8')


def extract_information_from_fixture_url(fixture_url: str) -> GameInformation:
    fixture_page = requests.get(fixture_url)
    fixture_query = PyQuery(fixture_page.content)

    possible_maccabi_game_elements = fixture_query('.rounds-section .round-games li.fc')

    maccabi_elements = [element for element in possible_maccabi_game_elements if 'מכבי תל אביב' in readable_text(element.text_content())]

    if len(maccabi_elements) != 1:
        raise RuntimeError('Could not verify which element is one of maccabi game')

    game_hour = PyQuery(maccabi_elements[0])('.time').text()
    possible_game_review = PyQuery(maccabi_elements[0])('.common-more')

    if possible_game_review:  # Not all fixtures has game reviews
        suffix_url_for_review = possible_game_review[0].attrib['href']

        review_url = f'{_WALLA_BASE_URL}{suffix_url_for_review}'
        if requests.get(review_url).status_code == 404:
            logging.info(f'Url is walla 404: {review_url}')
            review_url = ''

    else:
        logging.info(f'Fixture: {fixture_url} has no game review')
        review_url = ''

    return review_url, game_hour


def extract_reviews_and_hours_from_season(season_id: str) -> OneSeasonMapping:
    walla_league_id = _SEASON_TO_WALLA_LEAGUE_ID[season_id]
    walla_season_url = _WALLA_SEASON_URL_UNFORMATTED.format(league_id=walla_league_id)

    logging.info(f'Extracting info from season {season_id} from: {walla_season_url}')

    game_data_by_fixture_number = {}

    walla_season_page = requests.get(walla_season_url)
    season_query = PyQuery(walla_season_page.content)

    fixture_elements = season_query('.round-select-box option')[1:]  # The first column is "בחר מחזור"
    for fixture in fixture_elements:
        try:
            fixture_number = int(readable_text(fixture.text).replace('מחזור', '').strip())
            fixture_url = f'{_WALLA_BASE_URL}{fixture.attrib["value"]}'

            logging.info(f'Extracting info from fixture {fixture_number}, season: {season_id}')
            game_data_by_fixture_number[fixture_number] = extract_information_from_fixture_url(fixture_url)
        except Exception:
            logging.exception(f'Unhandled exception handling fixture: {fixture} on season: {season_id}')

    return game_data_by_fixture_number


def fetch_walla_sport_game_reviews_and_hours() -> SeasonToGameMapping:
    games_information_by_season = {}

    for season in _SEASON_TO_WALLA_LEAGUE_ID.keys():
        games_information_by_season[season] = extract_reviews_and_hours_from_season(season)

    return games_information_by_season


def add_one_season_walla_data_to_maccabipedia(walla_season_data: OneSeasonMapping, maccabipedia_season_games: MaccabiGamesStats):
    if len(maccabipedia_season_games) != len(walla_season_data):
        a = 6
        if a < 2:  # For breakpoint
            raise RuntimeError('Should not happen')

    for fixture, game_information in walla_season_data.items():
        logging.info(f'Handling fixture: {fixture}')

        current_game = [g for g in maccabipedia_season_games if g.league_fixture == int(fixture)]
        if len(current_game) != 1:
            raise RuntimeError('Should not happen')

        fixture_game_page = game_page_from_maccabipedia_game(current_game[0])
        try:
            add_hour_and_game_review_to_game_page(fixture_game_page, game_information)
        except Exception:
            logging.exception(f'Unhandled exception while adding data to game: {fixture}')


def add_walla_game_date_to_maccabipedia(walla_games_data: SeasonToGameMapping):
    maccabipedia_games = load_from_maccabipedia_source().league_games  # Walla has only league games in these tables

    for season in _SEASON_TO_WALLA_LEAGUE_ID.keys():
        logging.info(f'Starting to add date for season: {season}')
        season_league_games = maccabipedia_games.get_games_by_season(season)
        walla_current_season_mapping = walla_games_data[season]

        add_one_season_walla_data_to_maccabipedia(walla_current_season_mapping, season_league_games)


if __name__ == '__main__':
    this_folder = Path(__file__).absolute().parent

    # game_data_by_season = fetch_walla_sport_game_reviews_and_hours()
    #
    # serialize 'game_data_by_season' here
    # with open(this_folder / 'walla_game_data.json', 'w') as f:
    #     json.dumps(game_data_by_season, f)

    # Upload the walla sport data to maccabipedia

    walla_data = json.loads((this_folder / 'walla_game_data.json').read_text())
    add_walla_game_date_to_maccabipedia(walla_data)
