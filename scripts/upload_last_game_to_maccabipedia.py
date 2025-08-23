import logging

from maccabistats import load_from_maccabisite_source

# We need to log before we run any of our code
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)

from gamesbot import upload_games_to_maccabipedia
from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats


def loading_last_game_from_maccabi_site() -> MaccabiGamesStats:
    games_from_maccabi_tlv_site = load_from_maccabisite_source()
    logging.info(
        f'Loaded games from maccabi tlv site: {games_from_maccabi_tlv_site.first_game_date} to {games_from_maccabi_tlv_site.last_game_date}')
    return MaccabiGamesStats([games_from_maccabi_tlv_site[-1]])


if __name__ == '__main__':
    logging.info('Loading last game from maccabi tlv site')
    last_games = loading_last_game_from_maccabi_site()

    logging.info('Upload last game to MaccabiPedia')
    upload_games_to_maccabipedia(last_games)
    logging.info('Uploaded last game to MaccabiPedia')
