"""
Shared fixtures for maccabistats tests.

Builds a small set of synthetic games that cover the key scenarios:
  - Wins, losses, ties
  - Home and away games
  - Multiple competitions (league, cup, friendly)
  - Two seasons
  - Goals from bench (sub-in then score)
  - Own goals
  - A comeback game
  - A technical result
  - Multiple coaches, referees, stadiums, opponents
  - Various player events: lineup, sub in/out, goals, assists, yellow/red cards, captain
"""
import datetime
from datetime import timedelta

import pytest

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
from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats


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
# Season 2019/20 — 6 games, Season 2020/21 — 4 games
# Competitions: "ליגת העל" (league), "גביע המדינה" (cup), "ידידות" (friendly)
# Results: 5 wins, 2 losses, 2 ties, 1 technical win
# Home: 6 games, Away: 4 games

GAMES: list[GameData] = []

# ---- Game 1: League, home, WIN 3-1, season 2019/20 ----
# Maccabi scores 3 (player_a x2, player_b x1), opponent scores 1
# player_a is captain, player_c assists twice
GAMES.append(_game(
    competition="ליגת העל", fixture="מחזור1", season="2019/20",
    date=datetime.datetime(2019, 9, 14),
    stadium="בלומפילד", referee="שופט_א",
    home_team=TeamInGame("מכבי תל אביב", "מאמן_א", 3, [
        _player("שחקן_א", 10, [_lineup(), _captain(), _goal(15), _goal(70)]),
        _player("שחקן_ב", 7, [_lineup(), _goal(40, GoalTypes.HEADER)]),
        _player("שחקן_ג", 8, [_lineup(), _assist(15), _assist(40)]),
        _player("שחקן_ד", 3, [_lineup()]),
        _player("שחקן_ה", 1, [_lineup()]),
        _player("שחקן_ו", 5, [_lineup()]),
        _player("שחקן_ז", 6, [_lineup()]),
        _player("שחקן_ח", 11, [_lineup()]),
        _player("שחקן_ט", 4, [_lineup()]),
        _player("שחקן_י", 9, [_lineup()]),
        _player("שחקן_יא", 2, [_lineup()]),
    ]),
    away_team=TeamInGame("הפועל באר שבע", "מאמן_יריב_א", 1, [
        _player("יריב_א", 9, [_lineup(), _goal(55)]),
    ]),
))

# ---- Game 2: League, away, LOSS 0-2, season 2019/20 ----
GAMES.append(_game(
    competition="ליגת העל", fixture="מחזור2", season="2019/20",
    date=datetime.datetime(2019, 9, 21),
    stadium="טדי", referee="שופט_ב",
    home_team=TeamInGame("בית\"ר ירושלים", "מאמן_יריב_ב", 2, [
        _player("יריב_ב", 10, [_lineup(), _goal(30), _goal(60)]),
    ]),
    away_team=TeamInGame("מכבי תל אביב", "מאמן_א", 0, [
        _player("שחקן_א", 10, [_lineup(), _captain(), _yellow(50)]),
        _player("שחקן_ב", 7, [_lineup()]),
        _player("שחקן_ג", 8, [_lineup(), _sub_out(60)]),
        _player("שחקן_ד", 3, [_lineup()]),
        _player("שחקן_ה", 1, [_lineup()]),
        _player("שחקן_ו", 5, [_lineup()]),
        _player("שחקן_ז", 6, [_lineup()]),
        _player("שחקן_ח", 11, [_lineup()]),
        _player("שחקן_ט", 4, [_lineup()]),
        _player("שחקן_י", 9, [_lineup()]),
        _player("שחקן_יא", 2, [_lineup()]),
        _player("שחקן_יב", 14, [_sub_in(60)]),
    ]),
))

# ---- Game 3: League, home, TIE 1-1, season 2019/20 ----
GAMES.append(_game(
    competition="ליגת העל", fixture="מחזור3", season="2019/20",
    date=datetime.datetime(2019, 10, 5),
    stadium="בלומפילד", referee="שופט_א",
    home_team=TeamInGame("מכבי תל אביב", "מאמן_א", 1, [
        _player("שחקן_א", 10, [_lineup(), _captain(), _goal(80, GoalTypes.PENALTY)]),
        _player("שחקן_ב", 7, [_lineup()]),
        _player("שחקן_ג", 8, [_lineup()]),
        _player("שחקן_ד", 3, [_lineup()]),
        _player("שחקן_ה", 1, [_lineup()]),
        _player("שחקן_ו", 5, [_lineup()]),
        _player("שחקן_ז", 6, [_lineup()]),
        _player("שחקן_ח", 11, [_lineup()]),
        _player("שחקן_ט", 4, [_lineup()]),
        _player("שחקן_י", 9, [_lineup()]),
        _player("שחקן_יא", 2, [_lineup()]),
    ]),
    away_team=TeamInGame("מכבי חיפה", "מאמן_יריב_ג", 1, [
        _player("יריב_ג", 7, [_lineup(), _goal(20)]),
    ]),
))

# ---- Game 4: Cup, home, WIN 2-0 (clean sheet), season 2019/20 ----
GAMES.append(_game(
    competition="גביע המדינה", fixture="שמינית גמר", season="2019/20",
    date=datetime.datetime(2019, 11, 12),
    stadium="בלומפילד", referee="שופט_ג",
    home_team=TeamInGame("מכבי תל אביב", "מאמן_א", 2, [
        _player("שחקן_א", 10, [_lineup(), _captain(), _goal(25, GoalTypes.FREE_KICK)]),
        _player("שחקן_ב", 7, [_lineup(), _goal(50)]),
        _player("שחקן_ג", 8, [_lineup(), _assist(25), _assist(50)]),
        _player("שחקן_ד", 3, [_lineup()]),
        _player("שחקן_ה", 1, [_lineup()]),
        _player("שחקן_ו", 5, [_lineup()]),
        _player("שחקן_ז", 6, [_lineup()]),
        _player("שחקן_ח", 11, [_lineup()]),
        _player("שחקן_ט", 4, [_lineup()]),
        _player("שחקן_י", 9, [_lineup()]),
        _player("שחקן_יא", 2, [_lineup()]),
    ]),
    away_team=TeamInGame("הפועל תל אביב", "מאמן_יריב_ד", 0, [
        _player("יריב_ד", 1, [_lineup()]),
    ]),
))

# ---- Game 5: League, home, WIN 4-2 (COMEBACK from 0-2), season 2019/20 ----
# Opponent scores 2, then Maccabi scores 4 (including own goal by opponent)
GAMES.append(_game(
    competition="ליגת העל", fixture="מחזור4", season="2019/20",
    date=datetime.datetime(2019, 12, 7),
    stadium="בלומפילד", referee="שופט_ב",
    home_team=TeamInGame("מכבי תל אביב", "מאמן_א", 4, [
        _player("שחקן_א", 10, [_lineup(), _captain(), _goal(50), _goal(70)]),
        _player("שחקן_ב", 7, [_lineup(), _goal(60)]),
        _player("שחקן_ג", 8, [_lineup(), _assist(50), _assist(60)]),
        _player("שחקן_ד", 3, [_lineup()]),
        _player("שחקן_ה", 1, [_lineup()]),
        _player("שחקן_ו", 5, [_lineup(), _yellow(30)]),
        _player("שחקן_ז", 6, [_lineup()]),
        _player("שחקן_ח", 11, [_lineup(), _sub_out(55)]),
        _player("שחקן_ט", 4, [_lineup()]),
        _player("שחקן_י", 9, [_lineup()]),
        _player("שחקן_יא", 2, [_lineup()]),
        _player("שחקן_יב", 14, [_sub_in(55), _goal(80, GoalTypes.NORMAL_KICK)]),
    ]),
    away_team=TeamInGame("הפועל באר שבע", "מאמן_יריב_א", 2, [
        _player("יריב_א", 9, [_lineup(), _goal(10), _goal(20)]),
    ]),
))

# ---- Game 6: Friendly, away, WIN 1-0, season 2019/20 ----
GAMES.append(_game(
    competition="ידידות", fixture="ידידות", season="2019/20",
    date=datetime.datetime(2020, 1, 15),
    stadium="אחר", referee="שופט_ד",
    home_team=TeamInGame("קבוצה זרה", "מאמן_יריב_ה", 0, [
        _player("יריב_ה", 1, [_lineup()]),
    ]),
    away_team=TeamInGame("מכבי תל אביב", "מאמן_א", 1, [
        _player("שחקן_א", 10, [_lineup(), _captain()]),
        _player("שחקן_ב", 7, [_lineup(), _sub_out(70)]),
        _player("שחקן_ג", 8, [_lineup()]),
        _player("שחקן_ד", 3, [_lineup()]),
        _player("שחקן_ה", 1, [_lineup()]),
        _player("שחקן_ו", 5, [_lineup()]),
        _player("שחקן_ז", 6, [_lineup()]),
        _player("שחקן_ח", 11, [_lineup()]),
        _player("שחקן_ט", 4, [_lineup()]),
        _player("שחקן_י", 9, [_lineup()]),
        _player("שחקן_יא", 2, [_lineup()]),
        # Goal from bench: sub in at 70, score at 85
        _player("שחקן_יב", 14, [_sub_in(70), _goal(85)]),
    ]),
))

# ---- Game 7: League, home, WIN 2-1, season 2020/21, new coach ----
GAMES.append(_game(
    competition="ליגת העל", fixture="מחזור1", season="2020/21",
    date=datetime.datetime(2020, 9, 12),
    stadium="בלומפילד", referee="שופט_א",
    home_team=TeamInGame("מכבי תל אביב", "מאמן_ב", 2, [
        _player("שחקן_א", 10, [_lineup(), _captain(), _goal(30)]),
        _player("שחקן_ב", 7, [_lineup(), _goal(75)]),
        _player("שחקן_ג", 8, [_lineup(), _assist(30), _assist(75)]),
        _player("שחקן_ד", 3, [_lineup()]),
        _player("שחקן_ה", 1, [_lineup()]),
        _player("שחקן_ו", 5, [_lineup()]),
        _player("שחקן_ז", 6, [_lineup()]),
        _player("שחקן_ח", 11, [_lineup()]),
        _player("שחקן_ט", 4, [_lineup()]),
        _player("שחקן_י", 9, [_lineup()]),
        _player("שחקן_יא", 2, [_lineup()]),
    ]),
    away_team=TeamInGame("מכבי חיפה", "מאמן_יריב_ג", 1, [
        _player("יריב_ג", 7, [_lineup(), _goal(88)]),
    ]),
))

# ---- Game 8: League, away, LOSS 1-3, season 2020/21, player gets red card ----
GAMES.append(_game(
    competition="ליגת העל", fixture="מחזור2", season="2020/21",
    date=datetime.datetime(2020, 9, 26),
    stadium="סמי עופר", referee="שופט_ב",
    home_team=TeamInGame("מכבי חיפה", "מאמן_יריב_ג", 3, [
        _player("יריב_ג", 7, [_lineup(), _goal(20), _goal(45), _goal(70)]),
    ]),
    away_team=TeamInGame("מכבי תל אביב", "מאמן_ב", 1, [
        _player("שחקן_א", 10, [_lineup(), _captain(), _goal(35)]),
        _player("שחקן_ב", 7, [_lineup()]),
        _player("שחקן_ג", 8, [_lineup(), _assist(35)]),
        _player("שחקן_ד", 3, [_lineup(), _yellow(40), _second_yellow(65)]),
        _player("שחקן_ה", 1, [_lineup()]),
        _player("שחקן_ו", 5, [_lineup()]),
        _player("שחקן_ז", 6, [_lineup()]),
        _player("שחקן_ח", 11, [_lineup()]),
        _player("שחקן_ט", 4, [_lineup()]),
        _player("שחקן_י", 9, [_lineup()]),
        _player("שחקן_יא", 2, [_lineup()]),
    ]),
))

# ---- Game 9: League, home, TIE 0-0 (clean sheet), season 2020/21 ----
GAMES.append(_game(
    competition="ליגת העל", fixture="מחזור3", season="2020/21",
    date=datetime.datetime(2020, 10, 10),
    stadium="בלומפילד", referee="שופט_ג",
    home_team=TeamInGame("מכבי תל אביב", "מאמן_ב", 0, [
        _player("שחקן_א", 10, [_lineup(), _captain()]),
        _player("שחקן_ב", 7, [_lineup()]),
        _player("שחקן_ג", 8, [_lineup()]),
        _player("שחקן_ד", 3, [_lineup()]),
        _player("שחקן_ה", 1, [_lineup()]),
        _player("שחקן_ו", 5, [_lineup()]),
        _player("שחקן_ז", 6, [_lineup()]),
        _player("שחקן_ח", 11, [_lineup()]),
        _player("שחקן_ט", 4, [_lineup()]),
        _player("שחקן_י", 9, [_lineup()]),
        _player("שחקן_יא", 2, [_lineup()]),
    ]),
    away_team=TeamInGame("הפועל תל אביב", "מאמן_יריב_ד", 0, [
        _player("יריב_ד", 1, [_lineup()]),
    ]),
))

# ---- Game 10: League, home, TECHNICAL WIN 3-0, season 2020/21 ----
GAMES.append(_game(
    competition="ליגת העל", fixture="מחזור4", season="2020/21",
    date=datetime.datetime(2020, 11, 7),
    stadium="בלומפילד", referee="שופט_א",
    home_team=TeamInGame("מכבי תל אביב", "מאמן_ב", 3, [
        _player("שחקן_א", 10, [_lineup(), _captain()]),
        _player("שחקן_ב", 7, [_lineup()]),
        _player("שחקן_ג", 8, [_lineup()]),
        _player("שחקן_ד", 3, [_lineup()]),
        _player("שחקן_ה", 1, [_lineup()]),
        _player("שחקן_ו", 5, [_lineup()]),
        _player("שחקן_ז", 6, [_lineup()]),
        _player("שחקן_ח", 11, [_lineup()]),
        _player("שחקן_ט", 4, [_lineup()]),
        _player("שחקן_י", 9, [_lineup()]),
        _player("שחקן_יא", 2, [_lineup()]),
    ]),
    away_team=TeamInGame("בית\"ר ירושלים", "מאמן_יריב_ב", 0, [
        _player("יריב_ב", 10, [_lineup()]),
    ]),
    technical_result=True,
))


@pytest.fixture(scope="session")
def maccabi_games() -> MaccabiGamesStats:
    """A deterministic set of 10 synthetic games for offline testing."""
    return MaccabiGamesStats(GAMES)
