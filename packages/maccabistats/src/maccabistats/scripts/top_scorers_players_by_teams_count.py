from maccabistats import load_from_maccabipedia_source
from collections import defaultdict, Counter

import logging

# Allow to log when running with __name__ == "__main__"
logger = logging.getLogger("maccabistats")


def show_players_who_are_top_scorers_by_the_amount_of_teams_they_are_top_scorers_against():
    """
    Calculate the players who are the top scorer against each team,
    For each player count the number of teams he is the top scorer against and show those top players (by the amount of teams desc).
    """
    logger.info("Starting to calculate the top players with most of teams he is best scorer against (just for league games)")

    maccabipedia_league_games = load_from_maccabipedia_source().league_games
    opponents = maccabipedia_league_games.available_opponents

    best_players = defaultdict(list)
    for team in opponents:
        top_scorers_against_team = maccabipedia_league_games.get_games_against_team(team).players.best_scorers
        if top_scorers_against_team:
            player_name, scored = top_scorers_against_team[0]
            best_players[player_name].append((team, scored))

    players_with_most_teams = Counter({name: len(teams) for name, teams in best_players.items()})
    logger.info("Top players:")

    for player_name, teams_count_he_best_scorer_against in players_with_most_teams.most_common():
        logger.info(f"{player_name} <--> {teams_count_he_best_scorer_against} קבוצות")


if __name__ == "__main__":
    show_players_who_are_top_scorers_by_the_amount_of_teams_they_are_top_scorers_against()
