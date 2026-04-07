import datetime
import json
from typing import List, Optional, Union, Dict

from dateutil.parser import parse as datetime_parser
from maccabistats.models.player_game_events import GameEventTypes, GoalTypes
from maccabistats.models.team_in_game import TeamInGame


class GameData(object):
    def __init__(self, competition: str, fixture: str, date_as_hebrew_string: str, stadium: str, crowd: str,
                 referee: str, home_team: TeamInGame, away_team: TeamInGame,
                 season_string: str, half_parsed_events: List[Dict], date: Optional[datetime.datetime] = None,
                 technical_result: bool = False):
        """
        :param season_string: season description, such as : 2000-2001 or 2000-01
        :param half_parsed_events: Events we could not parse and we save them for manual manipulation
        :param date: the date the game was played.
        :param technical_result: Whether this game was finished by a technical result,
                                 If so check the winner by the teams score directly
        """
        self.competition = competition
        self.fixture = fixture

        # todo get this shit out of here
        self.date_as_hebrew_string = date_as_hebrew_string
        self._full_date = self.__get_date_as_datetime() if date is None else date
        # Remove any resolution lower than a day,
        # So we can check a if game is played before another game without checking the hour
        # (it might be added and we want to compare two Games object from different times in the maccabipedia time)
        self.date = self._full_date.replace(hour=0, minute=0, second=0, microsecond=0)

        self.stadium = stadium
        self.crowd = crowd
        self.referee = referee
        self.home_team = home_team
        self.away_team = away_team
        self.season = season_string
        self._half_parsed_events = half_parsed_events
        self.technical_result = technical_result

    def played_before(self, date: Union[datetime.datetime, datetime.date, str]) -> bool:
        if isinstance(date, str):
            date = datetime_parser(date)

        return date >= self.date

    def played_after(self, date: Union[datetime.datetime, datetime.date, str]) -> bool:
        if isinstance(date, str):
            date = datetime_parser(date)

        return date <= self.date

    def __get_date_as_datetime(self) -> datetime.datetime:
        date_args = self.date_as_hebrew_string.strip().split(" ")

        return datetime.datetime(year=int(date_args[2]),
                                 month=GameData.__get_month_num_from_hebrew(date_args[1]),
                                 day=int(date_args[0]))

    @staticmethod
    def __get_month_num_from_hebrew(month_name: str) -> int:
        months_in_hebrew_to_num = {"ינו": 1, "פבר": 2, "מרץ": 3, "אפר": 4, "מאי": 5, "יונ": 6,
                                   "יול": 7, "אוג": 8, "ספט": 9, "אוק": 10, "נוב": 11, "דצמ": 12}

        return months_in_hebrew_to_num[month_name]

    @property
    def league_fixture(self) -> Optional[int]:
        try:
            return int(self.fixture.replace("מחזור", ""))
        except ValueError:
            return None

    @property
    def maccabi_score(self) -> int:
        return self.maccabi_team.score

    @property
    def maccabi_score_diff(self) -> int:
        return self.maccabi_team.score - self.not_maccabi_team.score

    @property
    def is_maccabi_home_team(self) -> bool:
        # TODO: handle games which are not played on "home\away", radius and so on
        return self.home_team.name in ["מכבי תל אביב", "מכבי תא", 'מכבי ת"א']

    @property
    def maccabi_team(self) -> TeamInGame:
        return self.home_team if self.is_maccabi_home_team else self.away_team

    @property
    def not_maccabi_team(self) -> TeamInGame:
        return self.away_team if self.is_maccabi_home_team else self.home_team

    @property
    def is_maccabi_win(self) -> bool:
        return self.maccabi_score_diff > 0

    @property
    def events(self) -> List[Dict]:
        """
        Return all players events from maccabi_team in this game.
        :return: Each list entry contains:
                    normal_players dict, event.to_json, team_name.
                List is ordered by event_time asc.
        """

        # Maccabi team players events
        players_events = [dict(player.get_as_normal_player().__dict__,  # Players attributes, normal -> no events.
                               **event.json_dict(),
                               team=self.maccabi_team.name)
                          for player in self.maccabi_team.players
                          for event in player.events]

        # Not maccabi team players events
        players_events.extend([dict(player.get_as_normal_player().__dict__,  # Players attributes, normal -> no events.
                                    **event.json_dict(),
                                    team=self.not_maccabi_team.name)
                               for player in self.not_maccabi_team.players
                               for event in player.events])

        sorted_players_events = sorted(players_events, key=lambda p: p['time_occur'])  # Sort by event time.

        return sorted_players_events

    def goals(self) -> List[Dict]:
        """
        Return list of game events which their type is goal (ordered by time).
        Each event contains the results of the game as it was AFTER the goal was scored.
        """

        goals_events = [event for event in self.events if event['event_type'] == GameEventTypes.GOAL_SCORE.value]
        maccabi_score = not_maccabi_score = 0

        for goal in goals_events:
            if goal['team'] == "מכבי תל אביב":
                if goal['goal_type'] == GoalTypes.OWN_GOAL.value:
                    not_maccabi_score += 1
                else:
                    maccabi_score += 1
            else:
                if goal['goal_type'] == GoalTypes.OWN_GOAL.value:
                    maccabi_score += 1
                else:
                    not_maccabi_score += 1

            goal['maccabi_score'] = maccabi_score
            goal['not_maccabi_score'] = not_maccabi_score

        return goals_events

    def maccabi_goals(self) -> List[Dict]:
        """
        Wrapper for self.goals, returns just maccabi goals (including own goals scored by the opponent)
        """
        return [goal for goal in self.goals() if
                (goal['team'] != 'מכבי תל אביב' and goal['goal_type'] == 'Own goal') or
                goal['team'] == 'מכבי תל אביב']

    def json_dict(self) -> Dict:
        return dict(stadium=self.stadium,
                    date=self.date.isoformat(),
                    crowd=self.crowd,
                    referee=self.referee,
                    competition=self.competition,
                    fixture=self.fixture,
                    home_team=self.home_team.json_dict(),
                    away_team=self.away_team.json_dict())

    def to_json(self) -> str:
        return json.dumps(self.json_dict())

    @property
    def _maccabipedia_page_name(self):
        return "{maccabipedia}/{prefix}:{date} {home_team} נגד {away_team} - {competition}".format(
            maccabipedia="https://www.maccabipedia.co.il",
            prefix="משחק",
            date=self.date.strftime('%d-%m-%Y'),
            home_team=self.home_team.name,
            away_team=self.away_team.name,
            competition=self.competition)

    def __repr__(self) -> str:
        return f"{self.date.date()} {self.competition}: {self.home_team.name}({self.home_team.score}) - ({self.away_team.score}){self.away_team.name}"

    def full_description(self) -> str:
        return "Game between {self.home_team.name} (home) - {self.away_team.name} (away)\n" \
               "Results : {self.home_team.score} - {self.away_team.score}\n" \
               "Played on {self.stadium} at {self.date} with {self.crowd} viewers\n" \
               "As part of {self.competition}, round - {self.fixture}\n" \
               "Referee : {self.referee}\n" \
               "HomeTeam : {self.home_team}\n" \
               "AwayTeam : {self.away_team}\n\n".format(self=self)
