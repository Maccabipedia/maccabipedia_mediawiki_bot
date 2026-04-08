import pytest

from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats

from game_fixtures import GAMES


@pytest.fixture(scope="session")
def maccabi_games() -> MaccabiGamesStats:
    """A deterministic set of 10 synthetic games for offline testing."""
    return MaccabiGamesStats(GAMES)
