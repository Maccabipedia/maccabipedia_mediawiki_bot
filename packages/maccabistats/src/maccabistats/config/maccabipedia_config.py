from dataclasses import dataclass


@dataclass
class _MaccabiPediaQueryGamesDataConfig:
    tables_names = 'Football_Games, Competitions, Stadiums, Opponents'
    fields_names = 'Football_Games._pageName, Football_Games.Date, Football_Games.Hour, Football_Games.MatchDay, Football_Games.Season, Football_Games.Competition, Football_Games.Leg, Opponents.OriginalName=Opponent, Football_Games.HomeAway, Stadiums.OriginalName=Stadium, Football_Games.ResultMaccabi, Football_Games.ResultOpponent, Football_Games.CoachMaccabi, Football_Games.CoachOpponent, Football_Games.Refs, Football_Games.Crowd, Football_Games.Technical'
    join_on = 'Football_Games.Competition=Competitions.OriginalName, Football_Games.Stadium=Stadiums.CanonicalName, Football_Games.Opponent=Opponents.CanonicalName'


@dataclass
class _MaccabiPediaQueryGamesEventsConfig:
    tables_names = 'Games_Events'
    fields_names = '_pageName, Date, PlayerName, PlayerNumber, Minute, EventType, SubType, Team, Part'


@dataclass
class MaccabiPediaConfig:
    base_crawling_address = 'http://www.maccabipedia.co.il/index.php?title=Special:CargoExport&format=json'

    games_data_query = _MaccabiPediaQueryGamesDataConfig()
    games_events_query = _MaccabiPediaQueryGamesEventsConfig()
