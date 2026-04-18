from pathlib import Path

from maccabipediabot.common import paths


def test_basketball_games_file_uses_env_var(monkeypatch):
    monkeypatch.setenv('MACCABIPEDIA_BASKETBALL_GAMES_FILE', '/tmp/custom.json')
    assert paths.basketball_games_file() == Path('/tmp/custom.json')


def test_basketball_games_file_falls_back_to_default(monkeypatch):
    monkeypatch.delenv('MACCABIPEDIA_BASKETBALL_GAMES_FILE', raising=False)
    result = paths.basketball_games_file()
    assert isinstance(result, Path)
    assert 'basketball' in str(result).lower()


def test_all_accessors_return_path(monkeypatch):
    for env_var in (
        'MACCABIPEDIA_BASKETBALL_GAMES_FILE',
        'MACCABIPEDIA_VOLLEYBALL_ROOT',
        'MACCABIPEDIA_VIDEOS_DIR',
        'MACCABIPEDIA_PAPERS_ROOT',
        'MACCABIPEDIA_BASKETBALL_TICKETS_ROOT',
    ):
        monkeypatch.delenv(env_var, raising=False)
    assert isinstance(paths.basketball_games_file(), Path)
    assert isinstance(paths.volleyball_root(), Path)
    assert isinstance(paths.videos_dir(), Path)
    assert isinstance(paths.papers_root(), Path)
    assert isinstance(paths.basketball_tickets_root(), Path)
