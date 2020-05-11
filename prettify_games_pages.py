import logging

import mwparserfromhell as mw

import pywikibot as pw
from pywikibot import pagegenerators

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

site = pw.Site()

games_page_prefix = "משחק:"
games_template_name = "קטלוג משחקים"

SHOULD_SAVE = True
SHOULD_SHOW_DIFF = False


def iterate_games_pages():
    """
    :rtype: list of pywikibot.page.Page
    """
    games_template_page = pw.Page(site, games_template_name, ns="תבנית")
    for game_page in pagegenerators.ReferringPageGenerator(games_template_page):
        if not game_page.title().startswith(games_page_prefix):
            logging.debug(f"Skipping ({game_page.title()} with uses '{games_template_name}' but does not start with '{games_page_prefix}' prefix")
            continue

        yield game_page


def _save_page_changes(game_page, new_text):
    """
    :type game_page: pywikibot.page.Page
    :type new_text: str
    """
    if game_page.text == new_text:
        return

    if SHOULD_SHOW_DIFF:
        pw.showDiff(game_page.text, new_text)
    if not SHOULD_SAVE:
        logging.info(f"SHOULD_SAVE=False, dont saving changes for page: {game_page.title()}")
        return

    game_page.text = new_text
    game_page.save(summary="MaccabiBot - Prettify games pages", botflag=True)


def matches_games_template(*args, **kwargs):
    return args[0].name.strip() == games_template_name


def prettify_game_page_main_template(game_page):
    """
    :type game_page: pywikibot.page.Page
    """
    parsed_mw_text = mw.parse(game_page.text)
    templates = parsed_mw_text.filter_templates(matches=matches_games_template)
    if not templates:
        logging.warning(f"Found no game template in this page: {game_page.title()}")
        return

    game_template = templates[0]

    # In order to make the first param in a new line, we will add a new line after the template name:
    if not game_template.name.endswith("\n"):
        game_template.name = f"{game_template.name}\n"

    for param in game_template.params:
        # Every param value should end with a new line (so the next param name+value will be in a new line)
        if not param.value.endswith("\n"):
            param.value = f"{param.value}\n"

        # Players description value should start with new line - more readable. Avoid mistakes in other params by disable it there
        if param.name == "אירועי שחקנים":
            if not param.value.startswith("\n"):
                param.value = f"\n{param.value}"
        else:
            if param.value.startswith("\n") and param.value != "\n":  # The value may be "empty" and contain only new line - that ok
                param.value = param.value.lstrip("\n")

        # Param name should not contain new lines - that may cause two "|" (param definition) to be at the same line
        param.name = param.name.strip("\n")

    _save_page_changes(game_page, parsed_mw_text)


def main():
    logging.info("Should save : {save}".format(save=SHOULD_SAVE))
    logging.info("Should show diff: {diff}\n".format(diff=SHOULD_SHOW_DIFF))

    logging.info("\nIterating all pages that uses football games template:")
    for game_page in iterate_games_pages():
        prettify_game_page_main_template(game_page)


if __name__ == '__main__':
    main()
