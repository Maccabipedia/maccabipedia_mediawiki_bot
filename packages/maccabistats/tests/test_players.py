"""Tests for MaccabiGamesPlayersStats."""


class TestBestScorers:
    def test_best_scorers_order(self, maccabi_games):
        scorers = maccabi_games.players.best_scorers
        # שחקן_א: 8 goals across games (2+0+1+1+2+0+1+1+0+0 = 8)
        assert scorers[0] == ("שחקן_א", 8)

    def test_best_scorers_second(self, maccabi_games):
        scorers = maccabi_games.players.best_scorers
        # שחקן_ב: 4 goals (1+0+0+1+1+0+1+0+0+0)
        assert scorers[1] == ("שחקן_ב", 4)

    def test_best_scorers_sub_player(self, maccabi_games):
        scorers = dict(maccabi_games.players.best_scorers)
        # שחקן_יב: 2 goals (game 5 at 80min + game 6 at 85min)
        assert scorers["שחקן_יב"] == 2

    def test_best_scorers_by_penalty(self, maccabi_games):
        penalty_scorers = dict(maccabi_games.players.best_scorers_by_penalty)
        assert penalty_scorers.get("שחקן_א", 0) == 1  # Game 3 penalty

    def test_best_scorers_by_head(self, maccabi_games):
        header_scorers = dict(maccabi_games.players.best_scorers_by_head)
        assert header_scorers.get("שחקן_ב", 0) == 1  # Game 1 header

    def test_best_scorers_by_freekick(self, maccabi_games):
        fk_scorers = dict(maccabi_games.players.best_scorers_by_freekick)
        assert fk_scorers.get("שחקן_א", 0) == 1  # Game 4 free kick


class TestBestAssisters:
    def test_best_assisters(self, maccabi_games):
        assisters = maccabi_games.players.best_assisters
        # שחקן_ג assists in games 1(2), 4(2), 5(2), 7(2), 8(1) = 9
        assert assisters[0][0] == "שחקן_ג"
        assert assisters[0][1] == 9

    def test_most_goals_involved(self, maccabi_games):
        involved = dict(maccabi_games.players.most_goals_involved)
        # שחקן_א: 8 goals + 0 assists = 8
        # שחקן_ג: 0 goals + 9 assists = 9
        assert involved["שחקן_ג"] == 9
        assert involved["שחקן_א"] == 8


class TestMostPlayed:
    def test_most_played(self, maccabi_games):
        played = dict(maccabi_games.players.most_played)
        # שחקן_א plays in all 10 games
        assert played["שחקן_א"] == 10

    def test_most_played_sub_player(self, maccabi_games):
        played = dict(maccabi_games.players.most_played)
        # שחקן_יב plays 3 games (sub in)
        assert played["שחקן_יב"] == 3


class TestGameConditions:
    def test_most_winners(self, maccabi_games):
        winners = dict(maccabi_games.players.most_winners)
        # שחקן_א played all 10 games, 6 are wins
        assert winners["שחקן_א"] == 6

    def test_most_losers(self, maccabi_games):
        losers = dict(maccabi_games.players.most_losers)
        assert losers["שחקן_א"] == 2

    def test_most_unbeaten(self, maccabi_games):
        unbeaten = dict(maccabi_games.players.most_unbeaten)
        # 6 wins + 2 ties = 8 unbeaten
        assert unbeaten["שחקן_א"] == 8

    def test_most_clean_sheet(self, maccabi_games):
        clean = dict(maccabi_games.players.most_clean_sheet)
        # 4 clean sheets
        assert clean["שחקן_א"] == 4


class TestCards:
    def test_most_yellow_carded(self, maccabi_games):
        yellows = dict(maccabi_games.players.most_yellow_carded)
        # שחקן_א: 1 yellow (game 2)
        # שחקן_ו: 1 yellow (game 5)
        # שחקן_ד: 1 yellow (game 8)
        assert yellows.get("שחקן_א", 0) == 1
        assert yellows.get("שחקן_ו", 0) == 1

    def test_most_red_carded(self, maccabi_games):
        reds = dict(maccabi_games.players.most_red_carded)
        # שחקן_ד has a second yellow in game 8 (counts as red)
        assert reds.get("שחקן_ד", 0) == 1


class TestSubstitutions:
    def test_most_substitute_in(self, maccabi_games):
        sub_ins = dict(maccabi_games.players.most_substitute_in)
        # שחקן_יב: 3 sub ins (games 2, 5, 6)
        assert sub_ins["שחקן_יב"] == 3

    def test_most_substitute_off(self, maccabi_games):
        sub_offs = dict(maccabi_games.players.most_substitute_off)
        # שחקן_ג: 1 sub out (game 2)
        # שחקן_ח: 1 sub out (game 5)
        # שחקן_ב: 1 sub out (game 6)
        assert sub_offs.get("שחקן_ג", 0) == 1


class TestCaptains:
    def test_most_captains(self, maccabi_games):
        captains = dict(maccabi_games.players.most_captains)
        assert captains["שחקן_א"] == 10


class TestGoalsAfterSubIn:
    def test_most_goals_after_sub_in(self, maccabi_games):
        goals_after_sub = dict(maccabi_games.players.most_goals_after_sub_in)
        # שחקן_יב scores after sub in in games 5 and 6
        assert goals_after_sub.get("שחקן_יב", 0) == 2


class TestPercentages:
    def test_most_winners_by_percentage(self, maccabi_games):
        result = maccabi_games.players.most_winners_by_percentage(minimum_games_played=5)
        # Filter for players with >= 5 games
        assert len(result) > 0
        # Each entry is (name, percentage, total_games)
        for entry in result:
            assert entry.total_games >= 5

    def test_never_lost(self, maccabi_games):
        never_lost = maccabi_games.players.never_lost(minimum_games_to_player=1)
        never_lost_names = {p[0] for p in never_lost}
        # שחקן_א lost 2 games, should NOT be in never_lost
        assert "שחקן_א" not in never_lost_names
