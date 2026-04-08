import logging

from maccabistats.parse.maccabipedia.maccabipedia_source import MaccabiPediaSource

logger = logging.getLogger(__name__)


class MaccabiPediaSingleFileSource(MaccabiPediaSource):

    def __init__(self, file_to_use: str) -> None:
        super().__init__()
        self.file_to_use = file_to_use

    def find_last_created_source_maccabi_games_file(self) -> str:
        return self.file_to_use
