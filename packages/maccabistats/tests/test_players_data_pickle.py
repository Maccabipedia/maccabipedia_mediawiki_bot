"""Test that MaccabiGamesStats includes players data in pickle for offline loading."""

import pickle
from datetime import datetime

import pytest

from maccabistats.maccabipedia.players import MaccabiPediaPlayers, MaccabiPediaPlayerData
from maccabistats.models.game_data import GameData
from maccabistats.models.player_in_game import PlayerInGame
from maccabistats.models.team_in_game import TeamInGame
from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats


@pytest.fixture(autouse=True)
def reset_players_singleton():
    yield
    MaccabiPediaPlayers._instance = None


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


def _make_players_instance():
    """Create a MaccabiPediaPlayers instance with test data."""
    players_data = {
        "שחקן א": MaccabiPediaPlayerData(name="שחקן א", birth_date=datetime(2000, 1, 1), is_home_player=True),
        "שחקן ב": MaccabiPediaPlayerData(name="שחקן ב", birth_date=datetime(1995, 6, 15), is_home_player=False),
    }
    return MaccabiPediaPlayers.load_from_cache(players_data)


def test_players_data_stored_as_attribute():
    """Players data should be stored as a regular attribute on MaccabiGamesStats."""
    players = _make_players_instance()
    games = [_make_game(datetime(2024, 9, 1))]
    stats = MaccabiGamesStats(games, maccabipedia_players=players)

    assert stats.maccabipedia_players is players
    assert stats.players_categories.maccabi_home_players_names == {"שחקן א"}


def test_pickle_roundtrip_preserves_players_data():
    """Pickling and unpickling should preserve the players data without crawling."""
    players = _make_players_instance()
    games = [_make_game(datetime(2024, 9, 1))]
    stats = MaccabiGamesStats(games, maccabipedia_players=players)

    pickled = pickle.dumps(stats)
    MaccabiPediaPlayers._instance = None

    restored = pickle.loads(pickled)
    assert restored.maccabipedia_players is not None
    assert restored.maccabipedia_players.home_players == {"שחקן א"}
    assert restored.maccabipedia_players.players_dates["שחקן ב"] == datetime(1995, 6, 15)


def test_filtered_stats_inherit_players_data(monkeypatch):
    """Filter properties (e.g. home_games) should inherit players data without crawling."""
    players = _make_players_instance()
    games = [_make_game(datetime(2024, 9, 1)), _make_game(datetime(2024, 10, 1))]
    stats = MaccabiGamesStats(games, maccabipedia_players=players)

    monkeypatch.setattr(
        MaccabiPediaPlayers, '_crawl_players_data',
        staticmethod(lambda: (_ for _ in ()).throw(RuntimeError("Should not crawl!"))),
    )
    MaccabiPediaPlayers._instance = None

    filtered = stats.maccabi_wins
    assert filtered.maccabipedia_players is players
    assert filtered.players_categories.maccabi_home_players_names == {"שחקן א"}


def test_unpickle_then_filter_works_offline(monkeypatch):
    """After unpickling, creating filtered stats should work without internet."""
    players = _make_players_instance()
    games = [_make_game(datetime(2024, 9, 1)), _make_game(datetime(2024, 10, 1))]
    stats = MaccabiGamesStats(games, maccabipedia_players=players)

    pickled = pickle.dumps(stats)
    MaccabiPediaPlayers._instance = None

    monkeypatch.setattr(
        MaccabiPediaPlayers, '_crawl_players_data',
        staticmethod(lambda: (_ for _ in ()).throw(RuntimeError("Should not crawl!"))),
    )

    restored = pickle.loads(pickled)
    filtered = MaccabiGamesStats(restored.games, maccabipedia_players=restored.maccabipedia_players)
    assert filtered.players_categories.maccabi_home_players_names == {"שחקן א"}


def test_empty_games_does_not_crawl(monkeypatch):
    """Creating MaccabiGamesStats with empty games should not trigger crawling."""
    monkeypatch.setattr(
        MaccabiPediaPlayers, '_crawl_players_data',
        staticmethod(lambda: (_ for _ in ()).throw(RuntimeError("Should not crawl!"))),
    )
    MaccabiPediaPlayers._instance = None

    stats = MaccabiGamesStats([])
    assert stats.maccabipedia_players is None


def test_old_pickle_without_players_data_falls_back_to_crawl():
    """Old pickles without maccabipedia_players should fall back to crawling (backward compat)."""
    players = _make_players_instance()
    games = [_make_game(datetime(2024, 9, 1))]
    stats = MaccabiGamesStats(games, maccabipedia_players=players)

    # Simulate an old pickle by removing the attribute before pickling
    del stats.__dict__['maccabipedia_players']
    pickled = pickle.dumps(stats)
    MaccabiPediaPlayers._instance = None

    # Loading through get_maccabi_stats_as_newest_wrapper-style path:
    # getattr(loaded, 'maccabipedia_players', None) returns None → __init__ falls back to crawl
    restored = pickle.loads(pickled)
    assert not hasattr(restored, 'maccabipedia_players')

    # When wrapping in a new MaccabiGamesStats, the fallback triggers crawl
    # (here we set up the singleton so it "crawls" from cache)
    MaccabiPediaPlayers.load_from_cache({
        "שחקן א": MaccabiPediaPlayerData(name="שחקן א", birth_date=datetime(2000, 1, 1), is_home_player=True),
    })
    wrapper = MaccabiGamesStats(
        restored.games,
        maccabipedia_players=getattr(restored, 'maccabipedia_players', None),
    )
    # Since getattr returns None and there are games, it falls back to singleton crawl
    assert wrapper.maccabipedia_players is not None


def test_load_from_cache_returns_instance():
    """load_from_cache should return the created instance."""
    players_data = {
        "שחקן א": MaccabiPediaPlayerData(name="שחקן א", birth_date=datetime(2000, 1, 1), is_home_player=True),
    }
    instance = MaccabiPediaPlayers.load_from_cache(players_data)
    assert instance is not None
    assert instance is MaccabiPediaPlayers._instance
    assert instance.home_players == {"שחקן א"}
