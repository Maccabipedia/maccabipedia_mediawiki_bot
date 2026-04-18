import os
from pathlib import Path

_DEFAULTS = {
    'MACCABIPEDIA_BASKETBALL_GAMES_FILE': r'C:\maccabi\basketball\games_for_upload.json',
    'MACCABIPEDIA_VOLLEYBALL_ROOT': r'D:\maccabipedia_google_drive\מכביפדיה_ראשי\כדורעף\משחקים מהעיתונות',
    'MACCABIPEDIA_VIDEOS_DIR': r'C:\maccabipedia\videos',
    'MACCABIPEDIA_PAPERS_ROOT': r'C:\code\maccabipedia_mediawikibot\games_papers_to_upload\from_drive',
    'MACCABIPEDIA_BASKETBALL_TICKETS_ROOT': r'C:\maccabipedia\automations\basketball_tickets-03-2026',
}


def _path_from_env(var_name: str) -> Path:
    return Path(os.environ.get(var_name, _DEFAULTS[var_name]))


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
