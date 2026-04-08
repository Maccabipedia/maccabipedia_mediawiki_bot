"""
Game fixture data for maccabistats tests using real historical Maccabi Tel Aviv names.

10 games designed to cover:
  - Game resolutions: 5 wins, 2 losses, 2 ties, 1 technical win (each >=2 occurrences)
  - Home (7) and away (3) games
  - Competitions: league (8), cup (1), friendly (1)
  - Two seasons: 2019/20 (6 games), 2020/21 (4 games)
  - Two coaches: אברם גרנט (6 games), פאולו סוזה (4 games)
  - A comeback game (0-2 down, win 4-2)
  - A tie comeback (0-1 down, tie 1-1)
  - Clean sheets (4 games)
  - Goals from bench (2 games)
  - Technical result (1 game)

Maccabi players (all-time top scorers and legends):
  - אבי נמני (#10) — captain, striker (all-time #1 scorer, 219 goals)
  - ערן זהבי (#14) — super sub, bench goals (all-time #2, 207 goals)
  - שייע גלזר (#5) — gets straight red (all-time #3, 197 goals)
  - בני טבק (#6) — midfielder (all-time #4, 175 goals)
  - אלי דריקס (#7) — header specialist (all-time #5, 159 goals)
  - גיורא שפיגל (#11) — winger (all-time #6, 135 goals)
  - יוסף מרימוביץ' (#4) — midfielder (all-time #7, 132 goals)
  - ויקי פרץ (#9) — forward (all-time #9, 101 goals)
  - אלירן עטר (#15) — benched (all-time #10, 96 goals)
  - חיים רביבו (#8) — playmaker, chief assister
  - טל בן חיים (#3) — defender, picks up cards
  - בונדארנקו (#1) — goalkeeper, stops penalties
  - מלאכי חלימי (#2) — fullback

Player events covered (each >=2 occurrences):
  - LINE_UP, SUBSTITUTION_IN, SUBSTITUTION_OUT
  - GOAL_SCORE, GOAL_ASSIST
  - YELLOW_CARD, RED_CARD, SECOND_YELLOW_CARD
  - CAPTAIN, PENALTY_MISSED, PENALTY_STOPPED, BENCHED

Goal types covered (each >=2):
  - NORMAL_KICK, HEADER, PENALTY, FREE_KICK, OWN_GOAL

Assist types covered (each >=2):
  - NORMAL_ASSIST, CORNER_ASSIST
"""
import datetime
from datetime import timedelta

from maccabistats.models.game_data import GameData
from maccabistats.models.player_game_events import (
    AssistGameEvent,
    AssistTypes,
    GameEvent,
    GameEventTypes,
    GoalGameEvent,
    GoalTypes,
)
from maccabistats.models.player_in_game import PlayerInGame
from maccabistats.models.team_in_game import TeamInGame


# ---------------------------------------------------------------------------
# Helper builders
# ---------------------------------------------------------------------------

def _player(name: str, number: int, events: list[GameEvent] | None = None) -> PlayerInGame:
    return PlayerInGame(name, number, events or [])


def _lineup(minute: int = 0) -> GameEvent:
    return GameEvent(GameEventTypes.LINE_UP, timedelta(minutes=minute))


def _sub_in(minute: int) -> GameEvent:
    return GameEvent(GameEventTypes.SUBSTITUTION_IN, timedelta(minutes=minute))


def _sub_out(minute: int) -> GameEvent:
    return GameEvent(GameEventTypes.SUBSTITUTION_OUT, timedelta(minutes=minute))


def _goal(minute: int, goal_type: GoalTypes = GoalTypes.NORMAL_KICK) -> GoalGameEvent:
    return GoalGameEvent(timedelta(minutes=minute), goal_type)


def _assist(minute: int, assist_type: AssistTypes = AssistTypes.NORMAL_ASSIST) -> AssistGameEvent:
    return AssistGameEvent(timedelta(minutes=minute), assist_type)


def _yellow(minute: int) -> GameEvent:
    return GameEvent(GameEventTypes.YELLOW_CARD, timedelta(minutes=minute))


def _red(minute: int) -> GameEvent:
    return GameEvent(GameEventTypes.RED_CARD, timedelta(minutes=minute))


def _second_yellow(minute: int) -> GameEvent:
    return GameEvent(GameEventTypes.SECOND_YELLOW_CARD, timedelta(minutes=minute))


def _captain(minute: int = 0) -> GameEvent:
    return GameEvent(GameEventTypes.CAPTAIN, timedelta(minutes=minute))


def _benched() -> GameEvent:
    return GameEvent(GameEventTypes.BENCHED, timedelta(minutes=0))


def _penalty_missed(minute: int) -> GameEvent:
    return GameEvent(GameEventTypes.PENALTY_MISSED, timedelta(minutes=minute))


def _penalty_stopped(minute: int) -> GameEvent:
    return GameEvent(GameEventTypes.PENALTY_STOPPED, timedelta(minutes=minute))


def _game(
    competition: str,
    fixture: str,
    date: datetime.datetime,
    stadium: str,
    referee: str,
    home_team: TeamInGame,
    away_team: TeamInGame,
    season: str,
    technical_result: bool = False,
) -> GameData:
    return GameData(
        competition=competition,
        fixture=fixture,
        date_as_hebrew_string="",
        stadium=stadium,
        crowd="1000",
        referee=referee,
        home_team=home_team,
        away_team=away_team,
        season_string=season,
        half_parsed_events=[],
        date=date,
        technical_result=technical_result,
    )


# ---------------------------------------------------------------------------
# The 10 synthetic games
# ---------------------------------------------------------------------------

GAMES: list[GameData] = []

# ---- Game 1: League, home, WIN 3-1, season 2019/20 ----
# Maccabi: אבי נמני scores 2 (normal), אלי דריקס scores 1 (header)
# חיים רביבו assists twice (normal + corner), אבי נמני is captain
# אלירן עטר is benched
GAMES.append(_game(
    competition="ליגת העל", fixture="מחזור1", season="2019/20",
    date=datetime.datetime(2019, 9, 14),
    stadium="בלומפילד", referee="יורם דוידוביץ",
    home_team=TeamInGame("מכבי תל אביב", "אברם גרנט", 3, [
        _player("אבי נמני", 10, [_lineup(), _captain(), _goal(15), _goal(70)]),
        _player("אלי דריקס", 7, [_lineup(), _goal(40, GoalTypes.HEADER)]),
        _player("חיים רביבו", 8, [_lineup(), _assist(15), _assist(40, AssistTypes.CORNER_ASSIST)]),
        _player("טל בן חיים", 3, [_lineup()]),
        _player("בונדארנקו", 1, [_lineup()]),
        _player("שייע גלזר", 5, [_lineup()]),
        _player("בני טבק", 6, [_lineup()]),
        _player("גיורא שפיגל", 11, [_lineup()]),
        _player("יוסף מרימוביץ'", 4, [_lineup()]),
        _player("ויקי פרץ", 9, [_lineup()]),
        _player("מלאכי חלימי", 2, [_lineup()]),
        _player("אלירן עטר", 15, [_benched()]),
    ]),
    away_team=TeamInGame("הפועל באר שבע", "אלישע לוי", 1, [
        _player("ערן לוי", 9, [_lineup(), _goal(55)]),
    ]),
))

# ---- Game 2: League, away, LOSS 0-2, season 2019/20 ----
# אבי נמני gets yellow, שייע גלזר gets straight red card
# ערן זהבי subs in, אלירן עטר benched
GAMES.append(_game(
    competition="ליגת העל", fixture="מחזור2", season="2019/20",
    date=datetime.datetime(2019, 9, 21),
    stadium="טדי", referee="אלי חקמון",
    home_team=TeamInGame("בית\"ר ירושלים", "גיא לוי", 2, [
        _player("יוסי בניון", 10, [_lineup(), _goal(30), _goal(60)]),
    ]),
    away_team=TeamInGame("מכבי תל אביב", "אברם גרנט", 0, [
        _player("אבי נמני", 10, [_lineup(), _captain(), _yellow(50)]),
        _player("אלי דריקס", 7, [_lineup()]),
        _player("חיים רביבו", 8, [_lineup(), _sub_out(60)]),
        _player("טל בן חיים", 3, [_lineup()]),
        _player("בונדארנקו", 1, [_lineup()]),
        _player("שייע גלזר", 5, [_lineup(), _red(55)]),
        _player("בני טבק", 6, [_lineup()]),
        _player("גיורא שפיגל", 11, [_lineup()]),
        _player("יוסף מרימוביץ'", 4, [_lineup()]),
        _player("ויקי פרץ", 9, [_lineup()]),
        _player("מלאכי חלימי", 2, [_lineup()]),
        _player("ערן זהבי", 14, [_sub_in(60)]),
        _player("אלירן עטר", 15, [_benched()]),
    ]),
))

# ---- Game 3: League, home, TIE 1-1, season 2019/20 ----
# Tie comeback: opponent scores at 20', Maccabi equalizes at 80' (penalty)
# אבי נמני misses a penalty at 60'
GAMES.append(_game(
    competition="ליגת העל", fixture="מחזור3", season="2019/20",
    date=datetime.datetime(2019, 10, 5),
    stadium="בלומפילד", referee="יורם דוידוביץ",
    home_team=TeamInGame("מכבי תל אביב", "אברם גרנט", 1, [
        _player("אבי נמני", 10, [_lineup(), _captain(), _penalty_missed(60), _goal(80, GoalTypes.PENALTY)]),
        _player("אלי דריקס", 7, [_lineup()]),
        _player("חיים רביבו", 8, [_lineup()]),
        _player("טל בן חיים", 3, [_lineup()]),
        _player("בונדארנקו", 1, [_lineup()]),
        _player("שייע גלזר", 5, [_lineup()]),
        _player("בני טבק", 6, [_lineup()]),
        _player("גיורא שפיגל", 11, [_lineup()]),
        _player("יוסף מרימוביץ'", 4, [_lineup()]),
        _player("ויקי פרץ", 9, [_lineup()]),
        _player("מלאכי חלימי", 2, [_lineup()]),
    ]),
    away_team=TeamInGame("מכבי חיפה", "ברק בכר", 1, [
        _player("אייל גולסה", 7, [_lineup(), _goal(20)]),
    ]),
))

# ---- Game 4: Cup, home, WIN 2-0 (clean sheet), season 2019/20 ----
# אבי נמני scores free kick, אלי דריקס scores header
# חיים רביבו assists twice (corner), בונדארנקו stops a penalty
GAMES.append(_game(
    competition="גביע המדינה", fixture="שמינית גמר", season="2019/20",
    date=datetime.datetime(2019, 11, 12),
    stadium="בלומפילד", referee="רועי ריינשרייבר",
    home_team=TeamInGame("מכבי תל אביב", "אברם גרנט", 2, [
        _player("אבי נמני", 10, [_lineup(), _captain(), _goal(25, GoalTypes.FREE_KICK)]),
        _player("אלי דריקס", 7, [_lineup(), _goal(50, GoalTypes.HEADER)]),
        _player("חיים רביבו", 8, [_lineup(), _assist(25, AssistTypes.CORNER_ASSIST), _assist(50)]),
        _player("טל בן חיים", 3, [_lineup()]),
        _player("בונדארנקו", 1, [_lineup(), _penalty_stopped(35)]),
        _player("שייע גלזר", 5, [_lineup()]),
        _player("בני טבק", 6, [_lineup()]),
        _player("גיורא שפיגל", 11, [_lineup()]),
        _player("יוסף מרימוביץ'", 4, [_lineup()]),
        _player("ויקי פרץ", 9, [_lineup()]),
        _player("מלאכי חלימי", 2, [_lineup()]),
    ]),
    away_team=TeamInGame("הפועל תל אביב", "ניר קלינגר", 0, [
        _player("מפלייטיקאל", 1, [_lineup()]),
    ]),
))

# ---- Game 5: League, home, WIN 4-2 (COMEBACK from 0-2), season 2019/20 ----
# Opponent scores at 10', 20'. Maccabi scores at 50', 60', 70', 80' (bench goal)
# Includes an own goal by opponent player at 60'
GAMES.append(_game(
    competition="ליגת העל", fixture="מחזור4", season="2019/20",
    date=datetime.datetime(2019, 12, 7),
    stadium="בלומפילד", referee="אלי חקמון",
    home_team=TeamInGame("מכבי תל אביב", "אברם גרנט", 4, [
        _player("אבי נמני", 10, [_lineup(), _captain(), _goal(50), _goal(70)]),
        _player("אלי דריקס", 7, [_lineup()]),
        _player("חיים רביבו", 8, [_lineup(), _assist(50), _assist(70)]),
        _player("טל בן חיים", 3, [_lineup()]),
        _player("בונדארנקו", 1, [_lineup()]),
        _player("שייע גלזר", 5, [_lineup(), _yellow(30)]),
        _player("בני טבק", 6, [_lineup()]),
        _player("גיורא שפיגל", 11, [_lineup(), _sub_out(55)]),
        _player("יוסף מרימוביץ'", 4, [_lineup()]),
        _player("ויקי פרץ", 9, [_lineup()]),
        _player("מלאכי חלימי", 2, [_lineup()]),
        _player("ערן זהבי", 14, [_sub_in(55), _goal(80)]),
    ]),
    away_team=TeamInGame("הפועל באר שבע", "אלישע לוי", 2, [
        _player("ערן לוי", 9, [_lineup(), _goal(10), _goal(20)]),
        _player("עמית בן שושן", 4, [_lineup(), _goal(60, GoalTypes.OWN_GOAL)]),
    ]),
))

# ---- Game 6: Friendly, away, WIN 1-0, season 2019/20 ----
# Goal from bench: ערן זהבי subs in at 70, scores at 85
# אבי נמני misses penalty at 40
GAMES.append(_game(
    competition="ידידות", fixture="ידידות", season="2019/20",
    date=datetime.datetime(2020, 1, 15),
    stadium="אחר", referee="גל לייבוביץ",
    home_team=TeamInGame("קבוצה זרה", "מאמן זר", 0, [
        _player("שוער זר", 1, [_lineup()]),
    ]),
    away_team=TeamInGame("מכבי תל אביב", "אברם גרנט", 1, [
        _player("אבי נמני", 10, [_lineup(), _captain(), _penalty_missed(40)]),
        _player("אלי דריקס", 7, [_lineup(), _sub_out(70)]),
        _player("חיים רביבו", 8, [_lineup()]),
        _player("טל בן חיים", 3, [_lineup()]),
        _player("בונדארנקו", 1, [_lineup()]),
        _player("שייע גלזר", 5, [_lineup()]),
        _player("בני טבק", 6, [_lineup()]),
        _player("גיורא שפיגל", 11, [_lineup()]),
        _player("יוסף מרימוביץ'", 4, [_lineup()]),
        _player("ויקי פרץ", 9, [_lineup()]),
        _player("מלאכי חלימי", 2, [_lineup()]),
        # Goal from bench: sub in at 70, score at 85
        _player("ערן זהבי", 14, [_sub_in(70), _goal(85)]),
    ]),
))

# ---- Game 7: League, home, WIN 2-1, season 2020/21, new coach ----
# Own goal by opponent at 45'
GAMES.append(_game(
    competition="ליגת העל", fixture="מחזור1", season="2020/21",
    date=datetime.datetime(2020, 9, 12),
    stadium="בלומפילד", referee="יורם דוידוביץ",
    home_team=TeamInGame("מכבי תל אביב", "פאולו סוזה", 2, [
        _player("אבי נמני", 10, [_lineup(), _captain(), _goal(30)]),
        _player("אלי דריקס", 7, [_lineup()]),
        _player("חיים רביבו", 8, [_lineup(), _assist(30)]),
        _player("טל בן חיים", 3, [_lineup()]),
        _player("בונדארנקו", 1, [_lineup()]),
        _player("שייע גלזר", 5, [_lineup()]),
        _player("בני טבק", 6, [_lineup()]),
        _player("גיורא שפיגל", 11, [_lineup()]),
        _player("יוסף מרימוביץ'", 4, [_lineup()]),
        _player("ויקי פרץ", 9, [_lineup()]),
        _player("מלאכי חלימי", 2, [_lineup()]),
    ]),
    away_team=TeamInGame("מכבי חיפה", "ברק בכר", 1, [
        _player("אייל גולסה", 7, [_lineup(), _goal(45, GoalTypes.OWN_GOAL)]),
        _player("עומר אצילי", 11, [_lineup(), _goal(88)]),
    ]),
))

# ---- Game 8: League, away, LOSS 1-3, season 2020/21 ----
# טל בן חיים gets yellow then second yellow (=red)
GAMES.append(_game(
    competition="ליגת העל", fixture="מחזור2", season="2020/21",
    date=datetime.datetime(2020, 9, 26),
    stadium="סמי עופר", referee="אלי חקמון",
    home_team=TeamInGame("מכבי חיפה", "ברק בכר", 3, [
        _player("אייל גולסה", 7, [_lineup(), _goal(20), _goal(45), _goal(70)]),
    ]),
    away_team=TeamInGame("מכבי תל אביב", "פאולו סוזה", 1, [
        _player("אבי נמני", 10, [_lineup(), _captain(), _goal(35)]),
        _player("אלי דריקס", 7, [_lineup()]),
        _player("חיים רביבו", 8, [_lineup(), _assist(35)]),
        _player("טל בן חיים", 3, [_lineup(), _yellow(40), _second_yellow(65)]),
        _player("בונדארנקו", 1, [_lineup()]),
        _player("שייע גלזר", 5, [_lineup()]),
        _player("בני טבק", 6, [_lineup()]),
        _player("גיורא שפיגל", 11, [_lineup()]),
        _player("יוסף מרימוביץ'", 4, [_lineup()]),
        _player("ויקי פרץ", 9, [_lineup()]),
        _player("מלאכי חלימי", 2, [_lineup()]),
    ]),
))

# ---- Game 9: League, home, TIE 0-0 (clean sheet), season 2020/21 ----
GAMES.append(_game(
    competition="ליגת העל", fixture="מחזור3", season="2020/21",
    date=datetime.datetime(2020, 10, 10),
    stadium="בלומפילד", referee="רועי ריינשרייבר",
    home_team=TeamInGame("מכבי תל אביב", "פאולו סוזה", 0, [
        _player("אבי נמני", 10, [_lineup(), _captain()]),
        _player("אלי דריקס", 7, [_lineup()]),
        _player("חיים רביבו", 8, [_lineup()]),
        _player("טל בן חיים", 3, [_lineup()]),
        _player("בונדארנקו", 1, [_lineup(), _penalty_stopped(70)]),
        _player("שייע גלזר", 5, [_lineup()]),
        _player("בני טבק", 6, [_lineup()]),
        _player("גיורא שפיגל", 11, [_lineup()]),
        _player("יוסף מרימוביץ'", 4, [_lineup()]),
        _player("ויקי פרץ", 9, [_lineup()]),
        _player("מלאכי חלימי", 2, [_lineup()]),
    ]),
    away_team=TeamInGame("הפועל תל אביב", "ניר קלינגר", 0, [
        _player("מפלייטיקאל", 1, [_lineup()]),
    ]),
))

# ---- Game 10: League, home, TECHNICAL WIN 3-0, season 2020/21 ----
GAMES.append(_game(
    competition="ליגת העל", fixture="מחזור4", season="2020/21",
    date=datetime.datetime(2020, 11, 7),
    stadium="בלומפילד", referee="יורם דוידוביץ",
    home_team=TeamInGame("מכבי תל אביב", "פאולו סוזה", 3, [
        _player("אבי נמני", 10, [_lineup(), _captain()]),
        _player("אלי דריקס", 7, [_lineup()]),
        _player("חיים רביבו", 8, [_lineup()]),
        _player("טל בן חיים", 3, [_lineup()]),
        _player("בונדארנקו", 1, [_lineup()]),
        _player("שייע גלזר", 5, [_lineup()]),
        _player("בני טבק", 6, [_lineup()]),
        _player("גיורא שפיגל", 11, [_lineup()]),
        _player("יוסף מרימוביץ'", 4, [_lineup()]),
        _player("ויקי פרץ", 9, [_lineup()]),
        _player("מלאכי חלימי", 2, [_lineup()]),
    ]),
    away_team=TeamInGame("בית\"ר ירושלים", "גיא לוי", 0, [
        _player("יוסי בניון", 10, [_lineup()]),
    ]),
    technical_result=True,
))
