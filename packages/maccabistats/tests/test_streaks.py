"""Tests for MaccabiGamesStreaksStats."""
# Game results in order:
# 1: W 3-1  (league)
# 2: L 0-2  (league)
# 3: T 1-1  (league)
# 4: W 2-0  (cup)
# 5: W 4-2  (league)
# 6: W 1-0  (friendly)
# 7: W 2-1  (league)
# 8: L 1-3  (league)
# 9: T 0-0  (league)
# 10: W 3-0 (league, technical)
#
# Win streaks: [1], [4,5,6,7], [10] -> longest = 4
# Loss streaks: [2], [8] -> longest = 1
# Tie streaks: [3], [9] -> longest = 1
# Unbeaten: [1] then [3,4,5,6,7] then [9,10] -> longest = 5
# Clean sheet: games 4,6 both clean but not consecutive; 9,10 consecutive -> longest = 2
# Scoring: games 1,_,3,4,5,6,7,8,_,10 -> 1 then 3-8 then 10 -> longest scoring = 6


class TestLongestStreaks:
    def test_longest_wins_streak(self, maccabi_games):
        streak = maccabi_games.streaks.get_longest_wins_streak_games()
        assert len(streak) == 4
        # Should be games 4,5,6,7
        assert streak.games[0].date.month == 11  # Game 4: Nov 2019

    def test_longest_losses_streak(self, maccabi_games):
        streak = maccabi_games.streaks.get_longest_losses_streak_games()
        assert len(streak) == 1

    def test_longest_ties_streak(self, maccabi_games):
        streak = maccabi_games.streaks.get_longest_ties_streak_games()
        assert len(streak) == 1

    def test_longest_unbeaten_streak(self, maccabi_games):
        streak = maccabi_games.streaks.get_longest_unbeaten_streak_games()
        # Games 3(T), 4(W), 5(W), 6(W), 7(W) = 5
        assert len(streak) == 5

    def test_longest_clean_sheet_streak(self, maccabi_games):
        streak = maccabi_games.streaks.get_longest_clean_sheet_games()
        # Games 9(0-0) and 10(3-0) are consecutive clean sheets
        assert len(streak) == 2

    def test_longest_score_at_least_1(self, maccabi_games):
        streak = maccabi_games.streaks.get_longest_score_at_least_games(1)
        # Games 3,4,5,6,7,8 = 6 consecutive games scoring
        assert len(streak) == 6

    def test_longest_score_exactly_0(self, maccabi_games):
        streak = maccabi_games.streaks.get_longest_score_exactly_games(0)
        # Only game 2 and game 9 have 0 goals, neither consecutive
        assert len(streak) == 1

    def test_longest_goals_from_bench(self, maccabi_games):
        streak = maccabi_games.streaks.get_longest_goals_from_bench_games()
        # Games 5 and 6 both have goals from bench, consecutive
        assert len(streak) == 2


class TestCurrentStreaks:
    def test_current_wins_streak(self, maccabi_games):
        # Last game (10) is a win, game 9 is a tie -> current win streak = 1
        streak = maccabi_games.streaks.get_current_wins_streak()
        assert len(streak) == 1

    def test_current_unbeaten_streak(self, maccabi_games):
        # Games 9(T), 10(W) -> current unbeaten = 2
        streak = maccabi_games.streaks.get_current_unbeaten_streak()
        assert len(streak) == 2

    def test_current_losses_streak(self, maccabi_games):
        # Last game is a win, so current loss streak = 0
        streak = maccabi_games.streaks.get_current_losses_streak()
        assert len(streak) == 0

    def test_current_clean_sheet_streak(self, maccabi_games):
        # Games 9 and 10 are clean sheets
        streak = maccabi_games.streaks.get_current_clean_sheet_streak()
        assert len(streak) == 2


class TestSimilarStreaks:
    def test_similar_wins_streak_length_4(self, maccabi_games):
        similar = maccabi_games.streaks.get_similar_wins_streak_by_length(minimum_streak_length=4)
        assert len(similar) == 1  # Only one streak of length >= 4

    def test_similar_wins_streak_length_1(self, maccabi_games):
        similar = maccabi_games.streaks.get_similar_wins_streak_by_length(minimum_streak_length=1)
        # Streaks: [1], [4,5,6,7], [10] = 3 streaks of length >= 1
        assert len(similar) == 3

    def test_similar_unbeaten_streak(self, maccabi_games):
        similar = maccabi_games.streaks.get_similar_unbeaten_streak_by_length(minimum_streak_length=2)
        # [3,4,5,6,7]=5 and [9,10]=2
        assert len(similar) == 2


class TestScoreDiffStreaks:
    def test_longest_score_diff_at_least_1(self, maccabi_games):
        # Consecutive games with score diff >= 1 (maccabi wins by at least 1)
        streak = maccabi_games.streaks.get_longest_score_diff_at_least_games(1)
        # Games 4(+2), 5(+2), 6(+1), 7(+1) = 4
        assert len(streak) == 4

    def test_longest_scored_against_not_more_than_0(self, maccabi_games):
        # Same as clean sheet streak
        streak = maccabi_games.streaks.get_longest_scored_against_maccabi_not_more_than_games(0)
        assert len(streak) == 2


class TestEmptyStreaks:
    def test_empty_games_streak(self):
        from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats
        from conftest import mock_players_data
        empty = MaccabiGamesStats([], players_data=mock_players_data())
        streak = empty.streaks.get_longest_wins_streak_games()
        assert len(streak) == 0
