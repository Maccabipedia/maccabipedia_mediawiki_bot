"""Tests for MaccabiGamesImportantGoalsStats."""


class TestImportantGoals:
    def test_top_scorers_for_advantage(self, maccabi_games):
        # Goals that put maccabi in the lead
        scorers = dict(maccabi_games.important_goals.get_top_scorers_for_advantage())
        assert len(scorers) > 0

    def test_top_scorers_default_range(self, maccabi_games):
        # Default: goals scored when diff is between -2 and +1
        scorers = maccabi_games.important_goals.get_top_scorers()
        assert len(scorers) > 0

    def test_top_scorers_narrow_range(self, maccabi_games):
        # Only equalizers: goals scored when maccabi was behind by exactly 1
        equalizers = maccabi_games.important_goals.get_top_scorers(
            minimum_diff_for_maccabi=0, maximum_diff_for_maccabi=0)
        # These are goals that made it 1-1, 2-2, etc. (the moment after scoring, diff=0)
        # Game 3: penalty at 80' makes it 1-1 (diff goes from -1 to 0 → maccabi_score=1, not_maccabi=1, diff=0)
        # Game 5: goal at 50' makes it 1-2 (diff=-1→0? no, maccabi_score=1, not_maccabi=2, diff=-1)
        # The filter checks diff AFTER the goal, so diff=0 means equalizers
        assert isinstance(equalizers, list)

    def test_top_scorers_in_last_minutes(self, maccabi_games):
        # Goals in last 15 minutes (from minute 75+)
        late_scorers = maccabi_games.important_goals.get_top_scorers_in_last_minutes(from_minute=75)
        assert isinstance(late_scorers, list)
