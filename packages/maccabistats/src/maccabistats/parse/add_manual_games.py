from maccabistats.models.game_data import GameData
from maccabistats.models.team_in_game import TeamInGame
from maccabistats.models.player_in_game import PlayerInGame, GameEvent, GameEventTypes
from maccabistats.models.player_game_events import GoalTypes, GameEventTypes, GoalGameEvent

from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def add_manual_games(games):
    """ Here we will add all the games we've collected manually """

    logger.info("Adding manual games")
    __add_against_boca(games)


def __get_player_from_list(player_name, players):
    return list(filter(lambda p: p.name == player_name, players))[0]


def __add_against_boca(maccabi_games):
    against_boca = maccabi_games.played_at("2006-05-18")

    if against_boca:
        # Games exists, return
        return

    maccabi_lineup_players = ['לירן שטראובר', 'אבי יחיאל', "אלוין בג'ירי", 'כריסטיאן גונסאלס', 'אורי שטרית', 'שרן ייני', "ליאור ג'אן",
                              "ג'ובאני רוסו", 'לירן כהן', 'אופיר חיים', 'גיורגי דמיטרדזה']
    boca_lineup_players = ['פאבלו מיליורה', 'חוסה קאלבו', 'יונתן מאידנה', 'מורל רודריגס', 'ברוני אוריברי', 'מתיאס דונט', 'אבר בנגה', 'ניקולאס ברטולו',
                           "גיז'רמו מרינו", 'מרטין פאלרמו', "גיז'רמו בארוס סקלוטו"]

    # Maccabi team
    # Lineup
    maccabi_players = [PlayerInGame(name=player_name, number=None, game_events=[GameEvent(GameEventTypes.LINE_UP, timedelta(minutes=0))]) for
                       player_name in maccabi_lineup_players]

    # Subs
    maccabi_players.append(
        PlayerInGame(name="ז'וזה דוארטה", number=None, game_events=[GameEvent(GameEventTypes.SUBSTITUTION_IN, timedelta(minutes=41))]))
    __get_player_from_list("אופיר חיים", maccabi_players).add_event(GameEvent(GameEventTypes.SUBSTITUTION_OUT, timedelta(minutes=41)))

    maccabi_players.append(PlayerInGame(name="אסף מנדס", number=None, game_events=[GameEvent(GameEventTypes.SUBSTITUTION_IN, timedelta(minutes=69))]))
    __get_player_from_list("לירן שטראובר", maccabi_players).add_event(GameEvent(GameEventTypes.SUBSTITUTION_OUT, timedelta(minutes=69)))

    maccabi_players.append(
        PlayerInGame(name="אליאור ועקנין", number=None, game_events=[GameEvent(GameEventTypes.SUBSTITUTION_IN, timedelta(minutes=74))]))
    __get_player_from_list("גיורגי דמיטרדזה", maccabi_players).add_event(GameEvent(GameEventTypes.SUBSTITUTION_OUT, timedelta(minutes=74)))

    maccabi_players.append(
        PlayerInGame(name="הנרי מאקינווה", number=None, game_events=[GameEvent(GameEventTypes.SUBSTITUTION_IN, timedelta(minutes=79))]))
    __get_player_from_list("ג'ובאני רוסו", maccabi_players).add_event(GameEvent(GameEventTypes.SUBSTITUTION_OUT, timedelta(minutes=79)))

    # Boca team
    # Lineup
    boca_players = [PlayerInGame(name=player_name, number=None, game_events=[GameEvent(GameEventTypes.LINE_UP, timedelta(minutes=0))]) for
                    player_name in boca_lineup_players]

    # Subs
    boca_players.append(
        PlayerInGame(name="אמיליאנו סרדה", number=None, game_events=[GameEvent(GameEventTypes.SUBSTITUTION_IN, timedelta(minutes=46))]))
    __get_player_from_list("חוסה קאלבו", boca_players).add_event(GameEvent(GameEventTypes.SUBSTITUTION_OUT, timedelta(minutes=46)))

    boca_players.append(
        PlayerInGame(name="ויקטור אורמסבל", number=None, game_events=[GameEvent(GameEventTypes.SUBSTITUTION_IN, timedelta(minutes=65))]))
    __get_player_from_list("ניקולאס ברטולו", boca_players).add_event(GameEvent(GameEventTypes.SUBSTITUTION_OUT, timedelta(minutes=65)))

    boca_players.append(
        PlayerInGame(name="פאולו מאוצ'ה", number=None, game_events=[GameEvent(GameEventTypes.SUBSTITUTION_IN, timedelta(minutes=89))]))
    __get_player_from_list("גיז'רמו בארוס סקלוטו", boca_players).add_event(GameEvent(GameEventTypes.SUBSTITUTION_OUT, timedelta(minutes=89)))

    boca_players.append(
        PlayerInGame(name="חואן פישר", number=None, game_events=[GameEvent(GameEventTypes.SUBSTITUTION_IN, timedelta(minutes=90))]))
    __get_player_from_list("מרטין פאלרמו", boca_players).add_event(GameEvent(GameEventTypes.SUBSTITUTION_OUT, timedelta(minutes=90)))

    __get_player_from_list("מרטין פאלרמו", boca_players).add_event(GoalGameEvent(timedelta(minutes=76), GoalTypes.PENALTY))

    maccabi_team = TeamInGame(name="מכבי תל אביב", coach="טון קאנן", score=0, players=maccabi_players)
    boca_team = TeamInGame(name="בוקה ג'וניורס", coach="", score=1, players=boca_players)

    maccabi_against_boca = GameData(competition="ידידות", fixture="", date_as_hebrew_string="", stadium="בלומפילד", crowd="", referee="",
                                    home_team=maccabi_team, away_team=boca_team, season_string="2005/06", half_parsed_events=[],
                                    date=datetime(2006, 5, 18))

    logger.info("Adding maccabi against boca - 2006-05-18")
    maccabi_games.games.append(maccabi_against_boca)
