from dateutil.parser import parse as datetime_parser

import logging

logger = logging.getLogger(__name__)

_games_dates_to_change = [("2017-01-10", "2017-01-11"),  # Against Hapoel Raanana
                          ("2009-05-22", "2009-05-23"),  # Against Maccabi PT
                          ]


def __fix_games_date(maccabi_games_stats):
    for game_dates in _games_dates_to_change:
        matching_games = maccabi_games_stats.played_at(game_dates[0])
        if not matching_games:
            logger.warning(f"Cant find game's original date so it may be changed: {game_dates[0]} (should be {game_dates[1]}), Skipping this game.")
            continue
        elif len(matching_games) != 1:
            logger.warning(f"Found ({len(matching_games)}) games from this date: {game_dates[0]} (should be {game_dates[1]}), Skipping this game.")
            continue

        game_to_be_changed = matching_games[0]
        game_to_be_changed.date = datetime_parser(game_dates[1])
        logger.info(f"Changed game date from {game_dates[0]} -> {game_dates[1]}.")


def fix_specific_games(maccabi_games_stats):
    """
    Fix the specific errors for table source.
    :type maccabi_games_stats: maccabistats.stats.maccabi_games_stats.MaccabiGamesStats
    :return: maccabi games stats (fixed)
    """

    __fix_games_date(maccabi_games_stats)
    return maccabi_games_stats
