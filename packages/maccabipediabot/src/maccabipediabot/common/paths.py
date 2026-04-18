import os
from pathlib import Path


def _path_from_env(var_name: str) -> Path:
    value = os.environ.get(var_name)
    if value is None:
        raise RuntimeError(f"Environment variable {var_name} is not set")
    return Path(value)


def basketball_games_file() -> Path:
    return _path_from_env('MACCABIPEDIA_BASKETBALL_GAMES_FILE')


def volleyball_root() -> Path:
    return _path_from_env('MACCABIPEDIA_VOLLEYBALL_ROOT')


def videos_dir() -> Path:
    return _path_from_env('MACCABIPEDIA_VIDEOS_DIR')


def papers_root() -> Path:
    return _path_from_env('MACCABIPEDIA_PAPERS_ROOT')


def basketball_tickets_root() -> Path:
    return _path_from_env('MACCABIPEDIA_BASKETBALL_TICKETS_ROOT')
