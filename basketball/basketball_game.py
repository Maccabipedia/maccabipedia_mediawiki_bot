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
    defensive_rebounds:  Optional[int] = None
    offensive_rebounds:  Optional[int] = None
    personal_total_fouls:  Optional[int] = None
    personal_technical_fouls: Optional[int] = None
    steals:  Optional[int] = None
    turnovers:  Optional[int] = None
    assists:  Optional[int] = None
    blocks:  Optional[int] = None

class BasketballGame(BaseModel):
    home_team_name: str
    away_team_name: str
    competition: str
    fixture: str
    game_date: datetime
    home_team_score: int
    away_team_score: int
    game_url: list[str]
    has_overtime: bool
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
    referee_assistants: list[str] = Field(default_factory=[])
    maccabi_players: list[PlayerSummary] = Field(default_factory=[])
    opponent_players: list[PlayerSummary] = Field(default_factory=[])

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
