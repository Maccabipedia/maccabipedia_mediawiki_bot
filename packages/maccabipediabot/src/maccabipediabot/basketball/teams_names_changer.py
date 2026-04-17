"""Back-compat shim. Use `maccabipediabot.basketball.translations` directly."""
from maccabipediabot.basketball.translations import (
    _TEAM_RENAMES,
    canonical_team_name as _canonical,
)


class _Compat:
    """Mimics the legacy TeamNameChanger.change_name(game) API."""

    def __init__(self, old_name: str) -> None:
        self.old_name = old_name

    def change_name(self, game) -> str:
        return _canonical(self.old_name, game.game_date)


teams_names_changer = {old_name: _Compat(old_name) for old_name in _TEAM_RENAMES}
