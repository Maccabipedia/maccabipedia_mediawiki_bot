import logging
from pathlib import Path

from pydantic import TypeAdapter

from basketball.basketball_game import BasketballGame, PlayerSummary
from pywikibot_boilerplate import run_boilerplate

run_boilerplate()

import mwparserfromhell
import tldextract
import pywikibot as pw
from mwparserfromhell.nodes.template import Template

site = pw.Site()
site.login()

from maccabipediabot.prettify_games_pages import prettify_game_page_main_template

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

EXAMPLE_GAMES_FILE_PATH = Path(r"C:\maccabi\basketball\games_for_upload.json")

basketball_games_template_name = "משחק כדורסל"
basketball_games_prefix = "כדורסל"

# Legend games templates args consts:s
GAME_DATE = "תאריך המשחק"
GAME_HOUR = "שעת המשחק"
SEASON = "עונה"
COMPETITION = "מפעל"
FIXTURE = "שלב במפעל"
OPPONENT_NAME = "שם יריבה"
HOME_OR_AWAY = "בית חוץ"
ARENA = "אולם"
MACCABI_GAME_SCORE = "תוצאת משחק מכבי"
OPPONENT_GAME_SCORE = "תוצאת משחק יריבה"
MACCABI_COACH = "מאמן מכבי"
OPPONENT_COACH = "מאמן יריבה"
REFEREE = "שופט ראשי"
REFEREE_ASSISTERS = "עוזרי שופט"
CROWD = "כמות קהל"
HIGHLIGHTS_VIDEO = "תקציר וידאו"
HIGHLIGHTS_VIDEO2 = "תקציר וידאו2"
FULL_GAME_VIDEO = "משחק מלא"
FULL_GAME_VIDEO2 = "משחק מלא2"
BROADCAST = "גוף שידור"
GAME_SUMMARY = "סיכום משחק"
IS_OVERTIME = "הארכה"
ARTICLE1 = "כתבה1"
ARTICLE2 = "כתבה2"
MACCABI_PLAYERS = 'שחקנים מכבי'
OPPONENT_PLAYERS = 'שחקנים יריבה'
FIRST_QUARTER_MACCABI_POINTS = 'נקודות מכבי רבע1'
SECOND_QUARTER_MACCABI_POINTS = 'נקודות מכבי רבע2'
THIRD_QUARTER_MACCABI_POINTS = 'נקודות מכבי רבע3'
FOURTH_QUARTER_MACCABI_POINTS = 'נקודות מכבי רבע4'
FIRST_OVERTIME_MACCABI_POINTS = 'נקודות מכבי הארכה1'
SECOND_OVERTIME_MACCABI_POINTS = 'נקודות מכבי הארכה2'
THIRD_OVERTIME_MACCABI_POINTS = 'נקודות מכבי הארכה3'
FOURTH_OVERTIME_MACCABI_POINTS = 'נקודות מכבי הארכה4'
FIRST_QUARTER_OPPONENT_POINTS = 'נקודות יריבה רבע1'
SECOND_QUARTER_OPPONENT_POINTS = 'נקודות יריבה רבע2'
THIRD_QUARTER_OPPONENT_POINTS = 'נקודות יריבה רבע3'
FOURTH_QUARTER_OPPONENT_POINTS = 'נקודות יריבה רבע4'
FIRST_OVERTIME_OPPONENT_POINTS = 'נקודות יריבה הארכה1'
SECOND_OVERTIME_OPPONENT_POINTS = 'נקודות יריבה הארכה2'
THIRD_OVERTIME_OPPONENT_POINTS = 'נקודות יריבה הארכה3'
FOURTH_OVERTIME_OPPONENT_POINTS = 'נקודות יריבה הארכה4'
FIRST_HALF_MACCABI_POINTS = 'נקודות מכבי חצי1'
SECOND_HALF_MACCABI_POINTS = 'נקודות מכבי חצי2'
FIRST_HALF_OPPONENT_POINTS = 'נקודות יריבה חצי1'
SECOND_HALF_OPPONENT_POINTS = 'נקודות יריבה חצי2'


REFRESH_PAGES = False
JUST_EVENTS = True
SHOULD_SAVE = True
SHOULD_SHOW_DIFF = True
SHOULD_CHECK_FOR_UPDATE_IN_EXISTING_PAGES = False


def load_basketball_games() -> list[BasketballGame]:
    games_text = EXAMPLE_GAMES_FILE_PATH.read_text(encoding='utf-8')
    games = TypeAdapter(list[BasketballGame]).validate_json(games_text)
    return games


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

def format_url(game_url: str) -> str:
    main_domain = tldextract.extract(game_url).domain
    return f"[{game_url} עמוד המשחק באתר {main_domain}]"

def __get_football_game_template_with_maccabistats_game_value(game: BasketballGame) -> dict[str, str]:
    template_arguments = {
        GAME_DATE: str(game.game_date.strftime("%d-%m-%Y")),
        # We don't want to upload the hour if it's equal to zero (that an unknown time)
        GAME_HOUR: game.game_date.hour if game.game_date.hour != 0 else '',
        SEASON: game.season,
        COMPETITION: game.competition,
        FIXTURE: game.fixture,
        OPPONENT_NAME: game.opponent_name,
        HOME_OR_AWAY: 'בית' if game.is_home_game else 'חוץ',
        ARENA: game.arena,
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
        FIRST_HALF_MACCABI_POINTS: game.first_half_maccabi_points,
        SECOND_HALF_MACCABI_POINTS: game.second_half_maccabi_points,
        FIRST_HALF_OPPONENT_POINTS: game.first_half_opponent_points,
        SECOND_HALF_OPPONENT_POINTS: game.second_half_opponent_points,
        MACCABI_GAME_SCORE: game.maccabi_points,
        OPPONENT_GAME_SCORE: game.opponent_points,
        MACCABI_COACH: game.maccabi_coach,
        OPPONENT_COACH: game.opponent_coach,
        REFEREE: game.referee,
        REFEREE_ASSISTERS: ", ".join(game.referee_assistants),
        CROWD: game.crowd,
        HIGHLIGHTS_VIDEO: "",
        HIGHLIGHTS_VIDEO2: "",
        FULL_GAME_VIDEO: "",
        FULL_GAME_VIDEO2: "",
        BROADCAST: "",
        GAME_SUMMARY: ""
    }

    if game.has_overtime:
        template_arguments[IS_OVERTIME] = "כן"

    if game.game_url:
        template_arguments[ARTICLE1] = format_url(game.game_url[0])
        if len(game.game_url) > 1:
            template_arguments[ARTICLE2] = format_url(game.game_url[1])

    # Players events should be last:
    template_arguments[MACCABI_PLAYERS] = get_players_events_for_template(game.maccabi_players)
    template_arguments[OPPONENT_PLAYERS] = get_players_events_for_template(game.opponent_players)

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
        #game_page.delete(reason="MaccabiBot - Deleting basketball game page")
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
    games = load_basketball_games()
    upload_basketball_games_to_maccabipedia(games[5:10] + games[100:105])
    logging.info("Finish to upload basketball games to Maccabipedia")
