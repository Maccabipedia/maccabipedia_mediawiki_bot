import pywikibot as pw
from maccabistats import get_maccabi_stats
from pywikibot import pagegenerators, Category
from mwparserfromhell.nodes.template import Template
import mwparserfromhell
import logging
from maccabistats_player_event import PlayerEvent
import sys
import re

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))

football_games_prefix = "משחק"
football_games_template_name = "תבנית:הצגת_משחק"
football_games_category_name = "קטגוריה:משחקים"

# Legend games templates args consts:
GAME_ID = "תאריך המשחק"
GAME_HOUR = "שעת המשחק"
DAY_OF_WEEK = "יום המשחק בשבוע"
SEASON = "עונה"
COMPETITION = "מפעל"
ROUND_IN_COMPETITION = "מחזור במפעל"
OPPONENT_NAME = "שם יריבה"
HOME_OR_AWAY = "בית חוץ"
STADIUM = "אצטדיון"
MACCABI_RESULT = "תוצאת משחק מכבי"
OPPONENT_RESULT = "תוצאת משחק יריבה"
MACCABI_COACH = "מאמן מכבי"
OPPONENT_COACH = "מאמן יריבה"
REFEREE = "שופט"
CROWD = "כמות קהל"
BROADCAST = "גוף שידור"
COSTUME = "מכבי תלבושת"
PLAYERS_EVENTS = "אירועי שחקנים"

site = pw.Site()

SHOULD_SAVE = True
SHOULD_SHOW_DIFF = True
SHOULD_CHECK_FOR_UPDATE_IN_EXISTING_PAGES = False


def get_games_to_add():
    maccabi_games = get_maccabi_stats()
    return maccabi_games


def get_football_games_template_arguments():
    legend_games_template_page = pw.Page(site, football_games_template_name)
    legend_games_template_text = mwparserfromhell.parse(legend_games_template_page.text)
    return legend_games_template_text.filter_arguments()


def get_all_pages_that_use_football_games_template():
    legend_games_template_page = pw.Page(site, football_games_template_name)
    legend_games_templates_pages_iterator = pagegenerators.ReferringPageGenerator(legend_games_template_page)
    return list(legend_games_templates_pages_iterator)


def get_all_football_games_category_pages():
    games_category = Category(site, football_games_category_name)
    games_category = list(pagegenerators.CategorizedPageGenerator(games_category))
    return games_category


def get_football_games_template_object():
    return Template(football_games_template_name)


def generate_page_name_from_game(game):
    """
    :type game: maccabistats.models.game_data.GameData
    :rtype: str
    """

    page_name = "{prefix}: {date} {home_team} נגד {away_team} - {competition}".format(prefix=football_games_prefix,
                                                                                      date=game.date.strftime('%d-%m-%Y'),
                                                                                      home_team=game.home_team.name,
                                                                                      away_team=game.away_team.name,
                                                                                      competition=game.competition)

    return page_name


def get_players_events_for_template(game):
    """
    Return the events as they should be written to template:
    the separator between players attributes is '::'
    the separator between players is ','
    :type game: maccabistats.models.game_data.GameData
    :return:
    """

    # Atm, no sub event type is supported.

    # Maccabi players
    unsorted_events = [
        PlayerEvent(player.name, player.number, player_event.time_occur, player_event.event_type.value, None)
        for player in game.maccabi_team.players
        for player_event in player.events]

    # Opponent players
    unsorted_events.extend(
        [PlayerEvent(player.name, player.number, player_event.time_occur.min, player_event.event_type.value, None)
         for player in game.not_maccabi_team.players
         for player_event in player.events])

    events = sorted(unsorted_events, key=lambda player_event: player_event.minute_occur)

    wikimedia_formatted_events = ",".join(
        "{name}::{number}::{event_type}::{minute_occur}\n".format(**player_event.__dict__)
        for player_event in events)

    return wikimedia_formatted_events


def __get_football_game_template_with_maccabistats_game_value(game):
    """
    Return dict of the (template arguments->data taken from game).
    :type game: maccabistats.models.game_data.GameData
    :return: dict from str to str
    """

    template_arguments = dict()

    template_arguments[GAME_ID] = str(game.date.strftime("%d-%m-%Y"))
    template_arguments[GAME_HOUR] = game.date.hour
    template_arguments[DAY_OF_WEEK] = (game.date.weekday() + 2) % 8  # weekday return 0 for monday, 6 for sunday.
    template_arguments[SEASON] = game.season
    template_arguments[COMPETITION] = game.competition
    template_arguments[ROUND_IN_COMPETITION] = "" if game.fixture == "No round found" else game.fixture  # Empty for unknown rounds
    template_arguments[OPPONENT_NAME] = game.not_maccabi_team.name
    template_arguments[HOME_OR_AWAY] = "בית" if game.is_maccabi_home_team else "חוץ"
    template_arguments[STADIUM] = game.stadium
    template_arguments[MACCABI_RESULT] = game.maccabi_team.score
    template_arguments[OPPONENT_RESULT] = game.not_maccabi_team.score
    template_arguments[MACCABI_COACH] = "" if game.maccabi_team.coach == "Cant found coach" else game.maccabi_team.coach
    template_arguments[OPPONENT_COACH] = "" if game.not_maccabi_team.coach == "Cant found coach" else game.not_maccabi_team.coach
    template_arguments[REFEREE] = "" if game.referee == "Cant found referee" else game.referee
    template_arguments[CROWD] = "" if game.crowd == "Cant found crowd" else game.crowd
    template_arguments[BROADCAST] = "ערוץ הכיבוד"
    template_arguments[COSTUME] = "תלבושת {place} {years}".format(place=template_arguments[HOME_OR_AWAY], years=game.season)
    template_arguments[PLAYERS_EVENTS] = get_players_events_for_template(game)

    return template_arguments


def handle_existing_page(game_page, game):
    """
    :type game_page: pywikibot.page.Page
    :type game: maccabistats.models.game_data.GameData
    """

    parsed_mw_text = mwparserfromhell.parse(game_page.text)
    football_game_template = parsed_mw_text.filter_templates(football_games_template_name)[0]

    arguments = __get_football_game_template_with_maccabistats_game_value(game)

    for argument_name, argument_value in arguments.items():
        if str(argument_value) != football_game_template.get(argument_name).value and SHOULD_SHOW_DIFF:
            logger.info("Found diff between arguments on this argument_name: {arg_name}\n"
                        "existing value: {existing_value}\nnew_value: {new_value}".
                        format(arg_name=argument_name, existing_value=football_game_template.get(argument_name).value,
                               new_value=argument_value))

            football_game_template.add(argument_name, argument_value)

    game_page.text = parsed_mw_text


def handle_new_page(game_page, game):
    """
    :type game_page: pywikibot.page.Page
    :type game: maccabistats.models.game_data.GameData
    """

    football_game_template = get_football_games_template_object()

    arguments = __get_football_game_template_with_maccabistats_game_value(game)

    for argument_name, argument_value in arguments.items():
        football_game_template.add(argument_name, argument_value)

    game_page.text = str(football_game_template)


def create_or_update_game_page(game):
    page_name = generate_page_name_from_game(game)

    game_page = pw.Page(site, page_name)

    # handle_new_page & handle_existing_page changes the game_page.text attribute.
    if game_page.exists():
        logger.info("Page : {name} exists, check for updates\n".format(name=page_name))
        handle_existing_page(game_page, game)
    else:
        logger.info("Page : {name} does not exists, creating\n".format(name=page_name))
        handle_new_page(game_page, game)

    logger.info("")  # Empty line
    if SHOULD_SAVE:
        logger.info("Saving {name}".format(name=game_page.title()))
        game_page.save(summary="MaccabiBot - Add games")
    else:
        logger.info("Not saving {name}".format(name=game_page.title()))


def get_games_that_has_existing_pages(games):
    existing_games = []
    existing_games_pages = get_all_football_games_category_pages()
    for game_page in existing_games_pages:
        game_date = re.search("([0-9]{2}\-[0-9]{2}\-[0-9]{4})", game_page.title()).group()
        game_date = game_date.replace("-", ".")  # For maccabistats format played(before\after).

        game = games.played_before(game_date).played_after(game_date)
        if len(game) > 1:
            raise RuntimeError("found more than one game for {date}".format(date=game_date))
        existing_games.append(game[0])

    return existing_games


def main():
    logger.info("All pages in football games category:")
    for p in get_all_football_games_category_pages():
        logger.info(p)

    # logger.info("\football page template args:")
    # for a in get_football_games_template_arguments():
    #    logger.info(a)

    logger.info("\nAll pages that uses football games template:")
    for p in get_all_pages_that_use_football_games_template():
        logger.info(p)
    logger.info("")  # Empty line

    logger.info("Should save : {save}".format(save=SHOULD_SAVE))
    logger.info("Should show diff: {diff}\n".format(diff=SHOULD_SHOW_DIFF))

    games = get_games_to_add()

    # from random import randint
    # for i in range(20):
    #   create_or_update_game_page(games[randint(0, 2000)])

    for game in games[-80:]:
        create_or_update_game_page(game)

    logger.info("Finished adding new games.")

    if SHOULD_CHECK_FOR_UPDATE_IN_EXISTING_PAGES:
        logger.info("Now handling existing games:")
        existing_games = get_games_that_has_existing_pages(games)
        [create_or_update_game_page(game) for game in existing_games]
    else:
        logger.info("Dont check for updates in existing pages")

    logger.info("Finished handling existing games.")


if __name__ == '__main__':
    main()
