import pywikibot as pw
from maccabistats import get_maccabi_stats
from pywikibot import pagegenerators, Category
from mwparserfromhell.nodes.template import Template
import mwparserfromhell
import logging

logger = logging.getLogger(__name__)

games_pages_temp_prefix = "דמיקולו"
games_template_name = "תבנית:נסיון_משחקים_אגדיים"
games_template_name_for_wpt = "{{נסיון_משחקים_אגדיים}}"
legend_games_category_text = "[[קטגוריה:משחקים_אגדיים]]"

# Legend games templates args consts:
GAME_ID = "תאריך_המשחק"
GAME_HOUR = "שעת_המשחק"
SEASON = "עונה"
COMPETITION = "מפעל"
ROUND_IN_COMPETITION = "מחזור_במפעל"
OPPONENT_NAME = "שם_יריבה"
HOME_OR_AWAY = "בית_חוץ"
STADIUM = "אצטדיון"
MACCABI_RESULT = "תוצאת_משחק_מכבי"
OPPONENT_RESULT = "תוצאת_משחק_יריבה"
MACCABI_COACH = "מאמן_מכבי"
OPPONENT_COACH = "מאמן_יריבה"
REFEREE = "שופט"
CROWD = "כמות_קהל"
BROADCAST = "גוף_שידור"
COSTUME = "מכבי_תלבושת"

site = pw.Site()

SHOULD_SAVE = False
SHOULD_SHOW_DIFF = True


def get_games_to_add(number):
    maccabi_games = get_maccabi_stats()
    top_wins = sorted(maccabi_games.games, key=lambda g: g.maccabi_score_diff)

    return top_wins[0:number]


def get_legend_games_template_arguments():
    legend_games_template_page = pw.Page(site, games_template_name)
    legend_games_template_text = mwparserfromhell.parse(legend_games_template_page.text)
    return legend_games_template_text.filter_arguments()


def get_all_pages_that_use_legend_games_template():
    legend_games_template_page = pw.Page(site, games_template_name)
    legend_games_templates_pages_iterator = pagegenerators.ReferringPageGenerator(legend_games_template_page)
    return list(legend_games_templates_pages_iterator)


def get_all_legend_games_category_pages():
    games_category = Category(site, 'קטגוריה:משחקים_אגדיים')
    games_category = list(pagegenerators.CategorizedPageGenerator(games_category))
    return games_category


def get_legend_games_template_object():
    return Template(games_template_name_for_wpt)


def generate_page_name_from_game(game):
    """
    :type game: maccabistats.models.game_data.GameData
    :rtype: str
    """

    page_name = "{prefix}_{name1}_{name2}_{date}".format(prefix=games_pages_temp_prefix,
                                                         name1=game.maccabi_team.name,
                                                         name2=game.not_maccabi_team.name,
                                                         date=game.date_as_hebrew_string)

    return page_name


def __get_legend_game_template_with_maccabistats_game_value(game):
    """
    Return dict of the (template arguments->data taken from game).
    :type game: maccabistats.models.game_data.GameData
    :return: dict from str to str
    """

    template_arguments = dict()

    template_arguments[GAME_ID] = str(game.date.date())
    template_arguments[GAME_HOUR] = game.date.hour
    template_arguments[SEASON] = "2000-2001"
    template_arguments[COMPETITION] = game.competition
    template_arguments[ROUND_IN_COMPETITION] = game.fixture
    template_arguments[OPPONENT_NAME] = game.not_maccabi_team.name
    template_arguments[HOME_OR_AWAY] = "Home" if game.is_maccabi_home_team else "Away"
    template_arguments[STADIUM] = game.stadium
    template_arguments[MACCABI_RESULT] = game.maccabi_team.score
    template_arguments[OPPONENT_RESULT] = game.not_maccabi_team.score
    template_arguments[MACCABI_COACH] = game.maccabi_team.coach
    template_arguments[OPPONENT_COACH] = game.not_maccabi_team.coach
    template_arguments[REFEREE] = game.referee
    template_arguments[CROWD] = game.crowd
    template_arguments[BROADCAST] = "ערוץ 1"
    template_arguments[COSTUME] = "תלבושת ביתית 2000-2001"

    return template_arguments


def handle_existing_page(game_page, game):
    """
    :type game_page: pywikibot.page.Page
    :type game: maccabistats.models.game_data.GameData
    """

    parsed_mw_text = mwparserfromhell.parse(game_page.text)
    legend_template = parsed_mw_text.filter_templates(games_template_name)[0]

    arguments = __get_legend_game_template_with_maccabistats_game_value(game)

    for argument_name, argument_value in arguments.items():
        if str(argument_value) != legend_template.get(argument_name).value and SHOULD_SHOW_DIFF:
            logger.info("Found diff between arguments on this argument_name: {arg_name}\n"
                        "existing value: {existing_value}\n new_value: {new_value}".
                        format(arg_name=argument_name, existing_value=legend_template.get(argument_name).value,
                               new_value=argument_value))

            legend_template.add(argument_name, argument_value)

    game_page.text = parsed_mw_text


def handle_new_page(game_page, game):
    """
    :type game_page: pywikibot.page.Page
    :type game: maccabistats.models.game_data.GameData
    """

    legend_games_template = get_legend_games_template_object()

    arguments = __get_legend_game_template_with_maccabistats_game_value(game)

    for argument_name, argument_value in arguments.items():
        legend_games_template.add(argument_name, argument_value)

    game_page.text = str(legend_games_template)


def add_games_page(game):
    page_name = generate_page_name_from_game(game)

    game_page = pw.Page(site, page_name)

    if game_page.exists():
        logger.info("Page : {name} exists, exiting".format(name=page_name))
        handle_existing_page(game_page, game)
    else:
        logger.info("Page : {name} does not exists, continue".format(name=page_name))
        handle_new_page(game_page, game)

    # handle_new_page & handle_existing_page changes the game_page.text attribute.
    game_page.text += legend_games_category_text

    if SHOULD_SAVE:
        logger.info("Saving {name}".format(name=game_page.title()))
        game_page.save(summary="MaccabiBot - Legend Games Template")
    else:
        logger.info("Not saving {name}".format(name=game_page.title()))


def main():
    logger.info("All pages in legend games category:")
    for p in get_all_legend_games_category_pages():
        logger.info(p)
        logger.info("\n")

    logger.info("Legend page template args:")
    for a in get_legend_games_template_arguments():
        logger.info(a)
        logger.info("\n")

        logger.info("All pages in legend games template:")
    for p in get_all_pages_that_use_legend_games_template():
        logger.info(p)
        logger.info("\n")

    games = get_games_to_add(5)
    add_games_page(games[4])


if __name__ == '__main__':
    main()
