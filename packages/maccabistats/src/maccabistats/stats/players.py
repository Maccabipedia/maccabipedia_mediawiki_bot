from __future__ import annotations

from typing import TYPE_CHECKING, List, Tuple, Callable, NamedTuple, Dict

from maccabistats.models.game_data import GameData
from maccabistats.models.player_in_game import PlayerInGame

if TYPE_CHECKING:
    from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats

from collections import Counter
from datetime import timedelta
from functools import reduce
import logging
from maccabistats.models.player_game_events import GameEventTypes, GoalTypes, AssistTypes

logger = logging.getLogger(__name__)

PlayerStats = Tuple[str, int]  # Player name to the current stat (an int ranking)

PlayerNameToStat = Dict[str, float]


class _PlayerGamesPercentages(NamedTuple):
    name: str
    percentage: float
    total_games: int


class MaccabiGamesPlayersStats(object):
    """
    This class will handle all players statistics.
    """

    def __init__(self, maccabi_games_stats: MaccabiGamesStats) -> None:
        self.games = maccabi_games_stats.games

    # region Top players by last minute goals related sorting

    def get_top_scorers_on_last_minutes(self, from_minute: int = 75) -> List[PlayerStats]:
        from_this_minute_str = str(timedelta(minutes=from_minute))
        return self.__get_players_from_all_games_with_most_of_this_condition(
            lambda p: len([event for event in p.events
                           if event.event_type == GameEventTypes.GOAL_SCORE and str(
                    event.time_occur) > from_this_minute_str]))

    def get_top_players_for_goals_per_game(self, minimum_games_played: int = 10) -> List[PlayerStats]:
        players_total_played = Counter(dict(self.most_played))
        players_total_goals = Counter(dict(self.best_scorers))

        best_players = Counter()
        for player_name, total_games_for_player in players_total_played.items():
            if total_games_for_player >= minimum_games_played:
                key_name = "{player} - {total_games} games".format(player=player_name,
                                                                   total_games=total_games_for_player)
                best_players[key_name] = round(players_total_goals[player_name] / total_games_for_player, 2)

        return best_players.most_common()

    def get_top_players_for_goals_involvement_per_game(self, minimum_games_played: int = 10) -> List[PlayerStats]:
        players_total_played = Counter(dict(self.most_played))
        players_total_goals_involvement = Counter(dict(self.most_goals_involved))

        best_players = Counter()
        for player_name, total_games_for_player in players_total_played.items():
            if total_games_for_player >= minimum_games_played:
                key_name = "{player} - {total_games} games".format(player=player_name,
                                                                   total_games=total_games_for_player)
                best_players[key_name] = round(players_total_goals_involvement[player_name] / total_games_for_player, 2)

        return best_players.most_common()

    # endregion

    # region Top players by goals related sorting

    @property
    def best_scorers(self) -> List[PlayerStats]:
        return self.__get_players_from_all_games_with_most_of_this_condition(
            lambda p: p.event_count_by_type(GameEventTypes.GOAL_SCORE) - p.goals_count_by_goal_type(GoalTypes.OWN_GOAL))

    @property
    def best_scorers_by_freekick(self) -> List[PlayerStats]:
        return self.__get_players_from_all_games_with_most_of_this_condition(
            lambda p: p.goals_count_by_goal_type(GoalTypes.FREE_KICK))

    @property
    def best_scorers_by_penalty(self) -> List[PlayerStats]:
        return self.__get_players_from_all_games_with_most_of_this_condition(
            lambda p: p.goals_count_by_goal_type(GoalTypes.PENALTY))

    @property
    def best_scorers_by_head(self) -> List[PlayerStats]:
        return self.__get_players_from_all_games_with_most_of_this_condition(
            lambda p: p.goals_count_by_goal_type(GoalTypes.HEADER))

    @property
    def best_scorers_by_foot(self) -> List[PlayerStats]:
        return self.__get_players_from_all_games_with_most_of_this_condition(
            lambda p: p.goals_count_by_goal_type(GoalTypes.NORMAL_KICK))

    @property
    def best_scorers_by_own_goal(self) -> List[PlayerStats]:
        return self.__get_players_from_all_games_with_most_of_this_condition(
            lambda p: p.goals_count_by_goal_type(GoalTypes.OWN_GOAL))

    @property
    def best_assisters(self) -> List[PlayerStats]:
        return self.__get_players_from_all_games_with_most_of_this_condition(
            lambda p: p.event_count_by_type(GameEventTypes.GOAL_ASSIST))

    @property
    def best_assisters_by_penalty_winning(self) -> List[PlayerStats]:
        return self.__get_players_from_all_games_with_most_of_this_condition(
            lambda p: p.assists_count_by_assist_type(AssistTypes.PENALTY_WINNING_ASSIST))

    @property
    def best_assisters_by_corner(self) -> List[PlayerStats]:
        return self.__get_players_from_all_games_with_most_of_this_condition(
            lambda p: p.assists_count_by_assist_type(AssistTypes.CORNER_ASSIST))

    @property
    def best_assisters_by_free_kick(self) -> List[PlayerStats]:
        return self.__get_players_from_all_games_with_most_of_this_condition(
            lambda p: p.assists_count_by_assist_type(AssistTypes.FREE_KICK_ASSIST))

    @property
    def best_assisters_by_throw_in(self) -> List[PlayerStats]:
        return self.__get_players_from_all_games_with_most_of_this_condition(
            lambda p: p.assists_count_by_assist_type(AssistTypes.THROW_IN_ASSIST))

    @property
    def most_goals_involved(self) -> List[PlayerStats]:
        """
        Top players which involved in goals (score or assist)
        """
        return self.__get_players_from_all_games_with_most_of_this_condition(
            lambda p: p.event_count_by_type(GameEventTypes.GOAL_ASSIST) + p.event_count_by_type(
                GameEventTypes.GOAL_SCORE) - p.goals_count_by_goal_type(GoalTypes.OWN_GOAL))

    # endregion

    # region Top players by other game events sorting

    @property
    def most_yellow_carded(self) -> List[PlayerStats]:
        return self.__get_players_from_all_games_with_most_of_this_condition(
            lambda p: p.event_count_by_type(GameEventTypes.YELLOW_CARD))

    @property
    def most_red_carded(self) -> List[PlayerStats]:
        return self.__get_players_from_all_games_with_most_of_this_condition(
            lambda p: p.event_count_by_type(GameEventTypes.RED_CARD) + p.event_count_by_type(
                GameEventTypes.SECOND_YELLOW_CARD))

    @property
    def most_substitute_off(self) -> List[PlayerStats]:
        return self.__get_players_from_all_games_with_most_of_this_condition(
            lambda p: p.event_count_by_type(GameEventTypes.SUBSTITUTION_OUT))

    @property
    def most_substitute_in(self) -> List[PlayerStats]:
        return self.__get_players_from_all_games_with_most_of_this_condition(
            lambda p: p.event_count_by_type(GameEventTypes.SUBSTITUTION_IN))

    @property
    def most_lineup_players(self) -> List[PlayerStats]:
        return self.__get_players_from_all_games_with_most_of_this_condition(
            lambda p: p.event_count_by_type(GameEventTypes.LINE_UP))

    @property
    def most_captains(self) -> List[PlayerStats]:
        return self.__get_players_from_all_games_with_most_of_this_condition(
            lambda p: p.event_count_by_type(GameEventTypes.CAPTAIN))

    @property
    def most_penalty_missed(self) -> List[PlayerStats]:
        return self.__get_players_from_all_games_with_most_of_this_condition(
            lambda p: p.event_count_by_type(GameEventTypes.PENALTY_MISSED))

    @property
    def most_penalty_stopped(self) -> List[PlayerStats]:
        return self.__get_players_from_all_games_with_most_of_this_condition(
            lambda p: p.event_count_by_type(GameEventTypes.PENALTY_STOPPED))

    # endregion

    # region Top players by condition at the game level

    @property
    def most_winners(self) -> List[PlayerStats]:
        return self.__get_players_with_most_of_this_game_condition(lambda g: g.is_maccabi_win)

    @property
    def most_losers(self) -> List[PlayerStats]:
        return self.__get_players_with_most_of_this_game_condition(lambda g: g.maccabi_score_diff < 0)

    @property
    def most_unbeaten(self) -> List[PlayerStats]:
        return self.__get_players_with_most_of_this_game_condition(lambda g: g.maccabi_score_diff >= 0)

    @property
    def most_clean_sheet(self) -> List[PlayerStats]:
        return self.__get_players_with_most_of_this_game_condition(lambda g: g.not_maccabi_team.score == 0)

    @property
    def most_played(self) -> List[PlayerStats]:
        return self.__get_players_with_most_of_this_game_condition(lambda g: True)

    @staticmethod
    def __goals_count_after_sub_in(player: PlayerInGame) -> int:
        """
        Count the goals after sub in for this player
        """
        if not player.scored:
            return 0
        if not player.has_event_type(GameEventTypes.SUBSTITUTION_IN):
            return 0

        count_by_goals = player.event_count_by_type(GameEventTypes.GOAL_SCORE)

        subs_in_time = player.get_events_by_type(GameEventTypes.SUBSTITUTION_IN)[0].time_occur
        count_goals_after_sub = len(
            [goal for goal in player.get_events_by_type(GameEventTypes.GOAL_SCORE) if goal.time_occur >= subs_in_time])

        # Avoid bugs in maccabi site which registered players as subs in min 0.
        if subs_in_time == timedelta(seconds=0):
            return False

        if count_by_goals != count_goals_after_sub:
            # TODO: This is just for safety
            logger.error(f"A player: {player.name} has different number of goals in 'goals_after_sub_in' calculation.")

            return 0

        return count_by_goals

    @property
    def most_goals_after_sub_in(self) -> List[PlayerStats]:
        return self.__get_players_from_all_games_with_most_of_this_condition(
            lambda p: self.__goals_count_after_sub_in(p))

    # endregion

    # region Top players by game condition - percentages of games

    def most_winners_by_percentage(self, minimum_games_played: int = 0) -> List[_PlayerGamesPercentages]:
        """
        Returns sorted list of (player, wins, played) for each player.
        """
        return self.__get_most_players_by_percentage_with_this_game_condition(dict(self.most_winners),
                                                                              minimum_games_played)

    def most_losers_by_percentage(self, minimum_games_played: int = 0) -> List[_PlayerGamesPercentages]:
        """
        Returns sorted list of (player, losses, played) for each player.
        """
        return self.__get_most_players_by_percentage_with_this_game_condition(dict(self.most_losers),
                                                                              minimum_games_played)

    def most_unbeaten_by_percentage(self, minimum_games_played: int = 0) -> List[_PlayerGamesPercentages]:
        """
        Returns sorted list of (player, unbeaten, played) for each player.
        """
        return self.__get_most_players_by_percentage_with_this_game_condition(dict(self.most_unbeaten),
                                                                              minimum_games_played)

    def most_clean_sheet_by_percentage(self, minimum_games_played: int = 0) -> List[_PlayerGamesPercentages]:
        """
        Returns sorted list of (player, clean_sheer, played) for each player.
        """
        return self.__get_most_players_by_percentage_with_this_game_condition(dict(self.most_clean_sheet),
                                                                              minimum_games_played)

    # endregion

    def never_lost(self, minimum_games_to_player: int = 5) -> List[PlayerStats]:
        played_more_than_minimum_games = [player for player in self.most_played if
                                          player[1] >= minimum_games_to_player]

        players_that_lost = set(player[0] for player in self.most_losers)

        return [player for player in played_more_than_minimum_games if player[0] not in players_that_lost]

    def __get_players_from_all_games_with_most_of_this_condition(self, condition: Callable[[PlayerInGame], int]) \
            -> List[PlayerStats]:
        """
        :param condition: this function should get PlayerInGame as param, and return int.
                          0 wont count this player in the final summary.
        """
        players_with_most_event_type = reduce(
            lambda events_counter_a, events_counter_b: events_counter_a + events_counter_b,

            # TeamInGame saves dict which map between player event to the property
            # which return the most common players which have this event in this game & team.
            [game.maccabi_team.get_players_with_most_of_this_condition(condition)
             for game in self.games],
            Counter([]))  # When self.games above is empty, reduce will return this default value.

        return players_with_most_event_type.most_common()

    def __get_players_with_most_of_this_game_condition(self, condition: Callable[[GameData], bool] = None) \
            -> List[PlayerStats]:
        """
        Return the players which played the most at games with the given condition,
        example: __get_players_with_most_of_this_game_condition(lambda g: g.is_maccabi_win)
        for players who played when maccabi won.
        :param condition: callable which get game as param and return bool (if need to count this game).
        """

        if condition is None:
            condition = lambda g: True

        # Like __get_players_with_most_of_this_event
        most_played_players_with_game_condition = reduce(
            lambda played_counter_a, played_counter_b: played_counter_a + played_counter_b,
            [game.maccabi_team.played_players_with_amount
             for game in self.games if condition(game)],
            # Have an initializer for the case that no game satisfies the condition
            Counter({})
        )

        return Counter(most_played_players_with_game_condition).most_common()

    def __get_most_players_by_percentage_with_this_game_condition(
            self, players_ordered_by_game_condition: PlayerNameToStat, minimum_games_played: int = 0) \
            -> List[_PlayerGamesPercentages]:
        """
        Return list of players ordered by their percentage of (played games with this condition) / (played games)
        example : __get_most_players_by_percentage_with_this_game_condition(self.most_winner)
        for list of most winner players by percentage.
        Filter can be done with minimum_games_played to ignore players with high percentage and few games played.
        :param players_ordered_by_game_condition: Dict of players ordered by game condition,
                                                  dict key: player(normal player - without events)
                                                  dict value: count of game the player played with the game condition.
        :param minimum_games_played: used to ignore players with high percentage and few games.
        """

        total_players_games = dict(self.most_played)

        players_percentage = [_PlayerGamesPercentages(
            name=player,
            percentage=round(players_ordered_by_game_condition.get(player, 0) * 100 /  # 100 for percentage
                             total_players_games[player], 3),
            total_games=total_players_games[player])

            for player in total_players_games.keys()
            if total_players_games[player] >= minimum_games_played]

        sorted_players_percentage = sorted(players_percentage, key=lambda player: player.percentage, reverse=True)
        return sorted_players_percentage
