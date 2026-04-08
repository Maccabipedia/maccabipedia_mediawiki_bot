import os
from dataclasses import dataclass, field
from pathlib import Path

MACCABISTATS_DATA_DIR = Path(os.environ.get("MACCABISTATS_DATA_DIR", Path.home() / "maccabistats"))


@dataclass
class MaccabiSiteConfig:
    max_seasons_to_crawl: int = 87
    season_page_pattern: str = 'https://www.maccabi-tlv.co.il/משחקים-ותוצאות/הקבוצה-הבוגרת/תוצאות/?season={season_number}#content'
    folder_to_save_seasons_html_files: str = field(default_factory=lambda: str(MACCABISTATS_DATA_DIR / "crawl" / "seasons"))
    folder_to_save_games_html_files: str = field(default_factory=lambda: str(MACCABISTATS_DATA_DIR / "crawl" / "games"))
    use_disk_as_cache_when_crawling = True
    use_lxml_parser = True
    use_multiprocess_crawling = True
    crawling_process_number = 15
