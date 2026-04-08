"""Tests for MaccabiGamesImportantGoalsStats."""


class TestImportantGoals:
    def test_top_scorers_for_advantage(self, maccabi_games):
        # Goals that put maccabi in the lead (diff goes from <=0 to 1)
        scorers = dict(maccabi_games.important_goals.get_top_scorers_for_advantage())
        assert scorers["אבי נמני"] == 4
        assert scorers["ערן זהבי"] == 1

    def test_top_scorers_default_range(self, maccabi_games):
        # Goals scored when diff is between -2 and +1
        scorers = dict(maccabi_games.important_goals.get_top_scorers())
        assert scorers["אבי נמני"] == 7
        assert scorers["ערן זהבי"] == 1

    def test_top_scorers_in_last_minutes(self, maccabi_games):
        # Goals after minute 75
        late_scorers = dict(maccabi_games.important_goals.get_top_scorers_in_last_minutes(from_minute=75))
        # אבי נמני: penalty at 80' in game 3, ערן זהבי: goal at 80' in game 5 and 85' in game 6
        assert "אבי נמני" in late_scorers
        assert "ערן זהבי" in late_scorers

    def test_no_important_goals_in_blowout_range(self, maccabi_games):
        # Goals when maccabi is already leading by 5+ should be empty
        blowout = maccabi_games.important_goals.get_top_scorers(
            minimum_diff_for_maccabi=5, maximum_diff_for_maccabi=10)
        assert len(blowout) == 0
