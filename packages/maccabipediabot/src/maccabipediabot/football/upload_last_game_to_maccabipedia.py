import logging

from maccabistats import load_from_maccabisite_source

# We need to log before we run any of our code
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)

from maccabipediabot.football.gamesbot import upload_games_to_maccabipedia


def loading_last_game_from_maccabi_site():
    games_from_maccabi_tlv_site = load_from_maccabisite_source()
    logging.info(
        f'Loaded games from maccabi tlv site: {games_from_maccabi_tlv_site.first_game_date} to {games_from_maccabi_tlv_site.last_game_date}')
    return games_from_maccabi_tlv_site.create_maccabi_games_stats_with_filtered_games(
        [games_from_maccabi_tlv_site.games[-1]], 'Last game'
    )


if __name__ == '__main__':
    logging.info('Loading last game from maccabi tlv site')
    last_games = loading_last_game_from_maccabi_site()

    logging.info('Upload last game to MaccabiPedia')
    upload_games_to_maccabipedia(last_games)
    logging.info('Uploaded last game to MaccabiPedia')
