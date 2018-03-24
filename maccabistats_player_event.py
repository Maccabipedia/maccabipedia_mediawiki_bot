class PlayerEvent(object):
    def __init__(self, name, number, time_occur, event_type, sub_event_type):
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
        """

        self.name = name
        self.number = number or "אין-מספר"
        self.minute_occur = int(time_occur.seconds/60)
        self.event_type = event_type
        self.sub_event_type = sub_event_type
