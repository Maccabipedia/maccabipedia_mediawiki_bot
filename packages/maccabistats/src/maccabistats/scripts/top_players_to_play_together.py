import logging
import pprint
from collections import Counter
from itertools import combinations

from maccabistats import load_from_maccabipedia_source

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)

_logger = logging.getLogger(__name__)

AMOUNT_OF_PLAYERS_TO_PLAY_TOGETHER = 2  # Default is 2 - couple
TOP_SET_OF_PLAYERS_TO_SHOW = 25

# Find the couple/set of players that played the most games together
if __name__ == '__main__':
    maccabi_games = load_from_maccabipedia_source().official_games

    played_couples = Counter()

    for game in maccabi_games:
        _logger.info(f'Handle game date: {game.date}')

        current_game_played_players = list(game.maccabi_team.played_players_with_amount.keys())
        # We need to sort in order to have the same couple names
        current_game_played_players.sort()

        for couple in combinations(current_game_played_players, AMOUNT_OF_PLAYERS_TO_PLAY_TOGETHER):
            played_couples[couple] += 1

    _logger.info(pprint.pformat(played_couples.most_common(TOP_SET_OF_PLAYERS_TO_SHOW)))
