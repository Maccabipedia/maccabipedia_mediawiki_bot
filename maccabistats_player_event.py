from collections import defaultdict
from datetime import timedelta

from maccabistats.models.player_game_events import GameEventTypes, GoalTypes

maccabistats_events_to_maccabipedia_events = {GameEventTypes.LINE_UP.value: "הרכב",
                                              GameEventTypes.BENCHED.value: "ספסל",
                                              GameEventTypes.GOAL_SCORE.value: "גול",
                                              GameEventTypes.GOAL_ASSIST.value: "בישול",
                                              GameEventTypes.SUBSTITUTION_IN.value: "מחליף",
                                              GameEventTypes.SUBSTITUTION_OUT.value: "מוחלף",
                                              GameEventTypes.YELLOW_CARD.value: "כרטיס צהוב",
                                              GameEventTypes.RED_CARD.value: "כרטיס אדום",
                                              GameEventTypes.CAPTAIN.value: "קפטן",
                                              GameEventTypes.PENALTY_MISSED.value: "פנדל-החמצה",
                                              GameEventTypes.PENALTY_STOPPED.value: "פנדל-עצירה",
                                              }

maccabistats_sub_events_to_maccabipedia_events = {GoalTypes.OWN_GOAL.value: "עצמי",
                                                  GoalTypes.PENALTY.value: "פנדל",
                                                  GoalTypes.UNKNOWN.value: None,
                                                  GoalTypes.HEADER.value: "נגיחה",
                                                  GoalTypes.FREE_KICK.value: "בעיטה חופשית",
                                                  }

SQUAD_RANK = {"הרכב": 0,
              "קפטן": 1,
              "ספסל": 2,

              None: 5,  # No sub event
              "שוער": 4  # Goal keeper should be written before players
              }

SUBS_RANK = defaultdict(lambda: 5, {"מוחלף": 6,
                                    "מחליף": 7})

# Assists, Goals then the rest (only if the events are at the same minute)
GOALS_RANK = defaultdict(lambda: 5, {"בישול": 3,
                                     "גול": 4,
                                     "פנדל": 6,

                                     "החמצה": 7,
                                     "עצירה": 8})

SQUAD = [maccabistats_events_to_maccabipedia_events[GameEventTypes.LINE_UP.value],
         maccabistats_events_to_maccabipedia_events[GameEventTypes.BENCHED.value],
         maccabistats_events_to_maccabipedia_events[GameEventTypes.CAPTAIN.value]]

CARDS_AND_SUBS = [maccabistats_events_to_maccabipedia_events[GameEventTypes.RED_CARD.value],
                  maccabistats_events_to_maccabipedia_events[GameEventTypes.YELLOW_CARD.value],
                  maccabistats_events_to_maccabipedia_events[GameEventTypes.SUBSTITUTION_IN.value],
                  maccabistats_events_to_maccabipedia_events[GameEventTypes.SUBSTITUTION_OUT.value]]

GOALS_INVOLVED = [maccabistats_events_to_maccabipedia_events[GameEventTypes.GOAL_SCORE.value],
                  maccabistats_events_to_maccabipedia_events[GameEventTypes.GOAL_ASSIST.value],
                  "פנדל"]

_MACCABIPEDIA_PROPERTY_SEPARATOR = "::"


class PlayerEvent(object):
    def __init__(self, name, number, time_occur, event_type, sub_event_type, maccabi_player, game_part=None):
        """
        :param name: The player name
        :type: str
        :param number: The player number
        :type: int
        :param time_occur: The time the event has occurred to this player
        :type time_occur: datetime.timedelta
        :param event_type: The player event type (look at maccabistats.models.player_game_events.py)
        :type: maccabistats.models.player_game_events.GameEventTypes
        :param sub_event_type: The player sub event type, like goal by *head*(head=sub event type),
                               the sub type is just goal types atm, may be change in the future.
        :type sub_event_type: maccabistats.models.player_game_events.GoalTypes
        :param maccabi_player: does this player is maccabi player
        :type maccabi_player: bool
        :param game_part: In which game part this event occur? first/second half? extra time? and so on
        :type game_part: str
        """

        self.name = name
        self.number = number or "אין-מספר"
        self.minute_occur = int(time_occur.seconds / 60)
        self.event_type = event_type
        self.sub_event_type = sub_event_type
        self.team = "מכבי" if maccabi_player else "יריבה"
        self.game_part = game_part

        # Not for export:
        self.maccabi_player = maccabi_player

    @staticmethod
    def _translate_event_to_maccabipedia(event):
        """
        Translate the event name to hebrew
        :param event: maccabistats event type to translate (to maccabipedia one).
        :type event: maccabistats.models.player_game_events.GameEventTypes
        """

        if event.value not in maccabistats_events_to_maccabipedia_events:
            raise RuntimeError("There is no matching maccabipedia event for {event}".format(event=event.value))
        else:
            return maccabistats_events_to_maccabipedia_events[event.value]

    @staticmethod
    def _translate_sub_event_to_maccabipedia(sub_event):
        """
        Translate the event name to hebrew
        :param sub_event: maccabistats sub event type to translate (to maccabipedia one).
        :type sub_event: maccabistats.models.player_game_events.GoalTypes
        """

        if sub_event.value not in maccabistats_sub_events_to_maccabipedia_events:
            raise RuntimeError("There is no matching maccabipedia sub event for {sub_event}".format(sub_event=sub_event.value))
        else:
            return maccabistats_sub_events_to_maccabipedia_events[sub_event.value]

    def __eq__(self, other):
        a = 7

    def __lt__(self, other):
        """
        Compare two events, True if "Self" is less than "Other", False otherwise.
        :type other: PlayerEvent
        :rtype: bool
        """
        squad = (self.event_type in SQUAD) == (other.event_type in SQUAD)
        cards_and_subs = (self.event_type in CARDS_AND_SUBS) == (other.event_type in CARDS_AND_SUBS)
        goals_involved = (self.event_type in GOALS_INVOLVED) == (other.event_type in GOALS_INVOLVED)
        # Events must be in same group, we dont handle compare of not same group events (we dont need):
        if not squad or not cards_and_subs or not goals_involved:
            raise RuntimeError("Events should be in the same group")

        if self.maccabi_player and not other.maccabi_player:
            return True
        elif self.maccabi_player != other.maccabi_player:
            return False  # Different and self is not maccabi

        # Same team for sure from now on:
        if self.event_type in SQUAD:  # Squad, Captain, Bench. GoalKeeper first, Sort by shirt number in order of "tie".
            return (SQUAD_RANK[self.event_type], SQUAD_RANK[self.sub_event_type], self.number) < (
                SQUAD_RANK[other.event_type], SQUAD_RANK[other.sub_event_type], other.number)

        if self.event_type in CARDS_AND_SUBS:
            return (self.minute_occur, SUBS_RANK[self.event_type]) < (other.minute_occur, SUBS_RANK[self.event_type])

        if self.event_type in GOALS_INVOLVED:
            return (self.minute_occur, GOALS_RANK[self.event_type]) < (other.minute_occur, GOALS_RANK[self.event_type])

    def __maccabipedia__(self):
        """
        Return the player event as maccabipedia format expect it
        """
        # Hacky part for backward compatible (we dont want to add game part in events we didn't had one).
        game_part_property = "" if self.game_part is None else f"::{self.game_part}"

        if self.sub_event_type is not None:
            return f"{self.name}::{self.number}::{self.event_type}-{self.sub_event_type}::{self.minute_occur}::{self.team}{game_part_property}\n"
        else:
            return f"{self.name}::{self.number}::{self.event_type}::{self.minute_occur}::{self.team}{game_part_property}\n"

    def __repr__(self):
        return self.__maccabipedia__()

    @classmethod
    def from_maccabistats_event_type(cls, name, number, time_occur, event_type, sub_event_type, maccabi_player):
        """
        :param name: The player name
        :type: str
        :param number: The player number
        :type: int
        :param time_occur: The time the event has occurred to this player
        :type time_occur: datetime.timedelta
        :param event_type: The player event type (look at maccabistats.models.player_game_events.py)
        :type: maccabistats.models.player_game_events.GameEventTypes
        :param sub_event_type: The player sub event type, like goal by *head*(head=sub event type),
                               the sub type is just goal types atm, may be change in the future.
        :type sub_event_type: maccabistats.models.player_game_events.GoalTypes
        :param maccabi_player: does this player is maccabi player
        :type maccabi_player: bool
        """

        event_type = PlayerEvent._translate_event_to_maccabipedia(event_type)
        sub_event_type = PlayerEvent._translate_sub_event_to_maccabipedia(sub_event_type) if sub_event_type else None

        return PlayerEvent(name, number, time_occur, event_type, sub_event_type, maccabi_player)

    @classmethod
    def from_maccabipedia_format(cls, maccabipedia_text_format):
        """
        Creates a PlayerEvent from maccabipedia text format
        :type maccabipedia_text_format: str
        :rtype: PlayerEvent
        """
        properties = maccabipedia_text_format.strip('\n').split(_MACCABIPEDIA_PROPERTY_SEPARATOR)  # Remove leading and ending new lines + split
        if not 5 <= len(properties) <= 6:  # Might have game_part - optional
            raise TypeError(f"{maccabipedia_text_format} should have 5 properties (separated by {_MACCABIPEDIA_PROPERTY_SEPARATOR}).")

        name = properties[0]
        number = properties[1]
        minute_occur = timedelta(minutes=int(properties[3]))
        team = properties[4] == "מכבי"

        event_and_sub_event = properties[2].split('-')
        event_type_name = event_and_sub_event[0]
        sub_event_type_name = None
        if len(event_and_sub_event) > 1:
            sub_event_type_name = event_and_sub_event[1]

        game_part = None
        if len(properties) == 6:
            game_part = properties[5]

        return PlayerEvent(name, number, minute_occur, event_type_name, sub_event_type_name, team, game_part)
