import logging
from maccabistats.parse.table.fix_specific_games import fix_specific_games
from maccabistats.parse.maccabistats_source import MaccabiStatsSource
from maccabistats.parse.table.main_parser import get_parsed_maccabi_games_from_json
from maccabistats.parse.sources import SourcesNames

logger = logging.getLogger(__name__)

"""
Table is external source which saves maccabi games as json
"""


class TableSource(MaccabiStatsSource):

    def __init__(self):
        super().__init__(name=SourcesNames.Table.value)

    def _rerun_source(self):
        """
        Parse the raw data and saves it on self.maccabi_games_stats
        """

        return get_parsed_maccabi_games_from_json()

    def run_specific_fixes(self):
        """
        Run any specific fixes for this source (such as error within the raw data).
        """

        if self.maccabi_games_stats is None:
            raise RuntimeError("You should run parse_maccabi_games first")

        logger.info("Running fix specific games for maccabi-tlv site source")
        self.maccabi_games_stats = fix_specific_games(self.maccabi_games_stats)
