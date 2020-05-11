import pywikibot as pw
from maccabistats import get_maccabi_stats_as_newest_wrapper
from mwparserfromhell.nodes.template import Template
import logging
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))

referee_template_name = "שופט"

site = pw.Site()

SHOULD_SAVE = True


def get_referees_to_add():
    maccabi_games = get_maccabi_stats_as_newest_wrapper()
    all_referees_names_without_dups = list(maccabi_games.available_referees)
    return sorted(all_referees_names_without_dups)


def get_football_referee_template_object():
    return Template(referee_template_name)


def generate_page_name_from_referee_name(referee_name):
    page_name = "{name}".format(name=referee_name)

    return page_name


def handle_new_page(referee_page):
    referee_template = get_football_referee_template_object()
    referee_page.text = str(referee_template)


def create_referee_page(referee_name):
    logger.info("\nHandling  referee - {name}".format(name=referee_name))
    page_name = generate_page_name_from_referee_name(referee_name)
    referee_page = pw.Page(site, page_name)

    if referee_page.exists():
        print(f"Exists - {referee_name}, Stopping")
        return

    handle_new_page(referee_page)

    if SHOULD_SAVE:
        referee_page.save(summary="MaccabiBot - Add referees")


def main():
    referees_names = get_referees_to_add()[2:]  # Patch without "" and without "cant find referee"

    for referee_name in referees_names:
        create_referee_page(referee_name)

    logger.info("Finished adding new players.")


if __name__ == '__main__':
    main()
