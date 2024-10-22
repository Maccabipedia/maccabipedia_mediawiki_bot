from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class VolleyballGame:
    date: datetime
    fixture: str
    opponent: str
    home_game: bool
    competition: str
    season: str
    stadium: Optional[str] = None
    maccabi_result: Optional[int] = None
    opponent_result: Optional[int] = None

    @property
    def home_team(self):
        if self.home_game:
            return 'מכבי תל אביב'

        return self.opponent

    @property
    def away_team(self):
        if self.home_game:
            return self.opponent

        return 'מכבי תל אביב'
