from typing import Optional

from datetime import datetime

from pydantic import BaseModel, Field

class PlayerSummary(BaseModel):
    name: str
    number: Optional[int] = None
    # True / False / None: True → "כן", False → "לא", None → "" (unknown).
    is_starting_five: Optional[bool] = None
    minutes_played: Optional[int] = None
    total_points: int
    field_goals_attempts: int
    field_goals_scored: int
    three_scores_attempts: int
    three_scores_scored: int
    free_throws_attempts: int
    free_throws_scored: int
    defensive_rebounds: Optional[int] = None
    offensive_rebounds: Optional[int] = None
    total_rebounds: Optional[int] = None
    personal_total_fouls: Optional[int] = None
    personal_technical_fouls: Optional[int] = None
    steals: Optional[int] = None
    turnovers: Optional[int] = None
    assists: Optional[int] = None
    blocks: Optional[int] = None

    def __maccabipedia__(self) -> str:
        # Field order matches the existing wiki convention: 2pt before 3pt;
        # is_starting_five renders True→"כן", False→"לא", None→"" (unknown);
        # total_points falsy values (0 / None) render as empty so a DNP looks like "נק=" not "נק=0";
        # every other Optional[int] goes through `_blank_if_none` so a missing value
        # never leaks the string "None" into the wiki (e.g. jersey-less player → "מספר=").
        starting_five_str = {True: "כן", False: "לא"}.get(self.is_starting_five, "")
        b = _blank_if_none
        inner = " |".join([
            f"שם={self.name}",
            f"מספר={b(self.number)}",
            f"דקות={b(self.minutes_played)}",
            f"חמישייה={starting_five_str}",
            f"נק={self.total_points or ''}",
            f"זריקות עונשין={self.free_throws_attempts}",
            f"קליעות עונשין={self.free_throws_scored}",
            f"זריקות שתי נק={self.field_goals_attempts}",
            f"קליעות שתי נק={self.field_goals_scored}",
            f"זריקות שלוש נק={self.three_scores_attempts}",
            f"קליעות שלוש נק={self.three_scores_scored}",
            f"ריבאונד הגנה={b(self.defensive_rebounds)}",
            f"ריבאונד התקפה={b(self.offensive_rebounds)}",
            f"פאולים={b(self.personal_total_fouls)}",
            *(f"פאולים טכני={self.personal_technical_fouls}" if self.personal_technical_fouls is not None else []),
            f"חטיפות={b(self.steals)}",
            f"איבודים={b(self.turnovers)}",
            f"אסיסטים={b(self.assists)}",
            f"בלוקים={b(self.blocks)}",
        ])

        return f"{{{{אירועי שחקן סל |{inner}}}}}"


def _blank_if_none(value: Optional[int]) -> str:
    return "" if value is None else str(value)

class BasketballGame(BaseModel):
    home_team_name: str
    away_team_name: str
    competition: str
    fixture: str
    game_date: datetime
    home_team_score: int
    away_team_score: int
    game_url: list[str]
    has_overtime: Optional[bool] = None
    arena: Optional[str] = None
    first_quarter_maccabi_points: Optional[int] = None
    second_quarter_maccabi_points: Optional[int] = None
    third_quarter_maccabi_points: Optional[int] = None
    fourth_quarter_maccabi_points: Optional[int] = None
    first_overtime_maccabi_points: Optional[int] = None
    second_overtime_maccabi_points: Optional[int] = None
    third_overtime_maccabi_points: Optional[int] = None
    fourth_overtime_maccabi_points: Optional[int] = None
    first_quarter_opponent_points: Optional[int] = None
    second_quarter_opponent_points: Optional[int] = None
    third_quarter_opponent_points: Optional[int] = None
    fourth_quarter_opponent_points: Optional[int] = None
    first_overtime_opponent_points: Optional[int] = None
    second_overtime_opponent_points: Optional[int] = None
    fourth_overtime_opponent_points: Optional[int] = None
    third_overtime_opponent_points: Optional[int] = None
    first_half_maccabi_points: Optional[int] = None
    second_half_maccabi_points: Optional[int] = None
    first_half_opponent_points: Optional[int] = None
    second_half_opponent_points: Optional[int] = None
    season: Optional[str] = None
    hour: Optional[str] = None
    crowd: Optional[int] = None
    maccabi_coach: Optional[str] = None
    opponent_coach: Optional[str] = None
    referee: Optional[str] = None
    referee_assistants: Optional[list[str]] = Field(default_factory=list)
    maccabi_players: Optional[list[PlayerSummary]] = Field(default_factory=list)
    opponent_players: Optional[list[PlayerSummary]] = Field(default_factory=list)

    @property
    def opponent_name(self):
        if self.is_home_game:
            return self.away_team_name

        return self.home_team_name

    @property
    def maccabi_points(self):
        if self.is_home_game:
            return self.home_team_score

        return self.away_team_score

    @property
    def opponent_points(self):
        if self.is_home_game:
            return self.away_team_score

        return self.home_team_score

    @property
    def is_home_game(self):
        # TODO: validate that only home or away game is maccabi, on init
        return 'מכבי תל אביב' == self.home_team_name

    @classmethod
    def from_raw(cls, data: dict) -> 'BasketballGame':
        is_home = data["HomeAway"] != "חוץ"
        home_team = "מכבי תל אביב" if is_home else data["Opponent"]
        away_team = data["Opponent"] if is_home else "מכבי תל אביב"

        return cls(
            home_team_name=home_team,
            away_team_name=away_team,
            competition=data["Competition"],
            fixture="",
            game_date=datetime.strptime(data["Date"], "%d-%m-%Y"),
            home_team_score=data["TotalPointsMaccabi"] if is_home else data["TotalPointsOpponent"],
            away_team_score=data["TotalPointsOpponent"] if is_home else data["TotalPointsMaccabi"],
            game_url=data["GameUrl"],
        )
