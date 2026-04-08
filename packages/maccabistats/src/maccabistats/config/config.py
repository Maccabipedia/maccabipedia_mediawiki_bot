from dataclasses import dataclass

from .maccabipedia_config import MaccabiPediaConfig
from .maccabisite_config import MaccabiSiteConfig

# Re-export for convenience
from .maccabisite_config import MACCABISTATS_DATA_DIR  # noqa: F401


@dataclass
class MaccabiStatsConfig:
    maccabipedia = MaccabiPediaConfig()
    maccabi_site = MaccabiSiteConfig()


MaccabiStatsConfigSingleton = MaccabiStatsConfig()
