from __future__ import annotations

import logging
from collections import defaultdict
from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats

logger = logging.getLogger(__name__)

TeamStats = Tuple[str, float]


class TeamNamesConvertor:
    """
    This class will convert any team name (current or historic) to the current team name.
    This will allow us to search all the team games even if this team has several names (so we can group them all)
    """

    def __init__(self, maccabi_games_stats: MaccabiGamesStats):
        self.maccabi_games_stats = maccabi_games_stats
        self.historical_name_to_current_name = {game.not_maccabi_team.name: game.not_maccabi_team.current_name for game
                                                in maccabi_games_stats}

    def validate_uniqueness(self) -> None:
        """
        Validates that an historical name won't lead to two current names
        """
        historical_to_current_names = defaultdict(set)

        for game in self.maccabi_games_stats:
            historical_to_current_names[game.not_maccabi_team.name].add(game.not_maccabi_team.current_name)

        too_many_names = False
        for team_name, current_names in historical_to_current_names.items():
            if len(current_names) > 1:
                logger.warning(
                    f'Found {len(current_names)} names, which is more than 1 current team name for team: {team_name}')
                too_many_names = True

        if not too_many_names:
            return

        raise RuntimeError('Found too many names for several teams')

    def find_team_current_name(self, team_name: str) -> str:
        return self.historical_name_to_current_name[team_name]
