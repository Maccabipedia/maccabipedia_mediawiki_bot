import logging

from maccabistats.parse.maccabipedia.maccabipedia_parser import MaccabiPediaParser
from maccabistats.parse.maccabistats_source import MaccabiStatsSource
from maccabistats.parse.sources import SourcesNames

logger = logging.getLogger(__name__)

"""
Implement MaccabiStatsSource that crawl maccabipedia.
"""


class MaccabiPediaSource(MaccabiStatsSource):

    def __init__(self):
        super().__init__(name=SourcesNames.MaccabiPedia.value)

    def _rerun_source(self):
        """
        Parse the raw data and saves it on self.maccabi_games_stats
        """

        maccabipedia_parser = MaccabiPediaParser()
        return maccabipedia_parser.parse()

    def run_specific_fixes(self):
        """
        Run any specific fixes for this source (such as error within the raw data).
        """

        pass
