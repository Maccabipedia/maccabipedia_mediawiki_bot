from __future__ import annotations

from datetime import timedelta
from enum import Enum
from typing import Dict


class AssistTypes(Enum):
    NORMAL_ASSIST = 'NormalAssist'
    FREE_KICK_ASSIST = 'FreeKickAssist'
    CORNER_ASSIST = 'CornerAssist'
    THROW_IN_ASSIST = 'ThrowInAssist'
    PENALTY_WINNING_ASSIST = 'PenaltyWinningAssist'
    UNKNOWN = 'UnknownAssist'
    UNCATEGORIZED = 'UnCategorizedAssist'


class GoalTypes(Enum):
    FREE_KICK = 'FreeKickGoal'
    PENALTY = 'PenaltyGoal'
    HEADER = 'HeaderGoal'
    OWN_GOAL = 'OwnGoal'
    BICYCLE_KICK = 'BicycleKickGoal'
    NORMAL_KICK = 'NormalGoal'
    UNKNOWN = 'UnknownGoal'
    CORNER = 'CornerGoal'
    UNCATEGORIZED = 'UnCategorizedGoal'
    CHEST = 'Chest'

    @classmethod
    def _missing_(cls, value):
        # We use this function in order to allow old MaccabiGamesStats (pickled) to be loaded,
        # We replaced some of the values and we want to be able to load this.

        # We can not differentiate between normal and unknown goals in old maccabistats versions
        old_values_mapping = {'normal goal': GoalTypes.UNKNOWN,
                              'Penalty': GoalTypes.PENALTY,
                              'Own goal': GoalTypes.OWN_GOAL,
                              'Free-kick': GoalTypes.FREE_KICK,
                              'Header': GoalTypes.HEADER,
                              'Bicycle-kick': GoalTypes.BICYCLE_KICK}

        if value in old_values_mapping:
            return old_values_mapping[value]

        super()._missing_(value)


class GameEventTypes(Enum):
    GOAL_SCORE = 'ScoreGoal'
    RED_CARD = 'RedCard'
    YELLOW_CARD = 'YellowCard'  # No more than 1 yellow card in this game for this player
    FIRST_YELLOW_CARD = 'FirstYellowCard'
    SECOND_YELLOW_CARD = 'SecondYellowCard'
    LINE_UP = 'LineUp'
    SUBSTITUTION_IN = 'SubstitutionIn'
    SUBSTITUTION_OUT = 'SubstitutionOut'
    GOAL_ASSIST = 'AssistGoal'
    CAPTAIN = 'Captain'
    PENALTY_MISSED = 'PenaltyMissed'
    PENALTY_STOPPED = 'PenaltyStopped'
    BENCHED = "Benched"
    UNKNOWN = "Unknown"

    @classmethod
    def _missing_(cls, value):
        # We use this function in order to allow old MaccabiGamesStats (pickled) to be loaded,
        # We replaced some of the values and we want to be able to load this.
        old_values_mapping = {'Penalty missed': GameEventTypes.PENALTY_MISSED,
                              'Penalty-Missed': GameEventTypes.PENALTY_MISSED,
                              'Line-Up': GameEventTypes.LINE_UP,
                              'Score-Goal': GameEventTypes.GOAL_SCORE,
                              'Assist-Goal': GameEventTypes.GOAL_ASSIST,
                              'Substitution-In': GameEventTypes.SUBSTITUTION_IN,
                              'Substitution-Out': GameEventTypes.SUBSTITUTION_OUT,
                              'Red-Card': GameEventTypes.RED_CARD,
                              'Yellow-Card': GameEventTypes.YELLOW_CARD,
                              'Penalty-Stopped': GameEventTypes.PENALTY_STOPPED}

        if value in old_values_mapping:
            return old_values_mapping[value]

        super()._missing_(value)


class GameEvent(object):
    def __init__(self, game_event_type: GameEventTypes, time_occur: timedelta):
        self.event_type = game_event_type

        if not isinstance(time_occur, timedelta):
            raise Exception(f"time_occur parameter should be instance of timedelta: {time_occur}")

        self.time_occur = time_occur

    def __repr__(self) -> str:
        return "{self.event_type.value} occur at {self.time_occur}".format(self=self)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GameEvent):
            return NotImplemented

        return self.event_type == other.event_type and self.time_occur == other.time_occur

    def json_dict(self) -> Dict:
        return dict(event_type=self.event_type.value,
                    time_occur=str(self.time_occur))


class GoalGameEvent(GameEvent):
    def __init__(self, time_occur: timedelta, goal_type: GoalTypes = GoalTypes.UNKNOWN):
        super(GoalGameEvent, self).__init__(GameEventTypes.GOAL_SCORE, time_occur)
        self.goal_type = goal_type

    def __repr__(self) -> str:
        return "{game_event}\n" \
               "Goal type : {self.goal_type}".format(game_event=super(GoalGameEvent, self).__repr__(), self=self)

    def json_dict(self) -> Dict:
        base_class_json_dict = super(GoalGameEvent, self).json_dict()

        base_class_json_dict['goal_type'] = self.goal_type.value
        return base_class_json_dict


class AssistGameEvent(GameEvent):
    def __init__(self, time_occur: timedelta, assist_type: AssistTypes = AssistTypes.UNKNOWN):
        super(AssistGameEvent, self).__init__(GameEventTypes.GOAL_ASSIST, time_occur)
        self.assist_type = assist_type

    def __repr__(self) -> str:
        return "{game_event}\n" \
               "Assist type : {self.assist_type}".format(game_event=super(AssistGameEvent, self).__repr__(), self=self)

    def json_dict(self) -> Dict:
        base_class_json_dict = super(AssistGameEvent, self).json_dict()

        base_class_json_dict['assist_type'] = self.assist_type.value
        return base_class_json_dict
