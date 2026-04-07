import pprint

from maccabistats import load_from_maccabipedia_source

if __name__ == '__main__':
    maccabi_games = load_from_maccabipedia_source().official_games

    youngest_players = maccabi_games.players_special_games.youngest_players_by_first_time_to_be_captain()

    games_until_captain = {}

    for player in youngest_players:
        player_games = maccabi_games.get_games_by_played_player_name(player.player_name)
        game_index = player_games.games.index(player.first_game)
        games_until_captain[player.player_name] = game_index

    print(pprint.pformat(sorted(youngest_players, key=lambda i: i.time_in_days)))
    print(pprint.pformat(sorted(games_until_captain.items(), key=lambda i: i[1])))
