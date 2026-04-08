"""Tests for MaccabiGamesCoachesStats."""


class TestCoachesBasicStats:
    def test_most_trained_coach(self, maccabi_games):
        trained = dict(maccabi_games.coaches.most_trained_coach)
        assert trained["אברם גרנט"] == 6
        assert trained["פאולו סוזה"] == 4

    def test_most_winner_coach(self, maccabi_games):
        winners = dict(maccabi_games.coaches.most_winner_coach)
        # אברם גרנט: wins in games 1,4,5,6 = 4
        # פאולו סוזה: wins in games 7,10 = 2
        assert winners["אברם גרנט"] == 4
        assert winners["פאולו סוזה"] == 2

    def test_most_loser_coach(self, maccabi_games):
        losers = dict(maccabi_games.coaches.most_loser_coach)
        # אברם גרנט: loss in game 2 = 1
        # פאולו סוזה: loss in game 8 = 1
        assert losers["אברם גרנט"] == 1
        assert losers["פאולו סוזה"] == 1

    def test_most_goals_for_maccabi_coach(self, maccabi_games):
        goals = dict(maccabi_games.coaches.most_goals_for_maccabi_coach)
        # אברם גרנט: 3+0+1+2+4+1 = 11
        # פאולו סוזה: 2+1+0+3 = 6
        assert goals["אברם גרנט"] == 11
        assert goals["פאולו סוזה"] == 6

    def test_most_goals_against_maccabi_coach(self, maccabi_games):
        goals_against = dict(maccabi_games.coaches.most_goals_against_maccabi_coach)
        # אברם גרנט: 1+2+1+0+2+0 = 6
        # פאולו סוזה: 1+3+0+0 = 4
        assert goals_against["אברם גרנט"] == 6
        assert goals_against["פאולו סוזה"] == 4

    def test_most_clean_sheet_games_coach(self, maccabi_games):
        clean = dict(maccabi_games.coaches.most_clean_sheet_games_coach)
        # אברם גרנט: games 4(2-0), 6(1-0) = 2
        # פאולו סוזה: games 9(0-0), 10(3-0) = 2
        assert clean["אברם גרנט"] == 2
        assert clean["פאולו סוזה"] == 2


class TestCoachesPercentages:
    def test_most_winner_coach_by_percentage(self, maccabi_games):
        result = maccabi_games.coaches.most_winner_coach_by_percentage()
        # Returns list of (coach_name - games, percentage)
        assert len(result) == 2
        result_dict = dict(result)
        # אברם גרנט: 4/6 = 66.67%
        assert result_dict["אברם גרנט - 6"] == 66.67

    def test_most_winner_coach_by_percentage_with_minimum(self, maccabi_games):
        result = maccabi_games.coaches.most_winner_coach_by_percentage(minimum_games=5)
        # Only אברם גרנט has >= 5 games
        assert len(result) == 1


class TestCoachesPerGame:
    def test_most_goals_for_maccabi_per_game(self, maccabi_games):
        result = dict(maccabi_games.coaches.most_goals_for_maccabi_per_game_coach())
        # אברם גרנט: 11/6 = 1.83
        assert result["אברם גרנט - 6"] == 1.83
        # פאולו סוזה: 6/4 = 1.5
        assert result["פאולו סוזה - 4"] == 1.5
