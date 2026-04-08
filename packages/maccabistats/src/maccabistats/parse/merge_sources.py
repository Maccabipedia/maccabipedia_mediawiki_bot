import logging

logger = logging.getLogger(__name__)

"""
Merge all the sources to one maccabi games stats object, atm table source contains no events and we threat those games as verified content.
"""


def merge_maccabitlv_and_table(maccabitlv_site_source, table_source):
    """
    Merge All the sources to one maccabi games stats,
    For each maccabitlv-site game find the matching table game and merge.
    Ignoring (adding but nor merging) maccabi-tlv site games without matching table game.

    :param maccabitlv_site_source: the maccabi games stats object from maccabitlv site source.
    :type maccabitlv_site_source: maccabistats.stats.maccabi_games_stats.MaccabiGamesStats
    :type table_source: maccabistats.stats.maccabi_games_stats.MaccabiGamesStats
    :param table_source: the maccabi games stats object from table source.
    :rtype: maccabistats.stats.maccabi_games_stats.MaccabiGamesStats
    """

    logger.info("Merging maccabitlv site and table sources")

    # Table source supporting only league games.
    maccabitlv_site_league_games = maccabitlv_site_source.league_games

    # We dont need to merge non-league games
    merged_games = [game for game in maccabitlv_site_source if game not in maccabitlv_site_league_games]

    for maccabitlv_site_game in maccabitlv_site_league_games:
        matching_games = table_source.played_at(maccabitlv_site_game.date)

        if len(matching_games) != 1:
            logger.warning("Could not decide which game to take from this date: {date}, Found {num} games, adding them anyway"
                           .format(date=maccabitlv_site_game.date, num=len(matching_games)))

            # Atm, Add those games (1 or more).
            if len(matching_games) > 0:
                merged_games.extend(matching_games)
            else:
                merged_games.append(maccabitlv_site_game)
            continue

        merged_games.append(__merge_two_games(matching_games[0], maccabitlv_site_game))  # Takes only the first game on this date.

    return merged_games


def __merge_two_games(table_game, maccabitlv_site_game):
    """
    Merging two matching games (by playing date).
    :param maccabitlv_site_game: Game parsed from table source.
    :type maccabitlv_site_game: maccabistats.models.game_data.GameData
    :param table_game: Game parsed from maccabitlv site.
    :type table_game: maccabistats.models.game_data.GameData
    :rtype: maccabistats.models.game_data.GameData
    """

    logger.info(f"Merging games at date :{table_game.date}")
    __override_general_game_details_from_table(maccabitlv_site_game, table_game)

    # TODO - this might be in another function

    # Check whether there is home-away mismatch:
    if table_game.away_team.name == maccabitlv_site_game.home_team.name and table_game.home_team.name == maccabitlv_site_game.away_team.name:
        logger.info(f"Found home-away mismatch - switching positions,"
                    f" new home team: {maccabitlv_site_game.away_team.name}, new away team: {maccabitlv_site_game.home_team.name}")
        maccabitlv_site_game.home_team, maccabitlv_site_game.away_team = maccabitlv_site_game.away_team, maccabitlv_site_game.home_team

    if table_game.away_team.score != maccabitlv_site_game.away_team.score:
        logger.info(f"Found diff - away team score: {table_game.away_team.score}(table) - {maccabitlv_site_game.away_team.score}(maccabitlv site)")
        maccabitlv_site_game.away_team.score = table_game.away_team.score

    if table_game.home_team.score != maccabitlv_site_game.home_team.score:
        logger.info(f"Found diff - home team score: {table_game.home_team.score}(table) - {maccabitlv_site_game.home_team.score}(maccabitlv site)")
        maccabitlv_site_game.home_team.score = table_game.home_team.score

    return maccabitlv_site_game


def __override_general_game_details_from_table(maccabitlv_site_game, table_game):
    """
    Take the table general game data and sets it at maccabitlv site game.
    :param maccabitlv_site_game: Game parsed from table source.
    :type maccabitlv_site_game: maccabistats.models.game_data.GameData
    :param table_game: Game parsed from maccabitlv site.
    :type table_game: maccabistats.models.game_data.GameData
    """

    if table_game.referee != maccabitlv_site_game.referee:
        logger.info(f"Found diff - referee: {table_game.referee}(table) - {maccabitlv_site_game.referee}(maccabitlv site)")
        maccabitlv_site_game.referee = table_game.referee

    if table_game.stadium != maccabitlv_site_game.stadium:
        logger.info(f"Found diff - stadium: {table_game.stadium}(table) - {maccabitlv_site_game.stadium}(maccabitlv site)")
        maccabitlv_site_game.stadium = table_game.stadium

    if table_game.fixture != maccabitlv_site_game.fixture:
        logger.info(f"Found dif - fixture: {table_game.fixture}(table) - {maccabitlv_site_game.fixture}(maccabitlv site)")
        maccabitlv_site_game.fixture = table_game.fixture
