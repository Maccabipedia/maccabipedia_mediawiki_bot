"""Tests for MaccabiGamesRefereesStats."""


class TestRefereesStats:
    def test_most_judged_referee(self, maccabi_games):
        judged = dict(maccabi_games.referees.most_judged_referee)
        # 4 referees, top one refereed 4 games
        assert len(judged) == 4
        top_ref = max(judged, key=judged.get)
        assert judged[top_ref] == 4

    def test_best_referee(self, maccabi_games):
        # best_referee counts wins per referee
        best = dict(maccabi_games.referees.best_referee)
        assert len(best) > 0

    def test_worst_referee(self, maccabi_games):
        # worst_referee counts losses per referee
        worst = dict(maccabi_games.referees.worst_referee)
        assert len(worst) > 0

    def test_best_referee_by_percentage(self, maccabi_games):
        result = maccabi_games.referees.best_referee_by_percentage
        assert len(result) > 0
        # Each entry is (referee_name - judged_count, percentage)
        for name_key, pct in result:
            assert 0 <= pct <= 100

    def test_worst_referee_by_percentage(self, maccabi_games):
        result = maccabi_games.referees.worst_referee_by_percentage
        assert len(result) > 0
        for name_key, pct in result:
            assert 0 <= pct <= 100
