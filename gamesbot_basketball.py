import logging
from pathlib import Path

from pydantic import TypeAdapter

from basketball.basketball_game import BasketballGame, PlayerSummary
from pywikibot_boilerplate import run_boilerplate

run_boilerplate()

import mwparserfromhell
import pywikibot as pw
from mwparserfromhell.nodes.template import Template

site = pw.Site()
site.login()

from prettify_games_pages import prettify_game_page_main_template

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

EXAMPLE_GAME_FILE_PATH = Path(r"D:\maccabipedia_google_drive\מכביפדיה_ראשי\כדורסל\איסוף מידע לאתר\game_exmaple.json")

basketball_games_template_name = "משחק כדורסל"
basketball_games_prefix = "כדורסל"

# Legend games templates args consts:s
GAME_DATE = "תאריך המשחק"
GAME_HOUR = "שעת המשחק"
SEASON = "עונה"
COMPETITION = "מפעל"
ROUND_IN_COMPETITION = "שלב במפעל"
OPPONENT_NAME = "שם יריבה"
HOME_OR_AWAY = "בית חוץ"
STADIUM = "אצטדיון"
MACCABI_TOTAL_POINTS = "נקודות למכבי"
OPPONENT_TOTAL_POINTS = "נקודות ליריבה"
MACCABI_COACH = "מאמן מכבי"
OPPONENT_COACH = "מאמן יריבה"
REFEREE = "שופט ראשי"
REFEREE_ASSISTERS = "עוזרי שופט"
CROWD = "כמות קהל"
IS_OVERTIME = "הארכה"
GAME_URLS = "כתבות על המשחק"
MACCABI_PLAYERS = 'שחקנים מכבי'
OPPONENT_PLAYERS = 'שחקנים יריבה'
FIRST_QUARTER_MACCABI_POINTS = 'נקודות מכבי רבע ראשון'
SECOND_QUARTER_MACCABI_POINTS = 'נקודות מכבי רבע שני'
THIRD_QUARTER_MACCABI_POINTS = 'נקודות מכבי רבע שלישי'
FOURTH_QUARTER_MACCABI_POINTS = 'נקודות מכבי רבע רביעי'
FIRST_OVERTIME_MACCABI_POINTS = 'נקודות מכבי הארכה ראשונה'
SECOND_OVERTIME_MACCABI_POINTS = 'נקודות מכבי הארכה שניה'
THIRD_OVERTIME_MACCABI_POINTS = 'נקודות מכבי הארכה שלישית'
FOURTH_OVERTIME_MACCABI_POINTS = 'נקודות מכבי הארכה רביעית'
FIRST_QUARTER_OPPONENT_POINTS = 'נקודות יריבה רבע ראשון'
SECOND_QUARTER_OPPONENT_POINTS = 'נקודות יריבה רבע שניה'
THIRD_QUARTER_OPPONENT_POINTS = 'נקודות יריבה רבע שלישי'
FOURTH_QUARTER_OPPONENT_POINTS = 'נקודות יריבה רבע רביעי'
FIRST_OVERTIME_OPPONENT_POINTS = 'נקודות יריבה הארכה ראשונה'
SECOND_OVERTIME_OPPONENT_POINTS = 'נקודות יריבה הארכה שניה'
FOURTH_OVERTIME_OPPONENT_POINTS = 'נקודות יריבה הארכה שלישית'
THIRD_OVERTIME_OPPONENT_POINTS = 'נקודות יריבה הארכה רביעית'

REFRESH_PAGES = False
JUST_EVENTS = True
SHOULD_SAVE = True
SHOULD_SHOW_DIFF = True
SHOULD_CHECK_FOR_UPDATE_IN_EXISTING_PAGES = False


def load_basketball_games() -> list[BasketballGame]:
    game_text = EXAMPLE_GAME_FILE_PATH.read_text(encoding='utf-8')
    game = TypeAdapter(BasketballGame).validate_json(game_text)
    return [game]


def generate_page_name_from_game(game: BasketballGame) -> str:
    page_name = "{prefix}:{date} {home_team} נגד {away_team} - {competition}".format(prefix=basketball_games_prefix,
                                                                                     date=game.game_date.strftime(
                                                                                         '%d-%m-%Y'),
                                                                                     home_team=game.home_team_name,
                                                                                     away_team=game.away_team_name,
                                                                                     competition=game.competition)

    return page_name


def get_players_events_for_template(players_summary: list[PlayerSummary]) -> str:
    return ",\n".join(player_summary.__maccabipedia__() for player_summary in players_summary).rstrip()


def __get_football_game_template_with_maccabistats_game_value(game: BasketballGame) -> dict[str, str]:
    template_arguments = {
        GAME_DATE: str(game.game_date.strftime("%d-%m-%Y")),
        # We don't want to upload the hour if it's equal to zero (that an unknown time)
        GAME_HOUR: game.game_date.hour if game.game_date.hour != 0 else '',
        SEASON: game.season,
        COMPETITION: game.competition,
        OPPONENT_NAME: game.opponent_name,
        HOME_OR_AWAY: 'בית' if game.is_home_game else 'חוץ',
        STADIUM: game.stadium,
        FIRST_QUARTER_MACCABI_POINTS: game.first_quarter_maccabi_points,
        SECOND_QUARTER_MACCABI_POINTS: game.second_quarter_maccabi_points,
        THIRD_QUARTER_MACCABI_POINTS: game.third_quarter_maccabi_points,
        FOURTH_QUARTER_MACCABI_POINTS: game.fourth_quarter_maccabi_points,
        FIRST_OVERTIME_MACCABI_POINTS: game.first_overtime_maccabi_points,
        SECOND_OVERTIME_MACCABI_POINTS: game.second_overtime_maccabi_points,
        THIRD_OVERTIME_MACCABI_POINTS: game.third_overtime_maccabi_points,
        FOURTH_OVERTIME_MACCABI_POINTS: game.fourth_overtime_maccabi_points,
        FIRST_QUARTER_OPPONENT_POINTS: game.first_quarter_opponent_points,
        SECOND_QUARTER_OPPONENT_POINTS: game.second_quarter_opponent_points,
        THIRD_QUARTER_OPPONENT_POINTS: game.third_quarter_opponent_points,
        FOURTH_QUARTER_OPPONENT_POINTS: game.fourth_quarter_opponent_points,
        FIRST_OVERTIME_OPPONENT_POINTS: game.first_overtime_opponent_points,
        SECOND_OVERTIME_OPPONENT_POINTS: game.second_overtime_opponent_points,
        THIRD_OVERTIME_OPPONENT_POINTS: game.third_overtime_opponent_points,
        FOURTH_OVERTIME_OPPONENT_POINTS: game.fourth_overtime_opponent_points,
        MACCABI_TOTAL_POINTS: game.maccabi_points,
        OPPONENT_TOTAL_POINTS: game.opponent_points,
        MACCABI_COACH: game.maccabi_coach,
        OPPONENT_COACH: game.opponent_coach,
        REFEREE: game.referee,
        REFEREE_ASSISTERS: ", ".join(game.referee_assistants),
        CROWD: game.crowd,
        IS_OVERTIME: "כן" if game.has_overtime else "לא",
        GAME_URLS: ", ".join(game.game_url),
        MACCABI_PLAYERS: get_players_events_for_template(game.maccabi_players),
        OPPONENT_PLAYERS: get_players_events_for_template(game.opponent_players)
    }

    return template_arguments


def handle_existing_page(game_page: pw.page.Page, game: BasketballGame):
    if JUST_EVENTS:
        parsed_mw_text = mwparserfromhell.parse(game_page.text)
        football_game_template = parsed_mw_text.filter_templates(football_games_template_name)[0]

        arguments = __get_football_game_template_with_maccabistats_game_value(game)

        football_game_template.add(PLAYERS_EVENTS, arguments[PLAYERS_EVENTS])

        game_page.text = parsed_mw_text

    else:
        parsed_mw_text = mwparserfromhell.parse(game_page.text)
        football_game_template = parsed_mw_text.filter_templates(football_games_template_name)[0]

        arguments = __get_football_game_template_with_maccabistats_game_value(game)

        for argument_name, argument_value in arguments.items():
            if str(argument_value) != football_game_template.get(argument_name).value and SHOULD_SHOW_DIFF:
                logging.info("Found diff between arguments on this argument_name: {arg_name}\n"
                             "existing value: {existing_value}\nnew_value: {new_value}".
                             format(arg_name=argument_name,
                                    existing_value=football_game_template.get(argument_name).value,
                                    new_value=argument_value))

                football_game_template.add(argument_name, argument_value)

        game_page.text = parsed_mw_text

        if REFRESH_PAGES:
            from random import randint
            game_page.text += "<!--{num}-->".format(num=randint(0, 10000))


def handle_new_page(game_page: pw.page.Page, game: BasketballGame):
    basketball_template = Template(basketball_games_template_name)

    arguments = __get_football_game_template_with_maccabistats_game_value(game)

    for argument_name, argument_value in arguments.items():
        basketball_template.add(argument_name, argument_value)

    game_page.text = str(basketball_template)


def handle_game(game: BasketballGame, overwrite_existing_pages: bool = True):
    logging.info(f"Checking game : {game.game_date}")

    page_name = generate_page_name_from_game(game)
    game_page = pw.Page(site, page_name)
    page_exists = game_page.exists()

    if page_exists and not overwrite_existing_pages:
        logging.info(f"Don't edit existing pages, skipping: {page_name}")
        return

    if page_exists:
        logging.info(f"Page {page_name} already exists, checking for updates...")
        handle_existing_page(game_page, game)
    else:
        logging.info(f"Page {page_name} does not exist, creating...")
        handle_new_page(game_page, game)

    if not SHOULD_SAVE:
        logging.info(f"Not saving {game_page.title()}, just showing diff")
        return

    logging.info(f"Saving {game_page.title()}")
    game_page.save(summary="MaccabiBot - Uploading basketball games")

    logging.info(f"Prettifying {game_page.title()}")
    prettify_game_page_main_template(game_page)


def upload_basketball_games_to_maccabipedia(games: list[BasketballGame]):
    for game in games:
        handle_game(game, overwrite_existing_pages=False)


if __name__ == '__main__':
    logging.info(f"Should save? : {SHOULD_SAVE}, should show diff?: {SHOULD_SHOW_DIFF}")
    upload_basketball_games_to_maccabipedia(load_basketball_games())
    logging.info("Finish to upload basketball games to Maccabipedia")
