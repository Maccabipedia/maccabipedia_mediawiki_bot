from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats

logger = logging.getLogger(__name__)


class MaccabiGamesPlayersEventsSummaryStats(object):
    """
    This class will handle all players events statistics.
    """

    def __init__(self, maccabi_games_stats: MaccabiGamesStats):
        self.maccabi_games_stats = maccabi_games_stats

    # region assists
    @property
    def total_goals_assists_counted_for_maccabi_players(self) -> int:
        return sum(player[1] for player in self.maccabi_games_stats.players.best_assisters)

    @property
    def total_goals_assists_by_penalty_winning_for_maccabi_players(self) -> int:
        return sum(player[1] for player in self.maccabi_games_stats.players.best_assisters_by_penalty_winning)

    @property
    def total_goals_assists_by_corner_for_maccabi_players(self) -> int:
        return sum(player[1] for player in self.maccabi_games_stats.players.best_assisters_by_corner)

    @property
    def total_goals_assists_by_free_kick_for_maccabi_players(self) -> int:
        return sum(player[1] for player in self.maccabi_games_stats.players.best_assisters_by_free_kick)

    @property
    def total_goals_assists_by_throw_in_for_maccabi_players(self) -> int:
        return sum(player[1] for player in self.maccabi_games_stats.players.best_assisters_by_throw_in)

    # endregion

    # region goals
    @property
    def total_goals_scoring_counted_for_maccabi_players(self) -> int:
        return sum(player[1] for player in self.maccabi_games_stats.players.best_scorers)

    @property
    def total_penalties_goals_scoring_counted_for_maccabi_players(self) -> int:
        return sum(player[1] for player in self.maccabi_games_stats.players.best_scorers_by_penalty)

    @property
    def total_freekicks_goals_scoring_counted_for_maccabi_players(self) -> int:
        return sum(player[1] for player in self.maccabi_games_stats.players.best_scorers_by_freekick)

    @property
    def total_own_goals_scoring_counted_for_maccabi_players(self) -> int:
        return sum(player[1] for player in self.maccabi_games_stats.players.best_scorers_by_own_goal)

    @property
    def total_head_goals_scoring_counted_for_maccabi_players(self) -> int:
        return sum(player[1] for player in self.maccabi_games_stats.players.best_scorers_by_head)

    @property
    def total_foot_goals_scoring_counted_for_maccabi_players(self) -> int:
        return sum(player[1] for player in self.maccabi_games_stats.players.best_scorers_by_foot)

    # endregion
    @property
    def total_goals_involved_counted_for_maccabi_players(self) -> int:
        return sum(player[1] for player in self.maccabi_games_stats.players.most_goals_involved)

    @property
    def total_yellow_card_counted_for_maccabi_players(self) -> int:
        return sum(player[1] for player in self.maccabi_games_stats.players.most_yellow_carded)

    @property
    def total_red_card_counted_for_maccabi_players(self) -> int:
        return sum(player[1] for player in self.maccabi_games_stats.players.most_red_carded)

    @property
    def total_captains_counted_for_maccabi_players(self) -> int:
        return sum(player[1] for player in self.maccabi_games_stats.players.most_captains)

    @property
    def total_lineups_counted_for_maccabi_players(self) -> int:
        return sum(player[1] for player in self.maccabi_games_stats.players.most_lineup_players)

    @property
    def _players_with_numbers_for_maccabi(self) -> Tuple[int, int]:
        """
        Checks how many players (PlayerInGame) are registered with a player number.
        In old games we may could not find any evidence for the number of the player shirt.

        "A player" - means a player in a game, because we based on PlayerInGame class.

        :return: Count of players with shirt number, Count of players without shirt number
        """
        players_with_shirt_number = 0
        players_without_shirt_number = 0

        for game in self.maccabi_games_stats:
            current_game_players_with_number = sum(1 for p in game.maccabi_team.players if not p.number)

            players_without_shirt_number += current_game_players_with_number
            players_with_shirt_number += len(game.maccabi_team.players) - current_game_players_with_number

        return players_with_shirt_number, players_without_shirt_number

    @property
    def total_players_with_shirt_number_for_maccabi(self) -> int:
        return self._players_with_numbers_for_maccabi[0]

    def compare_to_other_maccabi_games_stats(self, other) -> None:
        """
        Prints the comparison of the current (self) maccabi games stats to the given object.
        All of the shown numbers will be relevant to the other.
        If we will show for example "+2", means that self has two more items in the given field than "other".
        :type other: maccabistats.stats.maccabi_games_stats.MaccabiGamesStats
        :rtype: str
        """

        def compared_field(field_name):
            return getattr(self, field_name) - getattr(other.players_events_summary, field_name)

        comparison = f"Comparing self <---> other events summary for maccabi players:\n\n" \
                     f"   Games Count: {len(self.maccabi_games_stats) - len(other)}\n" \
                     f"   Goals: {compared_field('total_goals_scoring_counted_for_maccabi_players')}\n" \
                     f"         By foot: {compared_field('total_foot_goals_scoring_counted_for_maccabi_players')}\n" \
                     f"         By head: {compared_field('total_head_goals_scoring_counted_for_maccabi_players')}\n" \
                     f"         By freekick: {compared_field('total_freekicks_goals_scoring_counted_for_maccabi_players')}\n" \
                     f"         By penalty: {compared_field('total_penalties_goals_scoring_counted_for_maccabi_players')}\n" \
                     f"         Own: {compared_field('total_own_goals_scoring_counted_for_maccabi_players')}\n" \
                     f"   Assists: {compared_field('total_goals_assists_counted_for_maccabi_players')}\n" \
                     f"         By penalty winning: {compared_field('total_goals_assists_by_penalty_winning_for_maccabi_players')}\n" \
                     f"         By corner: {compared_field('total_goals_assists_by_corner_for_maccabi_players')}\n" \
                     f"         By freekick: {compared_field('total_goals_assists_by_free_kick_for_maccabi_players')}\n" \
                     f"         By throw-in: {compared_field('total_goals_assists_by_throw_in_for_maccabi_players')}\n" \
                     f"   Goals involved: {compared_field('total_goals_involved_counted_for_maccabi_players')}\n" \
                     f"   Cards:\n" \
                     f"         Yellow cards: {compared_field('total_yellow_card_counted_for_maccabi_players')}\n" \
                     f"         Red cards: {compared_field('total_red_card_counted_for_maccabi_players')}\n" \
                     f"   Captains: {compared_field('total_captains_counted_for_maccabi_players')}\n" \
                     f"   Lineups: {compared_field('total_lineups_counted_for_maccabi_players')}\n" \
                     f"   Players shirt number: {compared_field('total_players_with_shirt_number_for_maccabi')}\n"

        print(comparison)

    def __str__(self) -> str:
        return f"Total event counting for maccabi players:\n\n" \
               f"   Games Count: {len(self.maccabi_games_stats)}\n" \
               f"   Goals: {self.total_goals_scoring_counted_for_maccabi_players}\n" \
               f"           By foot: {self.total_foot_goals_scoring_counted_for_maccabi_players}\n" \
               f"           By head: {self.total_head_goals_scoring_counted_for_maccabi_players}\n" \
               f"           By freekick: {self.total_freekicks_goals_scoring_counted_for_maccabi_players}\n" \
               f"           By penalty: {self.total_penalties_goals_scoring_counted_for_maccabi_players}\n" \
               f"           Own: {self.total_own_goals_scoring_counted_for_maccabi_players}\n" \
               f"   Assists: {self.total_goals_assists_counted_for_maccabi_players}\n" \
               f"           By penalty winning: {self.total_goals_assists_by_penalty_winning_for_maccabi_players}\n" \
               f"           By corner: {self.total_goals_assists_by_corner_for_maccabi_players}\n" \
               f"           By freekick: {self.total_goals_assists_by_free_kick_for_maccabi_players}\n" \
               f"           By throw-in: {self.total_goals_assists_by_throw_in_for_maccabi_players}\n" \
               f"   Goals involved: {self.total_goals_involved_counted_for_maccabi_players}\n" \
               f"   Cards:\n" \
               f"        Yellow cards: {self.total_yellow_card_counted_for_maccabi_players}\n" \
               f"        Red cards: {self.total_red_card_counted_for_maccabi_players}\n" \
               f"   Captains: {self.total_captains_counted_for_maccabi_players}\n" \
               f"   Lineups: {self.total_lineups_counted_for_maccabi_players}\n" \
               f"   Players shirt number: {self.total_players_with_shirt_number_for_maccabi}\n"
