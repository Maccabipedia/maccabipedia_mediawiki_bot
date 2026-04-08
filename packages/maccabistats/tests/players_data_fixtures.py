"""
Stub players data for offline MaccabiGamesStats construction.

Replaces the live MaccabiPediaPlayers singleton with static test data.
Declares אבי נמני and אלי דריקס as "home players"; all others are foreign.
Birth dates default to year 1000 (matching MaccabiPediaPlayers.missing_birth_date_value).
"""
from collections import defaultdict
from datetime import datetime

DEFAULT_BIRTH_DATE = datetime(year=1000, month=1, day=1)
HOME_PLAYERS = {"אבי נמני", "אלי דריקס"}


class StubPlayersData:
    def __init__(self):
        self.home_players = HOME_PLAYERS
        self.players_dates = defaultdict(lambda: DEFAULT_BIRTH_DATE)


def create_stub_players_data() -> StubPlayersData:
    return StubPlayersData()
