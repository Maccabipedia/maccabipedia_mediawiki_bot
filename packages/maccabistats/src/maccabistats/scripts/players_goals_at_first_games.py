import logging
import pprint

from maccabistats import load_from_maccabipedia_source
from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

FIRST_GAMES_COUNT = 5
GOALS_TO_SHOW_FROM = 4

if __name__ == '__main__':
    maccabi_games = load_from_maccabipedia_source().league_games

    players_games = maccabi_games.played_games_by_player_name()

    players_to_show = []

    for player, games in players_games.items():
        first_games = MaccabiGamesStats(games[:FIRST_GAMES_COUNT])
        player_goals = [goals for name, goals in first_games.players.best_scorers if name == player] or [0]
        player_goals = player_goals[0]
        if player_goals >= GOALS_TO_SHOW_FROM:
            players_to_show.append((player, player_goals, first_games[0].date))

    logging.info(pprint.pformat(
        sorted(players_to_show, key=lambda i: i[1], reverse=True)))
