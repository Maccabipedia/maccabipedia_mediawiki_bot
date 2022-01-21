from pywikibot import Site


class MaccabiPediaCragoDumper:
    def __init__(self):
        self.output_path = ""
        self.maccabipedia = Site()
        self.games = dict()
        self.games_events = dict()

    def dump_games_tables(self):
        request = self.maccabipedia._simple_request(action="cargoquery",
                                                    tables="Games_Catalog",
                                                    fields="Date, Hour, MatchDay, Season, Competition, Leg, Opponent, HomeAway, Stadium, ResultMaccabi, ResultOpponent, CoachMaccabi, CoachOpponent, Refs, Crowd",
                                                    limit=5000,
                                                    offset=0)
        self.games = request.submit()


if __name__ == "__main__":
    cargo_dumper = MaccabiPediaCragoDumper()

    cargo_dumper.dump_games_tables()

    a = 6
