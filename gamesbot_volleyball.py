import logging
from datetime import datetime
from pathlib import Path
from typing import List

from pywikibot_boilerplate import run_boilerplate

run_boilerplate()

from prettify_games_pages import prettify_game_page_main_template
from volleyball_game import VolleyballGame

import pywikibot as pw
from mwparserfromhell.nodes.template import Template

site = pw.Site()
site.login()

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

VOLLEYBALL_ROOT_FOLDER = Path(r'D:\maccabipedia_google_drive\מכביפדיה_ראשי\כדורעף\משחקים מהעיתונות')
ALLOWED_SEASONS = ['1989-90']

volleyball_games_prefix = "כדורעף"
volleyball_games_template_name = "משחק כדורעף"

# Legend games templates args consts:
GAME_ID = "תאריך המשחק"
GAME_HOUR = "שעת המשחק"
SEASON = "עונה"
COMPETITION = "מפעל"
ROUND_IN_COMPETITION = "שלב במפעל"
OPPONENT_NAME = "שם יריבה"
HOME_OR_AWAY = "בית חוץ"
STADIUM = "אולם"
MACCABI_RESULT = "תוצאת משחק מכבי"
OPPONENT_RESULT = "תוצאת משחק יריבה"
MACCABI_COACH = "מאמן מכבי"
OPPONENT_COACH = "מאמן יריבה"
REFEREE = "שופט ראשי"
REFEREE_HELPERS = "עוזרי שופט"

CROWD = "כמות קהל"
HIGHLIGHTS_VIDEO = "תקציר וידאו"
CROWD_VIDEO = "וידאו אוהדים"
FULL_GAME_VIDEO = "משחק מלא"
BROADCAST = "גוף שידור"
COSTUME = "מדים"
MACCABI_PLAYERS = 'שחקנים מכבי'
OPPONENT_PLAYERS = 'שחקנים יריבה'
MACCABI_FIRST_SET = 'מערכה1 מכבי'
OPPONENT_FIRST_SET = 'מערכה1 יריבה'
MACCABI_SECOND_SET = 'מערכה2 מכבי'
OPPONENT_SECOND_SET = 'מערכה2 יריבה'
MACCABI_THIRD_SET = 'מערכה3 מכבי'
OPPONENT_THIRD_SET = 'מערכה3 יריבה'
MACCABI_FORTH_SET = 'מערכה4 מכבי'
OPPONENT_FORTH_SET = 'מערכה4 יריבה'
MACCABI_FIFTH_SET = 'מערכה5 מכבי'
OPPONENT_FIFTH_SET = 'מערכה5 יריבה'

SHOULD_SAVE = True
SHOULD_SHOW_DIFF = True

FILES_TO_IGNORE = {'desktop.ini'}


def build_volleyball_game_from_folder(potential_game_folder: Path) -> VolleyballGame:
    raw_season, raw_competition, raw_game_details = potential_game_folder.relative_to(
        VOLLEYBALL_ROOT_FOLDER).parts

    season = raw_season.replace("עונת", "").strip().replace("-", "/")
    competition = raw_competition
    is_trophy = 'גביע' in raw_competition

    # In case it's a playoff game, we write it as: פלייאוף - מחזור 1, so we will have extra '-'
    if 'פלייאוף' in raw_game_details:
        playoff_name, fixture, opponent, raw_date, *raw_home_or_away = map(str.strip, raw_game_details.split('-'))
        fixture = f'{playoff_name} - {fixture}'
    else:
        fixture, opponent, raw_date, *raw_home_or_away = map(str.strip, raw_game_details.split('-'))

    game_date = datetime.strptime(raw_date, '%d.%m.%Y')

    if (not is_trophy) and (not raw_home_or_away):
        raise RuntimeError('We should have home or away for non trophy')

    is_home_game = True if not raw_home_or_away else raw_home_or_away[0] in ('בית', 'נייטרלי')

    return VolleyballGame(date=game_date,
                          fixture=fixture,
                          opponent=opponent,
                          home_game=is_home_game,
                          competition=competition,
                          season=season
                          )


def get_volleyball_games() -> List[VolleyballGame]:
    all_games = []

    for potential_game_folder in VOLLEYBALL_ROOT_FOLDER.glob("**"):
        if len(potential_game_folder.relative_to(VOLLEYBALL_ROOT_FOLDER).parts) != 3:
            logging.info(f'skipping folder: {potential_game_folder}, this folder has less parts than needed')
            continue

        if not any(f'עונת {season}' in str(potential_game_folder) for season in ALLOWED_SEASONS):
            logging.info(
                f'Skipping folder: {potential_game_folder}, this folder is not in allowed seasons: {ALLOWED_SEASONS}')
            continue

        try:
            volleyball_game = build_volleyball_game_from_folder(potential_game_folder)
            all_games.append(volleyball_game)
        except Exception:
            logging.exception(f'Could not build volleyball game form this folder: {potential_game_folder}, due to:')

    return all_games


def generate_page_name_from_game(volleyball_game: VolleyballGame):
    page_name = "{prefix}:{date} {home_team} נגד {away_team} - {competition}".format(prefix=volleyball_games_prefix,
                                                                                     date=volleyball_game.date.strftime(
                                                                                         '%d-%m-%Y'),
                                                                                     home_team=volleyball_game.home_team,
                                                                                     away_team=volleyball_game.away_team,
                                                                                     competition=volleyball_game.competition)

    return page_name


def get_value_if_not_none_or_empty_string(value):
    return value if value is not None else ''


def fill_page_content(game_page, volleyball_game: VolleyballGame):
    volleyball_game_template = Template(volleyball_games_template_name)
    contains_game_hour = volleyball_game.date.strftime("%H:%M") != "00:00"

    template_parameters = {GAME_ID: str(volleyball_game.date.strftime("%d-%m-%Y")),
                           GAME_HOUR: volleyball_game.date.strftime("%H:%M") if contains_game_hour else '',
                           SEASON: volleyball_game.season,
                           COMPETITION: volleyball_game.competition,
                           ROUND_IN_COMPETITION: volleyball_game.fixture,
                           OPPONENT_NAME: volleyball_game.opponent,
                           HOME_OR_AWAY: 'בית' if volleyball_game.home_game else 'חוץ',
                           STADIUM: volleyball_game.stadium if volleyball_game.stadium is not None else '',
                           MACCABI_RESULT: get_value_if_not_none_or_empty_string(volleyball_game.maccabi_result),
                           OPPONENT_RESULT: get_value_if_not_none_or_empty_string(volleyball_game.opponent_result),
                           MACCABI_COACH: '',
                           OPPONENT_COACH: '',
                           REFEREE: '',
                           REFEREE_HELPERS: '',
                           CROWD: '',
                           BROADCAST: '',

                           HIGHLIGHTS_VIDEO: '',
                           CROWD_VIDEO: '',
                           FULL_GAME_VIDEO: '',

                           MACCABI_FIRST_SET: '',
                           OPPONENT_FIRST_SET: '',
                           MACCABI_SECOND_SET: '',
                           OPPONENT_SECOND_SET: '',
                           MACCABI_THIRD_SET: '',
                           OPPONENT_THIRD_SET: '',
                           MACCABI_FORTH_SET: '',
                           OPPONENT_FORTH_SET: '',
                           MACCABI_FIFTH_SET: '',
                           OPPONENT_FIFTH_SET: '',

                           # We want to have these params at the end:
                           MACCABI_PLAYERS: '',
                           OPPONENT_PLAYERS: ''
                           }

    for argument_name, argument_value in template_parameters.items():
        volleyball_game_template.add(argument_name, argument_value)

    game_page.text = str(volleyball_game_template)


def create_or_update_game_page(volleyball_game: VolleyballGame, overwrite_existing_pages: bool = True):
    logging.info(f"create_or_update_game_page : {volleyball_game}")

    page_name = generate_page_name_from_game(volleyball_game)

    game_page = pw.Page(site, page_name)

    # handle_new_page & handle_existing_page changes the game_page.text attribute.
    if game_page.exists():
        if not overwrite_existing_pages:
            logging.info(f"Don't edit existing pages, skipping: {page_name}")
            return

    logging.info("Page : {name} does not exists, creating\n".format(name=page_name))
    fill_page_content(game_page, volleyball_game)

    logging.info("")  # Empty line
    if SHOULD_SAVE:
        logging.info("Saving {name}".format(name=game_page.title()))
        game_page.save(summary="MaccabiBot - Uploading Volleyball Games")

        logging.info(f"Prettifying {game_page.title()}")
        prettify_game_page_main_template(game_page)

    else:
        logging.info("Not saving {name}".format(name=game_page.title()))


def create_or_update_volleyball_game_pages(games_to_add: List[VolleyballGame]):
    logging.info("")  # Empty line

    logging.info("Should save : {save}".format(save=SHOULD_SAVE))
    logging.info("Should show diff: {diff}\n".format(diff=SHOULD_SHOW_DIFF))

    for volleyball_game in games_to_add:
        create_or_update_game_page(volleyball_game, overwrite_existing_pages=False)

    logging.info("Finished adding new games.")
    logging.info("Finished handling existing games.")


if __name__ == '__main__':
    create_or_update_volleyball_game_pages(get_volleyball_games())
