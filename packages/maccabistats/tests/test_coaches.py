"""Tests for MaccabiGamesCoachesStats."""


class TestCoachesBasicStats:
    def test_most_trained_coach(self, maccabi_games):
        trained = dict(maccabi_games.coaches.most_trained_coach)
        assert trained["מאמן_א"] == 6
        assert trained["מאמן_ב"] == 4

    def test_most_winner_coach(self, maccabi_games):
        winners = dict(maccabi_games.coaches.most_winner_coach)
        # מאמן_א: wins in games 1,4,5,6 = 4
        # מאמן_ב: wins in games 7,10 = 2
        assert winners["מאמן_א"] == 4
        assert winners["מאמן_ב"] == 2

    def test_most_loser_coach(self, maccabi_games):
        losers = dict(maccabi_games.coaches.most_loser_coach)
        # מאמן_א: loss in game 2 = 1
        # מאמן_ב: loss in game 8 = 1
        assert losers["מאמן_א"] == 1
        assert losers["מאמן_ב"] == 1

    def test_most_goals_for_maccabi_coach(self, maccabi_games):
        goals = dict(maccabi_games.coaches.most_goals_for_maccabi_coach)
        # מאמן_א: 3+0+1+2+4+1 = 11
        # מאמן_ב: 2+1+0+3 = 6
        assert goals["מאמן_א"] == 11
        assert goals["מאמן_ב"] == 6

    def test_most_goals_against_maccabi_coach(self, maccabi_games):
        goals_against = dict(maccabi_games.coaches.most_goals_against_maccabi_coach)
        # מאמן_א: 1+2+1+0+2+0 = 6
        # מאמן_ב: 1+3+0+0 = 4
        assert goals_against["מאמן_א"] == 6
        assert goals_against["מאמן_ב"] == 4

    def test_most_clean_sheet_games_coach(self, maccabi_games):
        clean = dict(maccabi_games.coaches.most_clean_sheet_games_coach)
        # מאמן_א: games 4(2-0), 6(1-0) = 2
        # מאמן_ב: games 9(0-0), 10(3-0) = 2
        assert clean["מאמן_א"] == 2
        assert clean["מאמן_ב"] == 2


class TestCoachesPercentages:
    def test_most_winner_coach_by_percentage(self, maccabi_games):
        result = maccabi_games.coaches.most_winner_coach_by_percentage()
        # Returns list of (coach_name - games, percentage)
        assert len(result) == 2
        result_dict = dict(result)
        # מאמן_א: 4/6 = 66.67%
        assert result_dict["מאמן_א - 6"] == 66.67

    def test_most_winner_coach_by_percentage_with_minimum(self, maccabi_games):
        result = maccabi_games.coaches.most_winner_coach_by_percentage(minimum_games=5)
        # Only מאמן_א has >= 5 games
        assert len(result) == 1


class TestCoachesPerGame:
    def test_most_goals_for_maccabi_per_game(self, maccabi_games):
        result = dict(maccabi_games.coaches.most_goals_for_maccabi_per_game_coach())
        # מאמן_א: 11/6 = 1.83
        assert result["מאמן_א - 6"] == 1.83
        # מאמן_ב: 6/4 = 1.5
        assert result["מאמן_ב - 4"] == 1.5
