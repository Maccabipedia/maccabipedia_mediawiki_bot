import pywikibot as pw
from maccabistats import get_maccabi_stats_as_newest_wrapper
from pywikibot import pagegenerators, Category
from mwparserfromhell.nodes.template import Template
import logging
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))

team_template_name = "תבנית:קבוצה"
coaches_category_name = "קטגוריה:מאמנים_ראשיים"

site = pw.Site()

SHOULD_SAVE = True


def get_teams_to_add():
    maccabi_games = get_maccabi_stats_as_newest_wrapper()
    all_teams_names_without_dups = list(maccabi_games.available_opponents)
    return sorted(all_teams_names_without_dups)


def get_all_football_players_category_pages():
    players_category = Category(site, coaches_category_name)
    players_category_pages = list(pagegenerators.CategorizedPageGenerator(players_category))
    return players_category_pages


def get_football_team_template_object():
    return Template(team_template_name)


def generate_page_name_from_team_name(team_name):
    page_name = "{name}".format(name=team_name)

    return page_name


def handle_new_page(team_page, team_name):
    team_template = get_football_team_template_object()
    team_page.text = str(team_template)


def create_team_page(team_name):
    logger.info("\nHandling  team - {name}".format(name=team_name))
    page_name = generate_page_name_from_team_name(team_name)
    team_page = pw.Page(site, page_name)

    if team_page.exists():
        print(f"Exists - {team_name}")
        return

    handle_new_page(team_page, team_name)

    team_page.save(summary="MaccabiBot - Add Teams")


def main():
    teams_names = get_teams_to_add()[1:]  # Patch without Cant Found Coach

    for team_name in teams_names:
        create_team_page(team_name)

    logger.info("Finished adding new players.")


if __name__ == '__main__':
    main()
