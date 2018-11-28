import pywikibot as pw
from maccabistats import get_maccabi_stats_as_newest_wrapper
import logging
from datetime import timedelta
import sys
import re
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))

site = pw.Site()

REFRESH_PAGES = False
SHOULD_SAVE = True
SHOULD_SHOW_DIFF = True
SHOULD_CHECK_FOR_UPDATE_IN_EXISTING_PAGES = False


def get_games_to_add():
    maccabi_games = get_maccabi_stats_as_newest_wrapper()
    return maccabi_games


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


def find_game_by_season_and_fixture(g, unformatted_season, fixture):
    season = unformatted_season[:4] + "/" + unformatted_season[4:]

    possible_games = [gg for gg in g if gg.fixture == f"מחזור {fixture}" and gg.season == f"{season}"]

    if not possible_games:
        raise RuntimeError(f"Could not find any games at season: {season} and fixture: {fixture}")

    if len(possible_games) > 1:
        raise RuntimeError(f"Found {len(possible_games)} of possible games at season: {season} and fixture: {fixture}")

    return possible_games[0]


def get_full_game_links_json():
    with open(r"C:\maccabipedia\videos\full_games.json") as f:
        return json.load(f)


def test(page_name, full_game_link):
    page = pw.Page(site, page_name)

    if not page.exists():
        raise RuntimeError("Cannot find this page")

    replace_me = "גוף שידור="

    new_line_pipe = "|"
    full_game_param_name = "משחק מלא="

    add_me = f"{full_game_param_name}{full_game_link}"

    if full_game_param_name in page.text:
        raise RuntimeError("This game already has fll game link")

    # Something bad happen here when debugging page variable in pycharm watch window, dont expand 'page'
    without_link = page.text
    with_full_game_link = without_link.replace(replace_me, f"{replace_me} {new_line_pipe} {add_me}")

    page.text = with_full_game_link
    if "http" in page.text:
        page.save(summary="Adding full game link")


def main():
    logger.info("Should save : {save}".format(save=SHOULD_SAVE))
    logger.info("Should show diff: {diff}\n".format(diff=SHOULD_SHOW_DIFF))

    g = get_games_to_add()

    links = get_full_game_links_json()

    for season in links:
        for fixture in links[season]:
            full_game_link = links[season][fixture]
            try:
                current_game = find_game_by_season_and_fixture(g, season, fixture)
                current_page_name = generate_page_name_from_game(current_game)
                test(current_page_name, full_game_link)
            except Exception as e:
                print(e)


if __name__ == '__main__':
    main()
