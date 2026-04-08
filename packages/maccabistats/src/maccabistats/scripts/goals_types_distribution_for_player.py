from maccabistats import load_from_maccabipedia_source
from maccabistats.models.player_game_events import GoalGameEvent
from collections import Counter
import logging

# Allow to log when running with __name__ == "__main__"
logger = logging.getLogger("maccabistats")


def show_goals_types_distribution_for_player(player_name):
    """
    Calculate the goals type distribution for the given player name.
    For example, a player may score 10 goals:
        * 4 of them by head
        * 4 of them are unknown type (regular or unclassified)
        * 2 of them by free-kick

    Calculation is done only for league games (can be changed within the code).

    :type player_name: basestring
    """
    logger.info(f"Calculating goals types distribution for player: {player_name}")

    maccabipedia_games = load_from_maccabipedia_source()
    player_league_games = maccabipedia_games.get_games_by_played_player_name(player_name).league_games

    player_goals = []
    for game in player_league_games.games:
        player_in_game = [player for player in game.maccabi_team.players if player.name == player_name]
        if len(player_in_game) > 1:
            raise RuntimeError(f"Found duplicate player names for '{player_name}', in this game: {game}")

        player = player_in_game[0]
        player_goals.extend([event for event in player.events if isinstance(event, GoalGameEvent)])

    player_goals_types = Counter(e.goal_type for e in player_goals)
    logger.info(f"Goals types distribution for {player_name} is:")

    for goal_type in player_goals_types.items():
        logger.info(f"{goal_type}, {goal_type[1]/len(player_goals):.2}%")


if __name__ == "__main__":
    show_goals_types_distribution_for_player("אלי דריקס")
