from typing import Optional

from datetime import datetime

from pydantic import BaseModel, Field

class PlayerSummary(BaseModel):
    name: str
    number: int
    is_starting_five: bool
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
    personal_total_fouls: Optional[int] = None
    personal_technical_fouls: Optional[int] = None
    steals: Optional[int] = None
    turnovers: Optional[int] = None
    assists: Optional[int] = None
    blocks: Optional[int] = None

    def __maccabipedia__(self) -> str:
        inner = "| ".join([
            f"שם={self.name}",
            f"מספר={self.number}",
            f"חמישייה={'כן' if self.is_starting_five else 'לא'}",
            f"נק={self.total_points}",
            f"נק מהקו נסיון={self.field_goals_attempts}",
            f"נק מהקו קלע={self.field_goals_scored}",
            f"נק מהשלוש נסיון={self.three_scores_attempts}",
            f"נק מהשלוש קלע={self.three_scores_scored}",
            f"נק מהצבע נסיון={self.free_throws_attempts}",
            f"נק מהצבע קלע={self.free_throws_scored}",
            f"ריבאונד הגנה={self.defensive_rebounds}",
            f"ריבאונד התקפה={self.offensive_rebounds}",
            f"פאולים={self.personal_total_fouls}",
            *(f"פאולים טכני={self.personal_technical_fouls}" if self.personal_technical_fouls is not None else []),
            f"חטיפות={self.steals}",
            f"איבודים={self.turnovers}",
            f"אסיסטים={self.assists}",
            f"בלוקים={self.blocks}"
        ])

        return f"{{{{אירועי שחקן סל| {inner} }}}}"

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
    stadium: Optional[str] = None
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
    season: Optional[str] = None
    hour: Optional[str] = None
    crowd: Optional[int] = None
    maccabi_coach: Optional[str] = None
    opponent_coach: Optional[str] = None
    referee: Optional[str] = None
    referee_assistants: Optional[list[str]] = Field(default_factory=[])
    maccabi_players: Optional[list[PlayerSummary]] = Field(default_factory=[])
    opponent_players: Optional[list[PlayerSummary]] = Field(default_factory=[])

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
