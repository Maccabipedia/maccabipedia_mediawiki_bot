import logging
from typing import List

import mwparserfromhell as mw
import pywikibot as pw
import pywikibot.page
from pywikibot import pagegenerators, Category

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)

site = pw.Site()

games_template_name = "משחק כדורעף"
volleyball_games_category_name = "קטגוריה:משחקי כדורעף"

SHOULD_SAVE = True
SHOULD_SHOW_DIFF = False


def iterate_games_pages() -> List[pywikibot.page.Page]:
    """
    :rtype: list of pywikibot.page.Page
    """

    volleyball_games_category = Category(site, volleyball_games_category_name)

    for index, game_page in enumerate(pagegenerators.CategorizedPageGenerator(volleyball_games_category)):
        logging.info(f"Page number: {index}")

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
    game_page.save(summary="MaccabiBot - Split sets parameter", botflag=True)


def matches_games_template(*args, **kwargs):
    return args[0].name.strip() == games_template_name


def split_old_set_param_to_new_format(game_template: mw.nodes.template.Template, current_param_name: str,
                                      maccabi_is_home: bool) -> None:
    if not game_template.has(current_param_name):
        return
    if not game_template.get(current_param_name).value.strip():
        game_template.add(f"{current_param_name} מכבי", '')
        game_template.add(f"{current_param_name} יריבה", '')
        return  # It may empty as no one filled it, in this case we will just add the params but without value

    scores = game_template.get(current_param_name).value.strip().replace("'", "").split(":")
    if len(scores) < 2:
        raise RuntimeError(f'Could not find results for both teams! {current_param_name}, {game_template}')

    game_template.add(f"{current_param_name} מכבי", scores[int(maccabi_is_home)])
    game_template.add(f"{current_param_name} יריבה", scores[int(not maccabi_is_home)])


def reorganize_sets_params(game_page: pywikibot.page.Page) -> None:
    parsed_mw_text = mw.parse(game_page.text)
    templates = parsed_mw_text.filter_templates(matches=matches_games_template)
    if not templates:
        logging.warning(f"Found no game template in this page: {game_page.title()}")
        return

    game_template = templates[0]
    is_home_games_for_maccabi = game_page.title().find('מכבי תל אביב') < game_page.title().find('נגד')

    split_old_set_param_to_new_format(game_template, 'מערכה1', is_home_games_for_maccabi)
    split_old_set_param_to_new_format(game_template, 'מערכה2', is_home_games_for_maccabi)
    split_old_set_param_to_new_format(game_template, 'מערכה3', is_home_games_for_maccabi)
    split_old_set_param_to_new_format(game_template, 'מערכה4', is_home_games_for_maccabi)
    split_old_set_param_to_new_format(game_template, 'מערכה5', is_home_games_for_maccabi)
    split_old_set_param_to_new_format(game_template, 'מערכת זהב', is_home_games_for_maccabi)

    _save_page_changes(game_page, parsed_mw_text)


def main():
    logging.info("Should save : {save}".format(save=SHOULD_SAVE))
    logging.info("Should show diff: {diff}\n".format(diff=SHOULD_SHOW_DIFF))

    logging.info("\nIterating all pages that uses volleyball games template:")
    for game_page in iterate_games_pages():
        try:
            reorganize_sets_params(game_page)
        except Exception:
            logging.exception(f"Unknown exception, skipping this game: {game_page.title()}")


if __name__ == '__main__':
    main()
