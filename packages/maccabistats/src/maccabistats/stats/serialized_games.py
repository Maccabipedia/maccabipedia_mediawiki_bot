import datetime
import glob
import logging
import os
import pickle
from pathlib import Path
from typing import Optional

from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats

logger = logging.getLogger(__name__)

_maccabistats_root_folder_path = Path.home().as_posix()
_serialized_maccabi_games_folder_path = os.path.join(_maccabistats_root_folder_path, "maccabistats")
_serialized_maccabi_games_file_name_pattern = "maccabi-{version}-{date}.games"
_serialized_maccabi_games_file_path_pattern = os.path.join(_serialized_maccabi_games_folder_path,
                                                           _serialized_maccabi_games_file_name_pattern)


def get_maccabi_stats_as_newest_wrapper(file_name: Optional[str] = None) -> MaccabiGamesStats:
    """"
    Returns the serialized file_name cast to the latest MaccabiGamesStats object, which means that newer functions can be used.
    """

    return MaccabiGamesStats(get_maccabi_stats(file_name).games)


def get_maccabi_stats(file_name: Optional[str] = None) -> MaccabiGamesStats:
    """
    :param file_name: pickled maccabi games (probably MaccabiGamesStats object).
                      When no file is given, Try to load the latest maccabi*.games from the default folder.
    """

    if file_name is None:
        maccabi_games_files_in_default_folder = glob.glob(
            _serialized_maccabi_games_file_path_pattern.format(version="*", date="*"))
        if not maccabi_games_files_in_default_folder:
            raise RuntimeError(
                f"No file name was given -> Failed to get the latest maccabi*.games from default folder: {_serialized_maccabi_games_folder_path}")
        file_name = max(maccabi_games_files_in_default_folder, key=os.path.getctime)

    else:
        if not os.path.isfile(file_name):
            raise RuntimeError(
                "You should have maccabi.games serialized object, you can use maccabistats.serialize_maccabi_games() to do that.")

    with open(file_name, 'rb') as f:
        logger.info(f"Loading maccabi games from {file_name}")
        return pickle.load(f)


def serialize_maccabi_games(maccabi_games_stats: MaccabiGamesStats,
                            folder_path: str = _serialized_maccabi_games_folder_path) -> None:
    """
    Re-serialize maccabi games stats, after doing manually manipulation (run_manual_fixes) or anything else.
    :param folder_path: Folder path to pickle maccabi game at
    """

    if not isinstance(maccabi_games_stats, MaccabiGamesStats):
        raise RuntimeError("You Should serialize only maccabi games stats object")

    file_name = os.path.join(folder_path, _serialized_maccabi_games_file_name_pattern).format(
        version=maccabi_games_stats.version,
        date=str(datetime.date.today()))
    with open(file_name, 'wb') as f:
        pickle.dump(maccabi_games_stats, f)

    logger.info(f"Serialized maccabi games to {file_name}")
