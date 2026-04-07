from __future__ import annotations

import datetime
import json
import logging
from collections import defaultdict
from tempfile import NamedTemporaryFile
from typing import List, Union, Dict, Any, DefaultDict

from dateutil.parser import parse as datetime_parser

from maccabistats.models.game_data import GameData
from maccabistats.models.player import Player
from maccabistats.stats.averages import MaccabiGamesAverageStats
from maccabistats.stats.coaches import MaccabiGamesCoachesStats
from maccabistats.stats.comebacks import MaccabiGamesComebacksStats
from maccabistats.stats.consts import TROPHY_COMPETITIONS, EUROPE_COMPETITIONS, LEAGUE_COMPETITIONS, \
    NON_OFFICIAL_COMPETITIONS
from maccabistats.stats.export import ExportMaccabiGamesStats
from maccabistats.stats.goals_timing import MaccabiGamesGoalsTiming
from maccabistats.stats.graphs import MaccabiGamesGraphsStats
from maccabistats.stats.important_goals import MaccabiGamesImportantGoalsStats
from maccabistats.stats.players import MaccabiGamesPlayersStats
from maccabistats.stats.players_and_teams_streaks import PlayersAndTeamsStreaksStats
from maccabistats.stats.players_categories import MaccabiGamesPlayersCategoriesStats
from maccabistats.stats.players_events_sumamry import MaccabiGamesPlayersEventsSummaryStats
from maccabistats.stats.players_first_and_last_games import MaccabiGamesPlayersFirstAndLastGamesStats
from maccabistats.stats.players_special_games import MaccabiGamesPlayersSpecialGamesStats
from maccabistats.stats.players_streaks import MaccabiGamesPlayersStreaksStats
from maccabistats.stats.referees import MaccabiGamesRefereesStats
from maccabistats.stats.results import MaccabiGamesResultsStats
from maccabistats.stats.seasons import MaccabiGamesSeasonsStats
from maccabistats.stats.streaks import MaccabiGamesStreaksStats
from maccabistats.stats.summary import MaccabiGamesSummary
from maccabistats.stats.teams import MaccabiGamesTeamsStats
from maccabistats.stats.teams_names_convertor import TeamNamesConvertor
from maccabistats.stats.teams_streaks import MaccabiGamesTeamsStreaksStats
from maccabistats.stats_utilities.points_calculator import calculate_points_for_games, \
    calculate_possible_points_for_games
from maccabistats.version import version as maccabistats_version

logger = logging.getLogger(__name__)


class MaccabiGamesStats:
    _DEFAULT_DESCRIPTION = 'All games'

    def __init__(self, games: List[GameData], description: str = None) -> None:
        self.games: List[GameData] = sorted(games, key=lambda g: g.date)  # Sort the games by date
        self.description = description or self._DEFAULT_DESCRIPTION

        self.coaches = MaccabiGamesCoachesStats(self)
        self.players = MaccabiGamesPlayersStats(self)
        self.streaks = MaccabiGamesStreaksStats(self)
        self.averages = MaccabiGamesAverageStats(self)
        self.results = MaccabiGamesResultsStats(self)
        self.referees = MaccabiGamesRefereesStats(self)
        self.comebacks = MaccabiGamesComebacksStats(self)
        self.important_goals = MaccabiGamesImportantGoalsStats(self)
        self.graphs = MaccabiGamesGraphsStats(self)
        self.players_streaks = MaccabiGamesPlayersStreaksStats(self)
        self.teams_streaks = MaccabiGamesTeamsStreaksStats(self)
        self.teams = MaccabiGamesTeamsStats(self)
        self.players_events_summary = MaccabiGamesPlayersEventsSummaryStats(self)
        self.players_special_games = MaccabiGamesPlayersSpecialGamesStats(self)
        self.players_first_and_last_games = MaccabiGamesPlayersFirstAndLastGamesStats(self)
        self.players_categories = MaccabiGamesPlayersCategoriesStats(self)
        self.summary = MaccabiGamesSummary(self)
        self.goals_timing = MaccabiGamesGoalsTiming(self)
        self.export = ExportMaccabiGamesStats(self)
        self.players_and_teams_streaks = PlayersAndTeamsStreaksStats(self)

        self.seasons = MaccabiGamesSeasonsStats(self)
        self._team_names_convertor = TeamNamesConvertor(self)

        self.version = maccabistats_version

    # region home_away

    @property
    def home_games(self) -> MaccabiGamesStats:
        return MaccabiGamesStats([game for game in self.games if game.is_maccabi_home_team],
                                 self._new_description('Home games'))

    @property
    def away_games(self) -> MaccabiGamesStats:
        return MaccabiGamesStats([game for game in self.games if not game.is_maccabi_home_team],
                                 self._new_description('Away games'))

    # endregion

    # region competitions filters

    @property
    def trophy_games(self) -> MaccabiGamesStats:
        return MaccabiGamesStats([game for game in self.games if game.competition in TROPHY_COMPETITIONS],
                                 self._new_description('Trophy games'))

    @property
    def europe_games(self) -> MaccabiGamesStats:
        return MaccabiGamesStats([game for game in self.games if game.competition in EUROPE_COMPETITIONS],
                                 self._new_description('Europe games'))

    @property
    def league_games(self) -> MaccabiGamesStats:
        return MaccabiGamesStats([game for game in self.games if game.competition in LEAGUE_COMPETITIONS],
                                 self._new_description('League games'))

    @property
    def official_games(self) -> MaccabiGamesStats:
        return MaccabiGamesStats([game for game in self.games if game.competition not in NON_OFFICIAL_COMPETITIONS],
                                 self._new_description('Official games'))

    @property
    def non_official_games(self) -> MaccabiGamesStats:
        return MaccabiGamesStats([game for game in self.games if game.competition in NON_OFFICIAL_COMPETITIONS],
                                 self._new_description(f'Non-official games'))

    # endregion

    # region available properties

    @property
    def available_competitions(self) -> List[str]:
        return list(set(game.competition for game in self.games))

    @property
    def available_opponents(self) -> List[str]:
        return list(set(game.not_maccabi_team.name for game in self.games))

    @property
    def available_stadiums(self) -> List[str]:
        return list(set(game.stadium for game in self.games))

    @property
    def available_players(self) -> List[Player]:
        """
        Returns players objects (name + number), Which means a player name can appear more than once.
        """
        players = set(player for game in self.games for player in game.maccabi_team.players)
        return list(set([player.get_as_normal_player() for player in players]))

    @property
    def available_players_names(self) -> List[str]:
        return list(set(player.name for player in self.available_players))

    @property
    def available_referees(self) -> List[str]:
        return list(set(game.referee for game in self.games))

    @property
    def available_coaches(self) -> List[str]:
        return list(set(game.maccabi_team.coach for game in self.games))

    @property
    def available_seasons(self) -> List[str]:
        return sorted(list(set(game.season for game in self.games)))

    # endregion

    # region result based

    @property
    def maccabi_wins(self) -> MaccabiGamesStats:
        return MaccabiGamesStats([game for game in self.games if game.is_maccabi_win],
                                 self._new_description('Wins only'))

    @property
    def maccabi_ties(self) -> MaccabiGamesStats:
        return MaccabiGamesStats([game for game in self.games if game.maccabi_score_diff == 0],
                                 self._new_description('Ties only'))

    @property
    def maccabi_losses(self) -> MaccabiGamesStats:
        return MaccabiGamesStats([game for game in self.games if game.maccabi_score_diff < 0],
                                 self._new_description('Losses only'))

    @property
    def technical_result_games(self) -> MaccabiGamesStats:
        return MaccabiGamesStats([game for game in self.games if game.technical_result],
                                 self._new_description('Technical games'))

    # endregion

    # region date based

    def played_before(self, date: Union[datetime.datetime, datetime.date, str]) -> MaccabiGamesStats:
        return MaccabiGamesStats([game for game in self.games if game.played_before(date)],
                                 self._new_description(f'Played before: {date}'))

    def played_after(self, date: Union[datetime.datetime, datetime.date, str]) -> MaccabiGamesStats:
        return MaccabiGamesStats([game for game in self.games if game.played_after(date)],
                                 self._new_description(f'Player after: {date}'))

    def played_at(self, date: Union[datetime.datetime, datetime.date, str]) -> MaccabiGamesStats:
        if isinstance(date, str):
            date = datetime_parser(date, dayfirst=True).date()
        elif isinstance(date, datetime.datetime):
            date = date.date()  # Leave only year & month & day

        return MaccabiGamesStats([game for game in self.games if game.date.date() == date],
                                 self._new_description(f'Played at: {date}'))

    @property
    def first_game_date(self) -> str:
        return self[0].date.strftime('%d-%m-%Y')

    @property
    def last_game_date(self) -> str:
        return self[-1].date.strftime('%d-%m-%Y')

    # endregion

    # region free-style filters

    def get_games_by_competition(self, competition_types: Union[List[str], str]) -> MaccabiGamesStats:
        if isinstance(competition_types, str):
            competition_types = [competition_types]

        return MaccabiGamesStats([game for game in self.games if game.competition in competition_types],
                                 self._new_description(f'Competitions: {competition_types}'))

    def get_games_by_stadium(self, stadium_name: str) -> MaccabiGamesStats:
        return MaccabiGamesStats([game for game in self.games if stadium_name == game.stadium],
                                 self._new_description(f'Stadium: {stadium_name}'))

    def get_games_against_team(self, team_name: str) -> MaccabiGamesStats:
        # We count the team name as the name when they appear to the game or the name as they have these days
        current_team_name = self._team_names_convertor.find_team_current_name(team_name)

        return MaccabiGamesStats([game for game in self.games if
                                  current_team_name == game.not_maccabi_team.current_name],
                                 self._new_description(f'Against team: {team_name}'))

    def get_games_by_coach(self, coach_name: str) -> MaccabiGamesStats:
        return MaccabiGamesStats([game for game in self.games if coach_name == game.maccabi_team.coach],
                                 self._new_description(f'Coach: {coach_name}'))

    def get_games_by_referee(self, referee_name: str) -> MaccabiGamesStats:
        return MaccabiGamesStats([game for game in self.games if referee_name == game.referee],
                                 self._new_description(f'Referee: {referee_name}'))

    def get_games_by_player_name(self, player_name: str) -> MaccabiGamesStats:
        """
        Returns all the games that this player have any event in, played or at the bench.
        """
        return MaccabiGamesStats([game for game in self.games
                                  if player_name in [p.name.strip() for p in game.maccabi_team.players]],
                                 self._new_description(f'Player in squad: {player_name}'))

    def get_games_by_played_player_name(self, player_name: str) -> MaccabiGamesStats:
        """
        Returns all the games that the given players played at.
        """
        return MaccabiGamesStats([game for game in self.games
                                  if player_name in [p.name.strip() for p in game.maccabi_team.played_players]],
                                 self._new_description(f'Played player: {player_name}'))

    def get_games_by_season(self, season: str) -> MaccabiGamesStats:
        """
        Return Maccabi games stats object with season games, season may be entered as "1900/01".
        """
        return MaccabiGamesStats([game for game in self.games if game.season == season],
                                 self._new_description(f'Season {season}'))

    def get_games_by_day_at_month(self, day: int, month: int) -> MaccabiGamesStats:
        """
        Filter the maccabi games that played at the given day and month
        """
        return MaccabiGamesStats([game for game in self.games if
                                  game.date.day == day and game.date.month == month],
                                 self._new_description(f'Played at DD/MM: {day}/{month}'))

    # endregion

    def played_games_by_player_name(self) -> DefaultDict[str, MaccabiGamesStats]:
        """
        Returns a mapping between a player name to the games he participated
        """
        players_games = defaultdict(list)

        for game in self.games:
            for player in game.maccabi_team.played_players:
                players_games[player.name].append(game)

        games_by_player = {player_name: MaccabiGamesStats(players_games[player_name],
                                                          self._new_description(f'Player games: {player_name}'))
                           for player_name in players_games.keys()}

        # Allow to return an empty list for unknown players
        return defaultdict(lambda: MaccabiGamesStats([]), games_by_player)

    def played_games_by_player_and_team(self) -> Dict[str, DefaultDict[str, MaccabiGamesStats]]:
        """
        Returns a mapping between a player name to a dict from team to games, means:
        {'player_name1': {'team1': game1,
                          'team2': game2},
         'player_name2': {'team1': game1,
                          'team3': game3}
        }
        """
        players_to_teams_to_games_mapping = defaultdict(lambda: defaultdict(list))

        for game in self.games:
            for player in game.maccabi_team.played_players:
                # adds at [player][team].append(game)
                players_to_teams_to_games_mapping[player.name][game.not_maccabi_team.current_name].append(game)

        games_by_player_and_team = defaultdict(lambda: defaultdict(lambda: MaccabiGamesStats([])))
        for player_name, teams_mapping in players_to_teams_to_games_mapping.items():
            for team_name, specific_player_and_team_games in teams_mapping.items():
                current_combination_games = MaccabiGamesStats(specific_player_and_team_games,
                                                              f'Players {player_name} and Team: {team_name} games')
                games_by_player_and_team[player_name][team_name] = current_combination_games

        # Allow to return an empty list for unknown players, same default dict as above but with MaccabiGamesStats
        return defaultdict(lambda: defaultdict(lambda: MaccabiGamesStats([])), games_by_player_and_team)

    def create_maccabi_stats_from_games(self, games: List[GameData]) -> MaccabiGamesStats:
        return MaccabiGamesStats(games, description=self.description)

    @property
    def points(self):
        """
        Calculate points is supported only for league games
        """
        current_competitions = self.available_competitions

        if not set(current_competitions) <= set(LEAGUE_COMPETITIONS):
            raise TypeError(f'Calculating points is supported only for league games, '
                            f'current competitions: {current_competitions}')

        return calculate_points_for_games(self)

    @property
    def success_rate(self):
        """
        Calculate the success rate of the current games (points/possible points)
        """
        current_competitions = self.available_competitions

        if not set(current_competitions) <= set(LEAGUE_COMPETITIONS):
            raise TypeError(f'Calculating success rate supported only for league games, '
                            f'current competitions: {current_competitions}')

        return round(calculate_points_for_games(self) / calculate_possible_points_for_games(self), 3)

    def get_summary(self) -> Dict[str, Any]:
        summary = {'games': len(self),
                   "wins": self.results.wins_count,
                   "wins_by_percentage": self.results.wins_percentage,
                   "losses": self.results.losses_count,
                   "losses_by_percentage": self.results.losses_percentage,
                   "ties": self.results.ties_count,
                   "ties_by_percentage": self.results.ties_percentage,
                   "goals_for_maccabi": self.results.total_goals_for_maccabi,
                   "goals_for_maccabi_avg": self.averages.goals_for_maccabi,
                   "goals_against_maccabi": self.results.total_goals_against_maccabi,
                   "goals_against_maccabi_avg": self.averages.goals_against_maccabi,
                   "goals_diff_for_maccabi": self.results.total_goals_diff_for_maccabi,
                   "goals_diff_for_maccabi_avg": self.averages.maccabi_diff}

        return summary

    def show_summary(self) -> None:
        summary = ("Maccabi games stats object:"
                   "\n\nGames count: {games}"
                   "\nWins : {wins} ({wins_by_percentage}%)"
                   "\nLosses : {losses} ({losses_by_percentage}%)"
                   "\nTies : {ties} ({ties_by_percentage}%)"
                   "\n\nGoals for maccabi : {goals_for_maccabi}, {goals_for_maccabi_avg} per game"
                   "\nGoals against maccabi : {goals_against_maccabi}, {goals_against_maccabi_avg} per game"
                   "\nGoals diff for maccabi: {goals_diff_for_maccabi}, {goals_diff_for_maccabi} per game").format(
            **self.get_summary())

        print(summary)

    def create_team_summary(self, team_name: str) -> MaccabiGamesSummary:
        team_games_stats = self.get_games_against_team(team_name)
        return team_games_stats.summary

    def to_json(self) -> str:
        return json.dumps([game.to_json() for game in self.games], indent=4)

    def serialize_to_json(self) -> None:
        # TODO, there is too much escaped stuff in this function output
        with NamedTemporaryFile(delete=False, mode='w') as temp_json:
            logger.info(f"Serializing current maccabi games stats to temporary json file at: {temp_json.name}")
            temp_json.file.write(self.to_json())

    def __len__(self) -> int:
        return len(self.games)

    def __getitem__(self, item) -> GameData:
        return self.games[item]

    def __iter__(self):
        for game in self.games:
            yield game

    def __repr__(self) -> str:
        if not self.games:
            return f'{self.description} | {len(self.games)} games'

        return f'{self.description} | {len(self.games)} games | (from {self.first_game_date} to {self.last_game_date})'

    def _new_description(self, new_description) -> str:
        """
        Create new str of the current description with the given description.
        If the current description is the default one which means the "All games", we just return the new description.
        """
        if self.description == self._DEFAULT_DESCRIPTION:
            return new_description

        return f'{self.description} + {new_description}'

    @property
    def hebrew_representation(self) -> str:
        summary = f"{len(self)} משחקים"
        if len(self) > 0:
            summary += f" (החל מ {self.first_game_date} ועד {self.last_game_date})"

        return summary
