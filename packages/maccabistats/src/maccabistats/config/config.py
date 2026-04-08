from dataclasses import dataclass

from .maccabipedia_config import MaccabiPediaConfig
from .maccabisite_config import MaccabiSiteConfig


@dataclass
class MaccabiStatsConfig:
    maccabipedia = MaccabiPediaConfig()
    maccabi_site = MaccabiSiteConfig()


MaccabiStatsConfigSingleton = MaccabiStatsConfig()
