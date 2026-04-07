from __future__ import annotations

import json
import logging
import typing
from collections import Counter
from typing import List, Callable, Dict, Any, Optional

from maccabistats.models.player_game_events import GameEventTypes, GoalTypes
from maccabistats.models.player_in_game import PlayerInGame
from maccabistats.models.team import Team

logger = logging.getLogger(__name__)


class TeamInGame(Team):
    def __init__(self, name: str, coach: str, score: int, players: List[PlayerInGame],
                 current_name: Optional[str] = None):
        super(TeamInGame, self).__init__(name)

        self.coach = coach
        self.score = score
        self.players = players

        # In case team name change the name during the years, the self.name will contain the name as they appear
        # to the specific game and the self.current_name is the current name they has
        self.current_name = current_name or name

    @property
    def lineup_players(self) -> List[PlayerInGame]:
        return [player for player in self.players if player.has_event_type(GameEventTypes.LINE_UP)]

    @property
    def players_from_bench(self) -> List[PlayerInGame]:
        return [player for player in self.players if not player.has_event_type(GameEventTypes.LINE_UP) and
                player.has_event_type(GameEventTypes.SUBSTITUTION_IN)]

    @property
    def not_played_players(self) -> List[PlayerInGame]:
        return [player for player in self.players if
                not player.has_event_type(GameEventTypes.LINE_UP) and not player.has_event_type(
                    GameEventTypes.SUBSTITUTION_IN)]

    @property
    def scored_players(self) -> List[PlayerInGame]:
        return [player for player in self.players if player.has_event_type(GameEventTypes.GOAL_SCORE)]

    @property
    def assist_players(self) -> List[PlayerInGame]:
        return [player for player in self.players if player.has_event_type(GameEventTypes.GOAL_ASSIST)]

    @property
    def yellow_carded_players(self) -> List[PlayerInGame]:
        return [player for player in self.players if player.has_event_type(GameEventTypes.YELLOW_CARD)]

    @property
    def red_carded_players(self) -> List[PlayerInGame]:
        return [player for player in self.players if
                player.has_event_type(GameEventTypes.RED_CARD) or
                player.has_event_type(GameEventTypes.SECOND_YELLOW_CARD)]

    @property
    def played_players(self) -> List[PlayerInGame]:
        return [player for player in self.players if player.played_in_game]

    @property
    def captain(self) -> PlayerInGame:
        captains = [player for player in self.players if player.has_event_type(GameEventTypes.CAPTAIN)]

        if len(captains) > 1:
            logger.warning("Found {caps} captains, returning the first 1!".format(caps=len(captains)))
            return captains[0]
        elif captains:
            return captains[0]
        else:
            logger.warning("Cant find any captain for this game :(")
            return PlayerInGame("Not a captain", 0, [])

    def get_players_with_most_of_this_condition(self, condition: Callable[[PlayerInGame], int]) \
            -> typing.Counter[str]:
        """
        :param condition: this function should get PlayerInGame as param, and return int.
                          0 wont count this player in the final summary.
        """
        return Counter({player.name: condition(player) for player in self.players if
                        condition(player) > 0})

    @property
    def scored_players_with_amount(self) -> typing.Counter[str]:
        return self.get_players_with_most_of_this_condition(
            lambda p: p.event_count_by_type(GameEventTypes.GOAL_SCORE))

    @property
    def scored_for_maccabi_players_with_amount(self) -> typing.Counter[str]:
        def scored_maccabi_goals(p) -> int:
            return p.event_count_by_type(GameEventTypes.GOAL_SCORE) - p.goals_count_by_goal_type(GoalTypes.OWN_GOAL)

        return self.get_players_with_most_of_this_condition(scored_maccabi_goals)

    @property
    def lineup_players_with_amount(self) -> typing.Counter[str]:
        return self.get_players_with_most_of_this_condition(
            lambda p: p.event_count_by_type(GameEventTypes.LINE_UP))

    @property
    def assist_players_with_amount(self) -> typing.Counter[str]:
        return self.get_players_with_most_of_this_condition(
            lambda p: p.event_count_by_type(GameEventTypes.GOAL_ASSIST))

    @property
    def goal_involved_players_with_amount(self) -> typing.Counter[str]:
        return self.assist_players_with_amount + self.scored_players_with_amount

    @property
    def substitute_off_players_with_amount(self) -> typing.Counter[str]:
        return self.get_players_with_most_of_this_condition(
            lambda p: p.event_count_by_type(GameEventTypes.SUBSTITUTION_OUT))

    @property
    def substitute_in_players_with_amount(self) -> typing.Counter[str]:
        return self.get_players_with_most_of_this_condition(
            lambda p: p.event_count_by_type(GameEventTypes.SUBSTITUTION_IN))

    @property
    def yellow_carded_players_with_amount(self) -> typing.Counter[str]:
        return self.get_players_with_most_of_this_condition(
            lambda p: p.event_count_by_type(GameEventTypes.YELLOW_CARD))

    @property
    def red_carded_players_with_amount(self) -> typing.Counter[str]:
        return self.get_players_with_most_of_this_condition(
            lambda p: p.event_count_by_type(GameEventTypes.RED_CARD) + p.event_count_by_type(
                GameEventTypes.SECOND_YELLOW_CARD))

    @property
    def captains_players_with_amount(self) -> typing.Counter[str]:
        return self.get_players_with_most_of_this_condition(
            lambda p: p.event_count_by_type(GameEventTypes.CAPTAIN))

    @property
    def penalty_missed_players_with_amount(self) -> typing.Counter[str]:
        return self.get_players_with_most_of_this_condition(
            lambda p: p.event_count_by_type(GameEventTypes.PENALTY_MISSED))

    @property
    def played_players_with_amount(self) -> typing.Counter[str]:
        # Return counter of 1 of all played players in game
        return Counter({player.name: 1 for player in self.played_players})

    @property
    def has_goal_from_bench(self) -> bool:
        return any(player.scored_after_sub_in for player in self.players_from_bench)

    def event_type_to_property_of_most_common_players(self, event_type: GameEventTypes) -> Callable[[], Any]:
        # In order to get the most common players in each event type, we need to create mapping
        # between event type to the required function, so maccabi wrapper object will know which function to call.
        event_type_to_property_of_most_common_players = {
            GameEventTypes.SUBSTITUTION_OUT: self.substitute_off_players_with_amount,
            GameEventTypes.SUBSTITUTION_IN: self.substitute_in_players_with_amount,
            GameEventTypes.GOAL_SCORE: self.scored_players_with_amount,
            GameEventTypes.GOAL_ASSIST: self.assist_players_with_amount,
            GameEventTypes.LINE_UP: self.lineup_players_with_amount,
            GameEventTypes.YELLOW_CARD: self.yellow_carded_players_with_amount,
            GameEventTypes.RED_CARD: self.red_carded_players_with_amount,
            GameEventTypes.CAPTAIN: self.captains_players_with_amount,
            GameEventTypes.PENALTY_MISSED: self.penalty_missed_players_with_amount}

        return event_type_to_property_of_most_common_players[event_type]

    def json_dict(self) -> Dict:
        return dict(name=self.name,
                    score=self.score,
                    coach=self.coach)

    def to_json(self) -> str:
        return json.dumps(self.json_dict())

    def __str__(self) -> str:
        return "{team_repr}" \
               "Scored: {self.score}\n" \
               "Coach: {self.coach}\n".format(team_repr=super(TeamInGame, self).__repr__(), self=self)

    def __repr__(self) -> str:
        return "{my_str}\n" \
               "Players: {self.players}\n\n".format(my_str=self.__str__(), self=self)
