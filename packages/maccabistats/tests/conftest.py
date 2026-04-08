import pytest

from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats

from game_fixtures import GAMES
from players_data_fixtures import create_stub_players_data


@pytest.fixture(scope="session")
def maccabi_games() -> MaccabiGamesStats:
    """A deterministic set of 10 synthetic games for offline testing."""
    return MaccabiGamesStats(GAMES, players_data=create_stub_players_data())
