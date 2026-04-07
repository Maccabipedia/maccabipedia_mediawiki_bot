import logging

from maccabistats import load_from_maccabipedia_source

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

_logger = logging.getLogger(__name__)

WITH_OPPONENT_PLAYERS = True

# Most players that used to be captains, from maccabi and opponent
if __name__ == '__main__':
    maccabi_games = load_from_maccabipedia_source().official_games

    captains = {player[0] for player in maccabi_games.players.most_captains}

    for game in maccabi_games:
        played_players = set(game.maccabi_team.played_players_with_amount.keys())
        opponent_players = set()

        if WITH_OPPONENT_PLAYERS:
            opponent_players.update(game.not_maccabi_team.played_players_with_amount.keys())

        maccabi_captains_players = captains.intersection(played_players)
        opponent_captains_players = captains.intersection(opponent_players)

        if len(opponent_captains_players) > 2:
            _logger.info(f'Opponent captains! {opponent_captains_players}, game: {game}')

        if len(maccabi_captains_players) + len(opponent_captains_players) > 10:
            _logger.info(f'{len(maccabi_captains_players)} captains, game: {game}\n'
                         f'captains: {maccabi_captains_players}')
