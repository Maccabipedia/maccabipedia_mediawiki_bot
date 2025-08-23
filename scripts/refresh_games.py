import logging
import sys

import pywikibot as pw
from maccabistats import load_from_maccabipedia_source
from maccabistats.error_finder.error_finder import ErrorsFinder

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))

site = pw.Site()
site.login()

football_games_prefix = "משחק"


def generate_page_name_from_game(game):
    """
    :type game: maccabistats.models.game_data.GameData
    :rtype: str
    """

    page_name = "{prefix}: {date} {home_team} נגד {away_team} - {competition}".format(prefix=football_games_prefix,
                                                                                      date=game.date.strftime(
                                                                                          '%d-%m-%Y'),
                                                                                      home_team=game.home_team.name,
                                                                                      away_team=game.away_team.name,
                                                                                      competition=game.competition)

    return page_name


if __name__ == '__main__':
    mo = load_from_maccabipedia_source().official_games
    e = ErrorsFinder(mo)

    for game in e.get_games_with_missing_goals_events():
        logger.info(f'handling game: {game}')

        page_name = generate_page_name_from_game(game)
        game_page = pw.Page(site, page_name)

        if game_page.exists():
            game_page.purge()
            game_page.touch(botflag=True)

    logger.info(f'Finished')
