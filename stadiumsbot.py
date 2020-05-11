import pywikibot as pw
from maccabistats import get_maccabi_stats_as_newest_wrapper
from mwparserfromhell.nodes.template import Template
import logging
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))

stadium_template_name = "אצטדיון"

site = pw.Site()

SHOULD_SAVE = True


def get_stadiums_to_add():
    maccabi_games = get_maccabi_stats_as_newest_wrapper()
    all_stadiums_names_without_dups = list(maccabi_games.available_stadiums)
    return sorted(all_stadiums_names_without_dups)


def get_football_stadium_template_object():
    return Template(stadium_template_name)


def generate_page_name_from_stadium_name(stadium_name):
    page_name = "{name}".format(name=stadium_name)

    return page_name


def handle_new_page(stadium_page):
    stadium_template = get_football_stadium_template_object()
    stadium_page.text = str(stadium_template)


def create_stadium_page(stadium_name):
    logger.info("\nHandling  stadium - {name}".format(name=stadium_name))
    page_name = generate_page_name_from_stadium_name(stadium_name)
    stadium_page = pw.Page(site, page_name)

    if stadium_page.exists():
        print(f"Exists - {stadium_name}, Stopping")
        return

    handle_new_page(stadium_page)

    if SHOULD_SAVE:
        stadium_page.save(summary="MaccabiBot - Add stadiums")


def main():
    stadiums_names = get_stadiums_to_add()[1:]  # Patch without ""

    for stadium_name in stadiums_names:
        create_stadium_page(stadium_name)

    logger.info("Finished adding new players.")


if __name__ == '__main__':
    main()
