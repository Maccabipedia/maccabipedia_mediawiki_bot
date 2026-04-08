import glob
import logging
import os
import pickle
from datetime import datetime
from pathlib import Path

from maccabistats.parse.general_fixes import run_general_fixes
from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats

logger = logging.getLogger(__name__)

home_folder = Path.home().as_posix()
serialized_sources_path_pattern = os.path.join(home_folder, "maccabistats", "sources", "{source_name}",
                                               "{source_name}-{version}-{date}.games")

"""
This class is responsible to set the api for each maccabistats source, the common usage should be :

m = MaccabiStatsSource()
m.parse_maccabi_games()
m.run_general_fixes()
m.run_specific_fixes()

games = m.maccabi_games_stats
"""


class MaccabiStatsSource(object):
    def __init__(self, name):
        self.name = name
        self.maccabi_games_stats = None

    @property
    def _serialized_games_path(self):
        return serialized_sources_path_pattern.format(source_name=self.name, version=self.maccabi_games_stats.version,
                                                      date=datetime.now().strftime("%Y-%m-%d %H-%M-%S"))

    @property
    def _serialized_games_path_pattern(self):
        return serialized_sources_path_pattern.format(source_name=self.name, version="*", date="*")

    def parse_maccabi_games(self):
        """
        Parse the raw data and saves it on self.maccabi_games_stats., this method is not responsible to serialize the games to the disk.
        """

        logger.info(f"Starting to parse maccabi games from: {self.name}")
        parsed_games = self._rerun_source()
        self.maccabi_games_stats = MaccabiGamesStats(parsed_games, f'Source: {self.name}')

    def _rerun_source(self):
        """
        Parse the raw data and saves it on self.maccabi_games_stats
        :return:
        """

        raise NotImplementedError()

    def run_specific_fixes(self):
        """
        Run any specific fixes for this source (such as error within the raw data).
        """

        raise NotImplementedError()

    def run_general_fixes(self):
        """
        Runs any general fixes that relevant for all sources (such as naming and so on).
        """

        if self.maccabi_games_stats is None:
            raise RuntimeError("You should run parse_maccabi_games first.")

        self.maccabi_games_stats = run_general_fixes(self.maccabi_games_stats)

    def load_serialized_games(self):
        """
        Load the serialized games to self.maccabi_games_stats
        :return: MaccabiGamesStats
        """
        last_created_source_games_file = self.find_last_created_source_maccabi_games_file()

        logger.info(f"Loading source {self.name} as MaccabiGamesStats from: {last_created_source_games_file},"
                    f" This is the last created serialized maccabi games file on this source folder")
        with open(last_created_source_games_file, 'rb') as f:
            self.maccabi_games_stats = pickle.load(f)

    def find_last_created_source_maccabi_games_file(self) -> str:
        serialized_source_games = glob.glob(self._serialized_games_path_pattern)
        if not serialized_source_games:
            raise RuntimeError(f"Cant find source serialized games at: {self._serialized_games_path_pattern}")

        last_created_serialized_maccabi_games_file = max(serialized_source_games, key=os.path.getctime)
        return last_created_serialized_maccabi_games_file

    def serialize_games(self):
        """
        Serialize the parsed games (without any fixes).
        """

        source_games_file_path = self._serialized_games_path
        Path(source_games_file_path).parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Serializing source ({self.name} MaccabiGamesStats to: {source_games_file_path})")
        if os.path.isfile(source_games_file_path):
            # todo: bkup the old file
            # old_file_path = Path(self._serialized_games_path)
            # old_file_path.stem+= int(time())
            pass

        with open(source_games_file_path, 'wb') as f:
            pickle.dump(self.maccabi_games_stats, f)
