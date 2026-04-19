# maccabipediabot is installed as a uv workspace member (uv sync)
# No sys.path manipulation needed.
from unittest.mock import MagicMock

# Modules like football/gamesbot.py call get_site() at module scope; stub it so
# test collection doesn't require real wiki credentials.
from maccabipediabot.common import wiki_login

wiki_login.get_site = lambda: MagicMock(name="stub-site")

# maintenance/football/league_tables_files_to_game_pages.py calls
# load_from_maccabipedia_source() at module scope, which expects a serialized
# games file on disk that doesn't exist in CI. Stub it.
import maccabistats  # noqa: E402

maccabistats.load_from_maccabipedia_source = lambda: MagicMock(name="stub-games")
