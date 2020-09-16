import logging

import mwparserfromhell as mw

import pywikibot as pw
from pywikibot import pagegenerators

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

site = pw.Site()

games_page_prefix = "משחק:"
games_template_name = "קטלוג משחקים"

OLD_CUSTOM_FIELD_NAME = 'מכבי תלבושת'
NEW_CUSTOM_FIELD_NAME = 'מדים'

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
        logging.info(f'Same content, skipping saving this page: {game_page.title()}')
        return

    if SHOULD_SHOW_DIFF:
        pw.showDiff(game_page.text, new_text)
    if not SHOULD_SAVE:
        logging.info(f"SHOULD_SAVE=False, dont saving changes for page: {game_page.title()}")
        return

    game_page.text = new_text
    game_page.save(summary="MaccabiBot - Change custom field name", botflag=True)


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

    logging.info(f'Handling page: {game_page.title()}')

    if game_template.has(OLD_CUSTOM_FIELD_NAME):
        logging.info('Removing old custom field name')
        game_template.remove(OLD_CUSTOM_FIELD_NAME)

    if game_template.has(NEW_CUSTOM_FIELD_NAME):
        logging.debug('Page has new custom field name, doing nothing!')
    else:
        logging.info('Adding to this page the new custom field name!')
        # New line is to see each parameter in new line
        add_before_this_param = 'תקציר וידאו' if game_template.has('תקציר וידו') else 'אירועי שחקנים'

        game_template.add(name=NEW_CUSTOM_FIELD_NAME, value='', before=add_before_this_param)

    _save_page_changes(game_page, parsed_mw_text)


def main():
    logging.info("Should save : {save}".format(save=SHOULD_SAVE))
    logging.info("Should show diff: {diff}\n".format(diff=SHOULD_SHOW_DIFF))

    logging.info("\nIterating all pages that uses football games template:")
    for game_page in iterate_games_pages():
        prettify_game_page_main_template(game_page)


if __name__ == '__main__':
    main()
