from maccabistats import load_from_maccabipedia_source
from datetime import timedelta

import logging

# Allow to log when running with __name__ == "__main__"
logger = logging.getLogger("maccabistats")


def last_minutes_win(maccabi_game):
    """
    We count only game that maccabi won "on the bazer", means the score dif between maccabi to the opponent team is 1.
    Moreover, this goal (maccabi winning goal) has to be scored at minute 90+

    :type maccabi_game: maccabistats.models.game_data.GameData
    :rtype: bool
    """

    if maccabi_game.maccabi_score_diff != 1:
        return False

    last_goal = maccabi_game.goals()[-1]

    last_goal_time = last_goal['time_occur']
    min_90_as_str = str(timedelta(minutes=90))

    if min_90_as_str > last_goal_time:
        return False

    # Make sure we dont count situation of 2-0 to maccabi and the opponent scored.
    # Moreover, dont count own goals
    if last_goal['team'] != "מכבי תל אביב":
        return False

    return True


def show_on_buzzer_wins_games():
    """
    Show the games maccabi won "on-buzzer":
     * A game that finished with 1 goal diff to maccabi
     * The last goal was maccabi one (its was a tie before)
     * The last goal scored at minute 90+ (at the second half)
     * Today we ignore own goals
    """
    maccabipedia_league_games = load_from_maccabipedia_source().league_games
    last_minutes_wins = []

    for game in maccabipedia_league_games:
        if last_minutes_win(game):
            logger.info(f"An on buzzer win: {game.date.date()}, {game.not_maccabi_team.name}")
            last_minutes_wins.append(game)

    logger.info(f"\ntotal last minutes wins: {len(last_minutes_wins)}")


if __name__ == "__main__":
    show_on_buzzer_wins_games()
