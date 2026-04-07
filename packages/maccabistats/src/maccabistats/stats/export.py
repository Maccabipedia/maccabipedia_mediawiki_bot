from __future__ import annotations

import csv
import itertools
import json
import logging
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Any, List, Optional

from maccabistats.models.game_data import GameData
from maccabistats.version import version

if TYPE_CHECKING:
    from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats

logger = logging.getLogger(__name__)

GameInformation = Dict[str, Any]
PlayersEventsInformation = List[Dict[str, Any]]

_BASE_EXPORT_FOLDER = Path.home() / 'maccabistats' / 'export'

_OPTIONAL_EVENT_PROPERTIES = ['player_goal_type', 'player_assist_type']


class ExportMaccabiGamesStats(object):
    """
    This class will serialize MaccabiGamesStats into readable/useful formats, like json, csv and so on.
    """

    def __init__(self, maccabi_games_stats: MaccabiGamesStats):
        self.maccabi_games_stats = maccabi_games_stats

    @staticmethod
    def _create_game_data_dict(game: GameData) -> GameInformation:
        return dict(stadium=game.stadium,
                    date=game.date.isoformat(),
                    crowd=game.crowd,
                    referee=game.referee,
                    competition=game.competition,
                    fixture=game.fixture,
                    season=game.season,
                    technical_result=game.technical_result,
                    home_team_name=game.home_team.name,
                    home_team_score=game.home_team.score,
                    home_team_coach=game.home_team.coach,
                    away_team_name=game.away_team.name,
                    away_team_score=game.away_team.score,
                    away_team_coach=game.away_team.coach)

    @staticmethod
    def _create_players_events_from_specific_game(game: GameData) -> PlayersEventsInformation:
        game_events = []
        game_data = ExportMaccabiGamesStats._create_game_data_dict(game)

        for current_event_data in game.events:
            # In order to prevent name collision and make te data more readable:
            event_data_with_player_prefix = {f'player_{key}': value for key, value in current_event_data.items()}

            hours, minutes, seconds = event_data_with_player_prefix['player_time_occur'].split(":")
            event_data_with_player_prefix['player_time_occur'] = (int(hours) * 60) + int(minutes)

            game_events.append({**game_data, **event_data_with_player_prefix})

        return game_events

    def _players_events_dict(self) -> List[PlayersEventsInformation]:
        logger.info('Starting to create a dict with all player events data')
        all_games = []

        for game in self.maccabi_games_stats:
            current_game_data = self._create_players_events_from_specific_game(game)

            if not current_game_data:
                logger.warning(f'Game: {game} is empty, could not serialize it, skipping it')
                continue

            all_games.append(current_game_data)

        logger.info('Finished to create a dict with all players events data')
        return all_games

    def _create_all_games_data(self) -> List[GameInformation]:
        logger.info('Starting to create a dict with all games data')
        all_games = []

        for game in self.maccabi_games_stats:
            current_game_data = self._create_game_data_dict(game)

            if not current_game_data:
                logger.warning(f'Game: {game} is empty, could not serialize it, skipping it')
                continue

            all_games.append(current_game_data)

        logger.info('Finished to create a dict with all games data')
        return all_games

    def export_players_events_json(self, folder_path: Optional[Path] = None) -> Path:
        now = _formatted_now()
        folder_path = folder_path or (_BASE_EXPORT_FOLDER / f'{now}_players_events')
        folder_path.mkdir(parents=True, exist_ok=True)

        file_path = self._create_players_events_json(folder_path)

        logger.info(f'Exported MaccabiGamesStats to players events json at: {file_path} successfully!')

        self._create_legend_for_maccabistats_data(folder_path)
        return file_path

    def export_games_data_json(self, folder_path: Optional[Path] = None) -> Path:
        now = _formatted_now()
        folder_path = folder_path or (_BASE_EXPORT_FOLDER / f'{now}_games_data')
        folder_path.mkdir(parents=True, exist_ok=True)

        file_path = self._create_games_data_json(folder_path)

        logger.info(f'Exported MaccabiGamesStats to games data json at: {file_path} successfully!')

        self._create_legend_for_maccabistats_data(folder_path)
        return file_path

    def export_players_events_csv(self, folder_path: Optional[Path] = None) -> Path:
        now = _formatted_now()
        folder_path = folder_path or (_BASE_EXPORT_FOLDER / f'{now}_players_events')
        folder_path.mkdir(parents=True, exist_ok=True)

        file_path = self._create_players_events_csv(folder_path)

        logger.info(f'Exported MaccabiGamesStats to players events csv at: {file_path} successfully!')

        self._create_legend_for_maccabistats_data(folder_path)
        return file_path

    def export_games_data_csv(self, folder_path: Optional[Path] = None) -> Path:
        now = _formatted_now()
        folder_path = folder_path or (_BASE_EXPORT_FOLDER / f'{now}_games_data')
        folder_path.mkdir(parents=True, exist_ok=True)

        file_path = self._create_games_data_csv(folder_path)

        logger.info(f'Exported MaccabiGamesStats to games data csv at: {file_path} successfully!')

        self._create_legend_for_maccabistats_data(folder_path)
        return file_path

    def export_everything_json(self, folder_path: Optional[Path] = None) -> Path:
        """
        Export all available data and zip it up
        """
        folder_path = (folder_path or _BASE_EXPORT_FOLDER)
        folder_path.mkdir(parents=True, exist_ok=True)

        file_path = folder_path / f'{_formatted_now()}_maccabistats.zip'

        with tempfile.TemporaryDirectory(prefix='MaccabiStatsExport') as temp_export_folder:
            self._create_games_data_json(folder_path=Path(temp_export_folder))
            self._create_players_events_json(folder_path=Path(temp_export_folder))

            self._create_legend_for_maccabistats_data(folder_path=Path(temp_export_folder))
            self._create_metadata_file(folder_path=Path(temp_export_folder))

            shutil.make_archive(file_path.with_suffix(""), 'zip', temp_export_folder)

        logger.info(f'Exported MaccabiGamesStats to zip at: {file_path} successfully!')

        return file_path

    def export_everything_csv(self, folder_path: Optional[Path] = None) -> Path:
        """
        Export all available data and zip it up
        """
        folder_path = (folder_path or _BASE_EXPORT_FOLDER)
        folder_path.mkdir(parents=True, exist_ok=True)

        file_path = folder_path / f'{_formatted_now()}_maccabistats.zip'

        with tempfile.TemporaryDirectory(prefix='MaccabiStatsExport') as temp_export_folder:
            self._create_games_data_csv(folder_path=Path(temp_export_folder))
            self._create_players_events_csv(folder_path=Path(temp_export_folder))

            self._create_legend_for_maccabistats_data(folder_path=Path(temp_export_folder))
            self._create_metadata_file(folder_path=Path(temp_export_folder))

            shutil.make_archive(file_path.with_suffix(""), 'zip', temp_export_folder)

        logger.info(f'Exported MaccabiGamesStats to zip at: {file_path} successfully!')

        return file_path

    def _create_players_events_csv(self, folder_path: Path) -> Path:
        file_path = folder_path / 'players_events_maccabistats.csv'

        games_data = itertools.chain.from_iterable(self._players_events_dict())
        first_player_event = next(games_data)

        with file_path.open(mode='w', encoding='utf8', newline='') as csv_file:
            writer = csv.DictWriter(csv_file,
                                    delimiter=',',
                                    fieldnames=list(first_player_event.keys()) + _OPTIONAL_EVENT_PROPERTIES)
            writer.writeheader()

            writer.writerow(first_player_event)  # Because we popped it out to set the header
            writer.writerows(games_data)

        return file_path

    def _create_players_events_json(self, folder_path: Path) -> Path:
        file_path = folder_path / 'players_events_maccabistats.json'

        players_events = itertools.chain.from_iterable(self._players_events_dict())

        jsoned_data = json.dumps(list(players_events), indent=4, ensure_ascii=False)
        file_path.write_text(jsoned_data, encoding='utf8')

        return file_path

    def _create_games_data_csv(self, folder_path: Path) -> Path:
        file_path = folder_path / 'games_data_maccabistats.csv'

        games_data = self._create_all_games_data()
        first_game_data = games_data[0]

        with file_path.open(mode='w', encoding='utf8', newline='') as csv_file:
            writer = csv.DictWriter(csv_file,
                                    delimiter=',',
                                    fieldnames=list(first_game_data.keys()))
            writer.writeheader()

            writer.writerow(first_game_data)  # Because we popped it out to set the header
            writer.writerows(games_data)

        return file_path

    def _create_games_data_json(self, folder_path: Path) -> Path:
        file_path = folder_path / 'games_data_maccabistats.json'

        games_data = self._create_all_games_data()

        jsoned_data = json.dumps(list(games_data), indent=4, ensure_ascii=False)
        file_path.write_text(jsoned_data, encoding='utf8')

        return file_path

    @staticmethod
    def _create_legend_for_maccabistats_data(folder_path: Path) -> Path:
        """
        Create a file that will show the different options for the data we have, such as:
        * Player Events
        * What 'technical_result' means?
        """
        prepared_readme_file = Path(__file__).absolute().parent / 'maccabistats_export_readme.md'
        file_path = folder_path / prepared_readme_file.name

        shutil.copy(prepared_readme_file, file_path)

        return folder_path

    def _create_metadata_file(self, folder_path: Path) -> Path:
        """
        Creates a txt file with general information such as:
        * Maccabistats version
        * MaccabiGamesStats object description - which games are filtered in?
        """
        file_path = folder_path / 'maccabistats_metadata.txt'

        file_path.write_text(f'*** MaccabiStats Metadata ***\n\n'
                             f'* MaccabiStats version: {version}\n'
                             f'* MaccabiStats description (which games are available in this export?):'
                             f' {self.maccabi_games_stats.description}')

        return file_path


def _formatted_now() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
