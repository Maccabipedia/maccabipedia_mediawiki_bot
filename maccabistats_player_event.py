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
                                              GameEventTypes.PENALTY_MISSED.value: "החטאת פנדל",
                                              }

maccabistats_sub_events_to_maccabipedia_events = {GoalTypes.OWN_GOAL.value: "עצמי",
                                                  GoalTypes.PENALTY.value: "פנדל",
                                                  GoalTypes.UNKNOWN.value: None,
                                                  GoalTypes.HEADER.value: "נגיחה",
                                                  GoalTypes.FREE_KICK.value: "בעיטה חופשית",
                                                  }


class PlayerEvent(object):
    def __init__(self, name, number, time_occur, event_type, sub_event_type, maccabi_player):
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

        self.name = name
        self.number = number or "אין-מספר"
        self.minute_occur = int(time_occur.seconds / 60)
        self.event_type = self._translate_event_to_maccabipedia(event_type)
        self.sub_event_type = self._translate_sub_event_to_maccabipedia(sub_event_type) if sub_event_type else None
        self.team = "מכבי" if maccabi_player else "יריבה"

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

    def __maccabipedia__(self):
        """
        Return the player event as maccabipedia format expect it
        """
        if self.sub_event_type is not None:
            return "{name}::{number}::{event_type}-{sub_event_type}::{minute_occur}::{team}\n".format(**self.__dict__)
        else:
            return "{name}::{number}::{event_type}::{minute_occur}::{team}\n".format(**self.__dict__)
