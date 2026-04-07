from maccabistats import load_from_maccabipedia_source

import logging

# Allow to log when running with __name__ == "__main__"
logger = logging.getLogger("maccabistats")


def show_players_with_atleast_goals_and_assists_in_this_season(maccabi_season, atleast_goals_and_assist=10, maximum_players_to_show=3):
    """
    Show the players in this season that have atleast: "atleast_goals_and_assist" goals and "atleast_goals_and_assist" assists.
    This function (and file) is built to show the players that done a "double-double" (atleast 10 goals and 10 assists in a season),
    but may be show other statistics as well.

    :type atleast_goals_and_assist: int
    :type maccabi_season: maccabistats.stats.maccabi_games_stats.MaccabiGamesStats
    """

    scorers = dict(maccabi_season.players.best_scorers[:10])
    assisters = dict(maccabi_season.players.best_assisters[:10])

    players_top_scorers_and_assisters = scorers.keys() & assisters.keys()
    players_with_minimum_between_scorers_and_assisters = dict()
    for player_name in players_top_scorers_and_assisters:
        players_with_minimum_between_scorers_and_assisters[player_name] = min(scorers[player_name], assisters[player_name])

    maybe_top_players = sorted(players_with_minimum_between_scorers_and_assisters.items(), key=lambda item: item[1], reverse=True)[
                        :maximum_players_to_show]
    top_players_names = [player_info[0] for player_info in maybe_top_players if player_info[1] >= atleast_goals_and_assist]

    if not top_players_names:
        return

    logger.info(f"\nTop players for season: {maccabi_season.games[0].season}:")
    for top_player_name in top_players_names:
        logger.info(f"Player {top_player_name } score: {scorers[top_player_name ]}, assist: {assisters[top_player_name ]}")


def show_players_that_done_a_double_double():
    """
    Show players that done a "double-double" (atleast 10 goals and assist in a season),
    Check every season from the last one to the first one.
    """

    maccabipedia_seasons = load_from_maccabipedia_source().league_games.seasons.get_seasons_stats()

    for season_index in reversed(range(len(maccabipedia_seasons))):
        show_players_with_atleast_goals_and_assists_in_this_season(maccabipedia_seasons[season_index], atleast_goals_and_assist=10)


if __name__ == "__main__":
    show_players_that_done_a_double_double()
