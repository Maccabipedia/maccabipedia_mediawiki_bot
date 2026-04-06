import pytest
import responses

from maccabipedia_mcp.config import Config
from maccabipedia_mcp.wiki_client import WikiClient

WIKI_URL = "https://test.wiki.co.il"
API_URL = f"{WIKI_URL}/api.php"


@pytest.fixture
def config():
    return Config(url=WIKI_URL, username=None, password=None)


@pytest.fixture
def client(config):
    return WikiClient(config)
