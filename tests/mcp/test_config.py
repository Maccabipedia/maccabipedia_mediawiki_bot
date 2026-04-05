import os
from maccabipedia_mcp.config import Config


def test_config_from_env_defaults(monkeypatch):
    monkeypatch.delenv("MACCABIPEDIA_URL", raising=False)
    monkeypatch.delenv("MACCABIPEDIA_BOT_USERNAME", raising=False)
    monkeypatch.delenv("MACCABIPEDIA_BOT_PASSWORD", raising=False)
    cfg = Config.from_env()
    assert cfg.url == "https://www.maccabipedia.co.il"
    assert cfg.api_url == "https://www.maccabipedia.co.il/api.php"
    assert cfg.username is None
    assert cfg.password is None


def test_config_from_env_custom(monkeypatch):
    monkeypatch.setenv("MACCABIPEDIA_URL", "https://test.wiki.co.il")
    monkeypatch.setenv("MACCABIPEDIA_BOT_USERNAME", "bot_user")
    monkeypatch.setenv("MACCABIPEDIA_BOT_PASSWORD", "bot_pass")
    cfg = Config.from_env()
    assert cfg.url == "https://test.wiki.co.il"
    assert cfg.api_url == "https://test.wiki.co.il/api.php"
    assert cfg.username == "bot_user"
    assert cfg.password == "bot_pass"
