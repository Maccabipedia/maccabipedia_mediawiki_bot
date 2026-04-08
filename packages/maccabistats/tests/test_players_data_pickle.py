"""Test that MaccabiGamesStats includes players data in pickle for offline loading."""

import pickle
from datetime import datetime

from maccabistats.maccabipedia.players import MaccabiPediaPlayers, MaccabiPediaPlayerData
from maccabistats.models.game_data import GameData
from maccabistats.models.player_in_game import PlayerInGame
from maccabistats.models.team_in_game import TeamInGame
from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats


def _make_game(date: datetime) -> GameData:
    """Create a minimal GameData for testing."""
    maccabi = TeamInGame(name="מכבי תל אביב", coach="מאמן", score=1, players=[
        PlayerInGame(name="שחקן א", number=7, game_events=[]),
    ])
    opponent = TeamInGame(name="הפועל תל אביב", coach="מאמן2", score=0, players=[
        PlayerInGame(name="יריב א", number=9, game_events=[]),
    ])
    return GameData(
        competition="ליגת העל", fixture="1", date_as_hebrew_string="",
        stadium="בלומפילד", crowd="1000", referee="שופט",
        home_team=maccabi, away_team=opponent,
        season_string="2024/25", half_parsed_events=[], date=date,
    )


def _setup_players_singleton():
    """Set up MaccabiPediaPlayers singleton with test data."""
    players_data = {
        "שחקן א": MaccabiPediaPlayerData(name="שחקן א", birth_date=datetime(2000, 1, 1), is_home_player=True),
        "שחקן ב": MaccabiPediaPlayerData(name="שחקן ב", birth_date=datetime(1995, 6, 15), is_home_player=False),
    }
    MaccabiPediaPlayers.load_from_cache(players_data)
    return players_data


def test_pickle_includes_players_data():
    """Players data should be included in the pickle state."""
    _setup_players_singleton()
    games = [_make_game(datetime(2024, 9, 1))]
    stats = MaccabiGamesStats(games)

    state = stats.__getstate__()
    assert '_players_data_cache' in state
    assert "שחקן א" in state['_players_data_cache']
    assert "שחקן ב" in state['_players_data_cache']

    # Clean up singleton
    MaccabiPediaPlayers._instance = None


def test_unpickle_restores_players_singleton():
    """Unpickling should restore the MaccabiPediaPlayers singleton without internet."""
    original_data = _setup_players_singleton()
    games = [_make_game(datetime(2024, 9, 1))]
    stats = MaccabiGamesStats(games)

    # Pickle and clear singleton
    pickled = pickle.dumps(stats)
    MaccabiPediaPlayers._instance = None

    # Unpickle - should restore singleton from cache
    restored = pickle.loads(pickled)
    assert MaccabiPediaPlayers._instance is not None
    assert MaccabiPediaPlayers.get_players_data().home_players == {"שחקן א"}
    assert MaccabiPediaPlayers.get_players_data().players_dates["שחקן ב"] == datetime(1995, 6, 15)

    # Clean up
    MaccabiPediaPlayers._instance = None


def test_unpickle_then_create_new_stats_works_offline(monkeypatch):
    """After unpickling, creating new MaccabiGamesStats (e.g. filtering) should not crawl."""
    _setup_players_singleton()
    games = [_make_game(datetime(2024, 9, 1)), _make_game(datetime(2024, 10, 1))]
    stats = MaccabiGamesStats(games)

    pickled = pickle.dumps(stats)
    MaccabiPediaPlayers._instance = None

    # Block any network crawling - if it tries to crawl, the test fails
    monkeypatch.setattr(
        MaccabiPediaPlayers, '_crawl_players_data',
        staticmethod(lambda: (_ for _ in ()).throw(RuntimeError("Should not crawl!"))),
    )

    restored = pickle.loads(pickled)
    # Creating a new MaccabiGamesStats from the restored games (like filter properties do)
    # should use the already-populated singleton
    filtered = MaccabiGamesStats(restored.games)
    assert filtered.players_categories.maccabi_home_players_names == {"שחקן א"}

    # Clean up
    MaccabiPediaPlayers._instance = None


def test_backwards_compatible_with_old_pickles():
    """Old pickle files without players data should still work (falling back to crawl)."""
    _setup_players_singleton()
    games = [_make_game(datetime(2024, 9, 1))]
    stats = MaccabiGamesStats(games)

    # Simulate an old pickle without _players_data_cache
    state = stats.__getstate__()
    del state['_players_data_cache']

    MaccabiPediaPlayers._instance = None
    stats2 = object.__new__(MaccabiGamesStats)
    stats2.__setstate__(state)

    # Singleton should still be None (no cache to restore from)
    assert MaccabiPediaPlayers._instance is None

    # Clean up
    MaccabiPediaPlayers._instance = None
