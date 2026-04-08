# -*- coding: utf-8 -*-
import logging
import os

from maccabistats.config import MaccabiStatsConfigSingleton
from maccabistats.parse.general_fixes import run_general_fixes
from maccabistats.parse.maccabi_tlv_site.maccabi_tlv_site_source import MaccabiTlvSiteSource
from maccabistats.parse.maccabipedia.maccabipedia_source import MaccabiPediaSource
from maccabistats.parse.maccabipedia.maccabipedia_single_file_source import MaccabiPediaSingleFileSource
from maccabistats.parse.merge_sources import merge_maccabitlv_and_table
from maccabistats.parse.table.table_source import TableSource
from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats

logger = logging.getLogger(__name__)


def __validate_folders_to_save_maccabi_games_exists():
    """
    Makes sure that the folders (from settings) that given to save the game & season exists
    """

    folder_to_save_seasons = MaccabiStatsConfigSingleton.maccabi_site.folder_to_save_seasons_html_files
    folder_to_save_games = MaccabiStatsConfigSingleton.maccabi_site.folder_to_save_games_html_files

    if not os.path.exists(folder_to_save_seasons):
        logger.info("The folder from settings to save the seasons in does not exists, creating : {path}".format(
            path=folder_to_save_seasons))
        os.makedirs(folder_to_save_seasons)

    if not os.path.exists(folder_to_save_games):
        logger.info("The folder from settings to save the games in does not exists, creating : {path}".format(
            path=folder_to_save_games))
        os.makedirs(folder_to_save_games)


def _run_source(source):
    """
    Run the given maccabi games stats source, serialized the output to the disk and returns the MaccabiGamesStats final object (after fixes).

    :param source: source instance to run
    :type source: maccabistats.parse.maccabistats_source.MaccabiStatsSource
    """

    logger.info(f"Running source: {source.name}")
    logger.info("Validating setup for source crawling is ready.")
    __validate_folders_to_save_maccabi_games_exists()

    logger.info("Parsing the source: {name}".format(name=source.name))
    source.parse_maccabi_games()
    source.run_general_fixes()
    source.run_specific_fixes()

    logger.info("Loading the source: {name}".format(name=source.name))
    source.serialize_games()

    return _load_from_source(source)  # Include general fixes


def run_maccabitlv_site_source():
    """
    Runs the MaccabiTlv-Site source and serialize its output.

    :rtype: maccabistats.stats.maccabi_games_stats.MaccabiGamesStats
    """

    return _run_source(MaccabiTlvSiteSource())


def run_table_source():
    """
    Runs the Table source and serialize its output.

    :rtype: maccabistats.stats.maccabi_games_stats.MaccabiGamesStats
    """

    return _run_source(TableSource())


def run_maccabipedia_source():
    """
    Runs the MaccabiPedia source and serialize its output.

    :rtype: maccabistats.stats.maccabi_games_stats.MaccabiGamesStats
    """

    return _run_source(MaccabiPediaSource())


def merge_maccabi_games_from_all_input_serialized_sources():
    """
    Assumes all the sources serialized their data (by calling "run_all_sources" or have somehow the serialized data).
    Iterate all the sources and merge the maccabi games stats (after running general&specific fixes) to one list of maccabi games.

    ATM the input sources are MaccabiTlv-Site and Table (MaccabiPedia does not count as input source [MaccabiPedia is the result]).

    :rtype: maccabistats.stats.maccabi_games_stats.MaccabiGamesStats
    """

    logger.info("Validating setup for crawling is ready.")

    maccabi_games_stats_from_all_sources = []
    maccabistats_sources = [MaccabiTlvSiteSource(), TableSource()]
    for source in maccabistats_sources:
        logger.info("Loading the source: {name}".format(name=source.name))
        source.load_serialized_games()
        source.run_general_fixes()
        source.run_specific_fixes()

        maccabi_games_stats_from_all_sources.append(source.maccabi_games_stats)

    # todo: write merge logic

    logger.info("Merging all the sources to one maccabi games stats")
    merged_maccabistats_games = merge_maccabitlv_and_table(maccabi_games_stats_from_all_sources[0],
                                                           maccabi_games_stats_from_all_sources[1])
    logger.info("Running general fixes on merged maccabi games stats object")

    maccabistats_games = run_general_fixes(MaccabiGamesStats(merged_maccabistats_games))
    return maccabistats_games


def _load_from_source(source):
    logger.info(f"Loading games from source: {source.name}")
    source.load_serialized_games()
    source.run_general_fixes()
    source.run_specific_fixes()

    return MaccabiGamesStats(source.maccabi_games_stats, description=f'Source: {source.name}')


def load_from_maccabipedia_source():
    return _load_from_source(MaccabiPediaSource())


def load_from_maccabipedia_file_source(maccabi_games_file: str):
    return _load_from_source(MaccabiPediaSingleFileSource(maccabi_games_file))


def load_from_table_source():
    return _load_from_source(TableSource())


def load_from_maccabisite_source():
    return _load_from_source(MaccabiTlvSiteSource())
