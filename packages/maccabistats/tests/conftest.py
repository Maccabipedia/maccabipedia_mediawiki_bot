from collections import defaultdict
from datetime import datetime

import pytest

from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats

from game_fixtures import GAMES

# Minimal mock for MaccabiPediaPlayers data required by players_categories and players_special_games.
# Declares the first two fixture players as "home players"; all others are foreign.
_DEFAULT_BIRTH_DATE = datetime(year=1000, month=1, day=1)
_HOME_PLAYERS = {"אבי נמני", "אלי דריקס"}


class _MockPlayersData:
    def __init__(self):
        self.home_players = _HOME_PLAYERS
        self.players_dates = defaultdict(lambda: _DEFAULT_BIRTH_DATE)


def mock_players_data():
    """Create a mock players_data for offline MaccabiGamesStats construction."""
    return _MockPlayersData()


@pytest.fixture(scope="session")
def maccabi_games() -> MaccabiGamesStats:
    """A deterministic set of 10 synthetic games for offline testing."""
    return MaccabiGamesStats(GAMES, players_data=mock_players_data())
