from maccabistats.models.player_game_events import GoalTypes, GameEvent, GameEventTypes, GoalGameEvent
from datetime import timedelta, datetime
from dateutil.parser import parse as datetime_parser

import logging

logger = logging.getLogger(__name__)

_games_dates_to_change = [("2012-03-23", "2012-03-24"),  # Against Hapoel Tel aviv
                          ("2012-01-31", "2012-01-30"),  # Against Kiryat Shmona
                          ("2011-02-17", "2011-02-19"),  # Against Hapoel PT
                          ("2005-10-12", "2005-12-11"),  # Against Hapoel TA
                          ("2004-07-03", "2004-03-07"),  # Against Hapoel BS
                          ("2002-05-01", "2002-01-05"),  # Against Hapoel BS
                          ("2002-04-07", "2002-04-06"),  # Against Maccabi Kiryat Gat
                          ("2002-01-04", "2002-04-01"),  # Against Hapoel TA
                          ("2001-10-11", "2001-11-10"),  # Against Hapoel TA
                          ("2001-11-04", "2001-11-05"),  # Against Beitar
                          ("2001-05-06", "2001-05-05"),  # Against Beitar
                          ("2001-03-02", "2001-02-03"),  # Against Maccabi Haifa
                          ("2000-09-15", "2000-09-16"),  # Against Tzafririm Holon
                          ("2000-06-11", "2000-11-06"),  # Against Hapoel TA
                          ("2005-04-18", "2005-04-17"),  # Against Maccabi Haifa
                          ("1998-09-19", "1998-09-26"),  # Against Maccabi Haifa
                          ("1997-11-02", "1997-11-01"),  # Against Hapoel TA
                          ("1997-10-26", "1997-10-25"),  # Against Maccabi Herzliya
                          ("1997-09-08", "1997-08-09"),  # Against Beitar
                          ("1996-09-06", "1996-09-07"),  # Against Hapoel BS
                          ("1995-04-28", "1995-04-29"),  # Against Hapoel Beit Shean
                          ("1994-12-25", "1994-12-24"),  # Against Beitar TA
                          ("1992-01-06", "1992-01-07"),  # Against Beitar TA
                          ("1991-06-08", "1991-06-07"),  # Against Maccabi Netanya
                          ("1991-05-25", "1991-05-24"),  # Against Beitar TA
                          ("1990-11-10", "1990-11-09"),  # Against Zafririm
                          ("1988-09-17", "1988-09-16"),  # Against Beitar TA
                          ("1987-12-26", "1987-12-25"),  # Against Hapoel Lod
                          ("1986-09-20", "1986-09-19"),  # Against Hapoel Lod
                          ("1983-05-01", "1983-04-30"),  # Against Hapoel Ramat-Gan
                          ("1981-04-19", "1981-04-18"),  # Against Hapoel TA
                          ("1980-05-02", "1980-05-03"),  # Against Hapoel Yahud
                          ("1977-04-03", "1977-04-02"),  # Against Maccabi Netanya
                          ("1973-04-08", "1973-04-07"),  # Against Hapoel Marmorek
                          ("1973-01-21", "1973-01-27"),  # Against Maccabi PT
                          ("1971-05-30", "1971-05-29"),  # Against Hapoel PT
                          ("1968-06-02", "1968-06-01"),  # Against Hapoel Jerusalem
                          ("1966-12-30", "1966-12-31"),  # Against Hacoh Ramt-Gan
                          ("1965-10-16", "1965-10-15"),  # Against Bnei Yehuda
                          ("1965-06-06", "1965-06-05"),  # Against Hacoh Ramt-Gan
                          ("1956-04-15", "1956-04-14"),  # Against Maccabi Netanya
                          ]

_wrong_games_to_remove = [datetime_parser(game_date) for game_date in
                          ["1972-01-22",  # Against Bnei Yehuda
                           ]]


def __remove_games(maccabi_games_stats):
    before_len = len(maccabi_games_stats.games)
    maccabi_games_stats.games = [game for game in maccabi_games_stats.games if game.date not in _wrong_games_to_remove]

    if before_len != len(maccabi_games_stats.games):
        logger.info(f"Removed {before_len - len(maccabi_games_stats.games)} games)")


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


def __fix_basel_three_three(games):
    against_basel_tie_three = games.played_at("2013-08-06")
    against_basel_tie_three = against_basel_tie_three[0]
    if against_basel_tie_three.not_maccabi_team.scored_players[0].events[2].goal_type is not GoalTypes.OWN_GOAL:
        against_basel_tie_three.not_maccabi_team.scored_players[0].events[2].goal_type = GoalTypes.OWN_GOAL
        logger.info("Fixed פביאן שאר goal to be own goal at min 34.")


def __fix_haifa_three_one(games):
    against_haifa_three_one_win = games.played_at("2014-10-20")
    against_haifa_three_one_win = against_haifa_three_one_win[0]
    if against_haifa_three_one_win.not_maccabi_team.scored_players[0].events[1].goal_type is not GoalTypes.OWN_GOAL:
        against_haifa_three_one_win.not_maccabi_team.scored_players[0].events[1].goal_type = GoalTypes.OWN_GOAL
        logger.info("Fixed טאלב טאווטחה goal to be own goal at min 52.")


def __fix_hibernians_five_one(games):
    against_hibernians_five_one_win = games.played_at("2015-07-21")
    against_hibernians_five_one_win = against_hibernians_five_one_win[0]
    if against_hibernians_five_one_win.not_maccabi_team.scored_players[1].events[1].goal_type is not GoalTypes.OWN_GOAL:
        against_hibernians_five_one_win.not_maccabi_team.scored_players[1].events[1].goal_type = GoalTypes.OWN_GOAL
        logger.info("Fixed ג'ורג' פריירה goal to be own goal at min 52.")


def __fix_akko_two_zero(games):
    against_akko_two_zero_win = games.played_at("2012-10-20")
    against_akko_two_zero_win = against_akko_two_zero_win[0]
    if against_akko_two_zero_win.not_maccabi_team.scored_players[0].events[1].goal_type is not GoalTypes.OWN_GOAL:
        against_akko_two_zero_win.not_maccabi_team.scored_players[0].events[1].goal_type = GoalTypes.OWN_GOAL
        logger.info("Fixed אימורו לוקמן goal to be own goal at min 52.")


def __fix_beitar_three_two(games):
    against_beitar_three_two_win = games.played_at("2003-05-17")
    against_beitar_three_two_win = against_beitar_three_two_win[0]
    david = [p for p in against_beitar_three_two_win.not_maccabi_team.players if p.name == "דוד אמסלם"][0]
    if not david.scored:
        goal = GameEvent(GameEventTypes.GOAL_SCORE, timedelta(minutes=33))
        david.add_event(goal)
        logger.info("Fixed דוד אמסלם goal - probably does not exists after crawling maccabi-tlv site( appear in events page but not in squads page.")

    if against_beitar_three_two_win._half_parsed_events:
        logger.info("Removing half parsed goals events from this game ({date}".format(date=against_beitar_three_two_win.date))
        against_beitar_three_two_win._half_parsed_events = list(
            filter(lambda event: event['event_type'] != GameEventTypes.GOAL_SCORE, against_beitar_three_two_win._half_parsed_events))


def __fix_kfar_saba_two_one(games):
    """ Because 1997-08-02 is mismatched with 1997-02-08 we need to identify them by more than date """

    logger.info("Changeing kfar-saba 1992-02-08 to 1997-08-02, just the game ended 2-1")
    against_kfar_saba_to_be_changed = [game for game in games.played_at("1997-02-08") if game.maccabi_team.score == 2]

    # IF someday it will be fixed
    if not against_kfar_saba_to_be_changed:
        return
    else:
        against_kfar_saba_to_be_changed[0].date = datetime_parser("1997-08-02")


def __fix_hapoel_haifa_four_two_date_99_00(games):
    # This game saved on maccabi-tlv site as against maccabi-haifa, that mistake, it should be against hapoel-haifa, round 18 for this season.
    # The original date is: 2000-01-03 (yy-mm-dd).
    against_hapoel_haifa = games.played_at("2000-03-01")
    if len(against_hapoel_haifa) > 1:
        logger.warning("Found more than one game that should be fixed at date : 2000-03-01, Taking the first.")

    if not against_hapoel_haifa:
        logger.info("Found no games at 2000-03-01, probably this game is fixed already")
        return

    against_hapoel_haifa = against_hapoel_haifa[0]
    against_hapoel_haifa.not_maccabi_team.name = "הפועל חיפה"
    against_hapoel_haifa.date = datetime(year=2000, month=1, day=3)
    logger.info("Changed the game at data: 2000-03-01 to be at date: 2000-01-03 and replaced the opponent name from הפועל חיפה to מכבי חיפה")


def __fix_kfar_saba_toto_games_at_2000_2001(games):
    """
    Should fix: against kfar saba at 2000-12-09 to be 2000-09-12, and update the result to 3-1 (to kfar saba).
    Update the second game to be 2-2, the goals are ok.
    """

    # First Game:
    logger.info("Changing game against kfar saba from 2000-12-09 to 2000-09-12, and changing the toto games results in 2000-01 against them.")
    kfar_saba_toto_games = games.get_games_by_competition("גביע הטוטו").get_games_against_team("הפועל כפר סבא")
    kfar_saba_wrong_date_and_score_game = kfar_saba_toto_games.played_at("2000-12-09")
    if kfar_saba_wrong_date_and_score_game:
        kfar_saba_wrong_date_and_score_game = kfar_saba_wrong_date_and_score_game[0]
        kfar_saba_wrong_date_and_score_game.date = datetime(year=2000, month=9, day=12)
        kfar_saba_wrong_date_and_score_game.not_maccabi_team.score = 3
        kfar_saba_wrong_date_and_score_game.maccabi_team.score = 1
    else:
        logger.info("Kfar saba game at 2000-12-09 already changed to be 2000-09-12, skipping fixing for this game")

    # Second game:
    wrong_score_game = kfar_saba_toto_games.played_at("2000-09-26")[0]
    wrong_score_game.not_maccabi_team.score = 2
    wrong_score_game.maccabi_team.score = 2


def __add_fixtures_numbers(games):
    pass


def __fix_half_parsed_goal_events(game):
    half_parsed_goals = [event for event in game._half_parsed_events if event['event_type'] == GameEventTypes.GOAL_SCORE]
    if not half_parsed_goals:
        return

    total_score = game.maccabi_team.score + game.not_maccabi_team.score
    total_goal_events = len(game.goals())

    if total_score != total_goal_events:
        logger.info("Found game (date-{date}) with "
                    "total score of: {total_score}, total goals events: {total_goal_events} and total half parsed goals: {total_half_parsed_goals}"
                    .format(date=game.date, total_score=total_score, total_goal_events=total_goal_events,
                            total_half_parsed_goals=len(half_parsed_goals)))
    else:
        logger.warning("Total score & total goals events are equals "
                       "but game (date-{date}) got {num} half parsed goals.".format(date=game.date, num=len(half_parsed_goals)))

    if total_goal_events + len(half_parsed_goals) <= total_score:
        logger.info("Half parsed goal events seems to missing goals, Adding them!")
        __add_half_parsed_goals_events_to_game(game, half_parsed_goals)
    else:
        logger.warning("Half parsed goals + total goals events does not equal to the total score, something wrong, do nothing.")


def __get_player_for_half_parsed_goals_events(game, goal_event):
    """
    Trying to search for exact name, after that for first\last name, after that splitting name by dot (if exist) and search for first\last name.
    """
    # Trying to find player with the exact name.
    name = goal_event['name']
    all_players = game.maccabi_team.players + game.not_maccabi_team.players
    players = [player for player in all_players if player.name == name]
    if players:
        return players[0]

    # Trying to find player with the same first\last name.
    logger.info("Cant find full player name, trying first\last name:{name}".format(name=name))
    players = [player for player in all_players if name in player.name.split()]
    if players:
        return players[0]

    # Trying dot pattern, like : א.זוהר which might be איציק זוהר
    logger.info("Cant find first\last player name, trying check for dot pattern name:{name}".format(name=name))
    if "." in name:
        first, last = [part.strip() for part in name.split(".")]
        players = [player for player in all_players if last in player.name.split()]
        # If we found two players with the same last name, try with the first name.
        if len(players) > 1:
            players = [player for player in players if player.name.startswith(first)]

        if players:
            return players[0]

    return None


def __add_half_parsed_goals_events_to_game(game, half_parsed_goals_events):
    event_to_delete_from_game_half_parsed_event = []

    for event in half_parsed_goals_events:
        if not event['name']:
            logger.warning("Found goal (game date - {date}) with empty player name, skipping".format(date=game.date))
            continue

        player_for_this_event = __get_player_for_half_parsed_goals_events(game, event)
        if player_for_this_event is None:
            logger.warning("Could not find any player that match somehow to this name:{name}, skipping this event".format(name=event['name']))
            continue

        logger.info("Add goal event: {event} to this player:{name} in this game date: {date}"
                    .format(event=event, name=player_for_this_event.name, date=game.date))

        goal_event = GoalGameEvent(event['time_occur'], event['goal_type'])
        player_for_this_event.add_event(goal_event)
        event_to_delete_from_game_half_parsed_event.append(event)

    if event_to_delete_from_game_half_parsed_event:
        logger.info("Removing half parsed goals events from this game")
        new_half_parsed_events = [not_added_half_parsed_event for not_added_half_parsed_event in half_parsed_goals_events if
                                  not_added_half_parsed_event not in event_to_delete_from_game_half_parsed_event]
        game._half_parsed_events = new_half_parsed_events


def fix_specific_games(games):
    # TODO separate to two diff function (or any another logic).

    # Fix goals:
    try:
        __fix_basel_three_three(games)
        __fix_haifa_three_one(games)
        __fix_hibernians_five_one(games)
        __fix_akko_two_zero(games)
        __fix_beitar_three_two(games)
        __fix_kfar_saba_two_one(games)
        __fix_kfar_saba_toto_games_at_2000_2001(games)

    except IndexError:
        logger.warning('Probably found no specific games to fix (it might cause because you run with MaccabiGamesStats without these games, Continue')

    # Fix dates & name:
    __fix_hapoel_haifa_four_two_date_99_00(games)

    # Fix just dates:
    __fix_games_date(games)

    # Games that seems to be wrong (and should be removed):
    __remove_games(games)

    # Add games fixtures
    # __add_fixtures_numbers(games)

    for game in games:
        # ATM, only the important events = goals.
        try:
            __fix_half_parsed_goal_events(game)
        except LookupError:
            logger.exception("Error while parsing goals half parsed events.")

    return games
