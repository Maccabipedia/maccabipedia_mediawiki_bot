import logging
import os

from maccabistats import run_maccabitlv_site_source

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)


def fetch_games_from_maccabi_tlv_site() -> None:
    # Season 2020/21
    os.environ['START_SEASON_TO_CRAWL'] = '81'

    run_maccabitlv_site_source()


if __name__ == '__main__':
    logging.info('Fetching last season games from maccabi tlv site')
    fetch_games_from_maccabi_tlv_site()
    logging.info('Fetched last season games from maccabi tlv site!')
