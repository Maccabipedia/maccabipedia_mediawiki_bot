import pytest
from maccabistats import load_from_maccabipedia_source
from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats


@pytest.fixture(scope="session")
def maccabipedia_maccabistats() -> MaccabiGamesStats:
    return load_from_maccabipedia_source()
