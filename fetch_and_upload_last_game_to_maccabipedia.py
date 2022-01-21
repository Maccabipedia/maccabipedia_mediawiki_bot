import logging
import os

from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats
from .gamesbot import upload_games_to_maccabipedia

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


def fetch_last_game_from_maccabi_site() -> MaccabiGamesStats:
    from maccabistats import run_maccabitlv_site_source, load_from_maccabisite_source

    # Season 2020/21
    os.environ['START_SEASON_TO_CRAWL'] = '81'

    run_maccabitlv_site_source()
    games_from_maccabi_tlv_site = load_from_maccabisite_source()
    return MaccabiGamesStats([games_from_maccabi_tlv_site[-1]])


if __name__ == '__main__':
    logging.info('Fetching last game from maccabi tlv site')
    last_games = fetch_last_game_from_maccabi_site()

    logging.info('Upload last game to MaccabiPedia')
    upload_games_to_maccabipedia(last_games)
    logging.info('Uploaded last game to MaccabiPedia')
