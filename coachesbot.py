import pywikibot as pw
from maccabistats import get_maccabi_stats
from pywikibot import pagegenerators, Category
from mwparserfromhell.nodes.template import Template
import mwparserfromhell
import logging
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))

player_template_name = "תבנית:פרופיל"
coaches_category_name = "קטגוריה:מאמנים_ראשיים"

NAME = "שם מלא"
SQUAD_ROLE = "תפקיד מקצועי"

site = pw.Site()

SHOULD_SAVE = True
SHOULD_SHOW_DIFF = True
SHOULD_CHECK_FOR_UPDATE_IN_EXISTING_PAGES = False


def get_players_to_add():
    maccabi_games = get_maccabi_stats()
    all_players_names_without_dups = list(maccabi_games.available_coaches)
    return sorted(all_players_names_without_dups)


def get_all_football_players_category_pages():
    players_category = Category(site, coaches_category_name)
    players_category_pages = list(pagegenerators.CategorizedPageGenerator(players_category))
    return players_category_pages


def get_football_player_template_object():
    return Template(player_template_name)


def generate_page_name_from_player_name(player_name):
    """
    :type player_name: str
    :rtype: str
    """

    page_name = "{name}".format(name=player_name)

    return page_name


def __get_football_player_template(player_name):
    """
    Return dict of the player, atm just the name & does_maccabi_player="כן".
    :type player_name: str
    :return: dict from str to str
    """

    template_arguments = dict()

    template_arguments[NAME] = player_name
    template_arguments[SQUAD_ROLE] = "מאמן"

    return template_arguments


def handle_existing_page(player_page, player_name):
    """
    :type player_page: pywikibot.page.Page
    :type player_name: str
    """

    parsed_mw_text = mwparserfromhell.parse(player_page.text)
    football_player_template = parsed_mw_text.filter_templates(player_template_name)[0]

    arguments = __get_football_player_template(player_name)

    for argument_name, argument_value in arguments.items():
        if str(argument_value) != football_player_template.get(argument_name).value and SHOULD_SHOW_DIFF:
            logger.info("Found diff between arguments on this argument_name: {arg_name}\n"
                        "existing value: {existing_value}\nnew_value: {new_value}".
                        format(arg_name=argument_name, existing_value=football_player_template.get(argument_name).value,
                               new_value=argument_value))

            football_player_template.add(argument_name, argument_value)

    player_page.text = parsed_mw_text


def handle_new_page(player_page, player_name):
    """
    :type player_page: pywikibot.page.Page
    :type player_name: str
    """

    football_player_template = get_football_player_template_object()

    arguments = __get_football_player_template(player_name)

    for argument_name, argument_value in arguments.items():
        football_player_template.add(argument_name, argument_value)

    player_page.text = str(football_player_template)


def page_was_probably_created_with_bot(player_page):
    parsed_mw_text = mwparserfromhell.parse(player_page.text)
    player_template = parsed_mw_text.filter_templates(player_template_name)[0]

    if any("שחקן מכבי" in t for t in player_template.params):
        #  patch - dont touch players
        return False
    # We will add just two params atm - name and does_maccabi_player.
    if len(player_template.params) == 2:
        return True
    else:
        return False


def create_or_update_player_page(player_name):
    logger.info("\nHandling  player - {name}".format(name=player_name))
    page_name = generate_page_name_from_player_name(player_name)
    save_this_page = True
    player_page = pw.Page(site, page_name)

    # handle_new_page & handle_existing_page changes the player_page.text attribute.
    if player_page.exists():
        if not page_was_probably_created_with_bot(player_page):
            save_this_page = False
            logger.info("Saw page {name} that probably wasn't created with bot, continue.".format(name=player_name))
        else:
            logger.info("Page : {name} exists, check for updates\n".format(name=page_name))
            handle_existing_page(player_page, player_name)
    else:
        logger.info("Page : {name} does not exists, creating\n".format(name=page_name))
        handle_new_page(player_page, player_name)

    if SHOULD_SAVE and save_this_page:
        logger.info("Saving {name}".format(name=player_page.title()))
        player_page.save(summary="MaccabiBot - Add Coaches")
    else:
        logger.info("Not saving {name}".format(name=player_page.title()))


def get_players_that_has_existing_pages(players_names):
    existing_players = []
    existing_players_pages = get_all_football_players_category_pages()
    for player_page in existing_players_pages:
        page_name_as_player_name = player_page.title(withNamespace=False)  # Remove "שחקן:"
        if page_name_as_player_name in players_names:
            existing_players.append(page_name_as_player_name)

    return existing_players


def main():
    logger.info("All pages in football players category:")
    for p in get_all_football_players_category_pages():
        logger.info(p)

    logger.info("Should save : {save}".format(save=SHOULD_SAVE))
    logger.info("Should show diff: {diff}\n".format(diff=SHOULD_SHOW_DIFF))

    players_names = get_players_to_add()[1:]  #Patch without Cant Found Coach

    for player in players_names:
        create_or_update_player_page(player)

    logger.info("Finished adding new players.")

    if SHOULD_CHECK_FOR_UPDATE_IN_EXISTING_PAGES:
        logger.info("Now handling existing players:")
        existing_players = get_players_that_has_existing_pages(players_names)
        [create_or_update_player_page(player) for player in existing_players]
    else:
        logger.info("Dont check for updates in existing pages")

    logger.info("Finished handling existing players.")


if __name__ == '__main__':
    main()
