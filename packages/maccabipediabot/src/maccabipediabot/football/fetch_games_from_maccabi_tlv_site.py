import logging
import os

from maccabistats import run_maccabitlv_site_source
from maccabistats.config import MaccabiStatsConfigSingleton

from maccabipediabot.common.logging_setup import setup_logging
setup_logging(level=logging.DEBUG)


def fetch_games_from_maccabi_tlv_site() -> None:
    # Season 2024/25
    os.environ['START_SEASON_TO_CRAWL'] = '85'
    logging.info(f"Fetching maccabi tlv site games with start season: {os.environ['START_SEASON_TO_CRAWL']}")

    MaccabiStatsConfigSingleton.maccabi_site.use_multiprocess_crawling = False
    logging.info(
        f"Changed use multi process to be: {MaccabiStatsConfigSingleton.maccabi_site.use_multiprocess_crawling}")
    run_maccabitlv_site_source()


if __name__ == '__main__':
    logging.info('Fetching last season games from maccabi tlv site')
    fetch_games_from_maccabi_tlv_site()
    logging.info('Fetched last season games from maccabi tlv site!')
