"""Tests for MaccabiGamesComebacksStats."""
# Game 5 is the comeback game: Maccabi down 0-2, wins 4-2
# Goal timeline: opponent 10', opponent 20', maccabi 50', maccabi 60', maccabi 70', maccabi 80'
# Max opponent advantage: -2 (after goals at 10' and 20')


class TestComebacks:
    def test_won_from_exactly_two_goal_diff(self, maccabi_games):
        comebacks = maccabi_games.comebacks.won_from_exactly_two_goal_diff()
        assert len(comebacks) == 1
        assert comebacks.games[0].date.month == 12  # Game 5: Dec 2019

    def test_won_from_exactly_one_goal_diff(self, maccabi_games):
        # No game has exactly 1-goal comeback (game 5 is 2-goal)
        comebacks = maccabi_games.comebacks.won_from_exactly_one_goal_diff()
        assert len(comebacks) == 0

    def test_won_from_any_goal_diff(self, maccabi_games):
        comebacks = maccabi_games.comebacks.won_from_any_goal_diff()
        assert len(comebacks) == 1

    def test_total_comebacks_count(self, maccabi_games):
        assert maccabi_games.comebacks.total_comebacks_count == 1

    def test_games_with_potential_comebacks(self, maccabi_games):
        # Games where opponent had > 1 goal advantage at some point
        potential = maccabi_games.comebacks.games_with_potential_comebacks()
        assert len(potential) >= 1  # At least game 5

    def test_games_with_potential_comebacks_that_maccabi_didnt_win(self, maccabi_games):
        # Game 5 is a comeback (maccabi won), so it shouldn't be here
        # Game 2: 0-2 loss, opponent had 2-goal advantage -> potential but maccabi didn't win
        didnt_win = maccabi_games.comebacks.games_with_potential_comebacks_that_maccabi_didnt_win()
        assert len(didnt_win) >= 1

    def test_tie_from_exactly_one_goal_diff(self, maccabi_games):
        # Game 3: 1-1 tie, opponent scored first (minute 20), maccabi equalized (minute 80)
        ties = maccabi_games.comebacks.tie_from_exactly_one_goal_diff()
        assert len(ties) == 1

    def test_tie_from_exactly_two_goal_diff(self, maccabi_games):
        ties = maccabi_games.comebacks.tie_from_exactly_two_goal_diff()
        assert len(ties) == 0


class TestNoComebacksInSubset:
    def test_no_comebacks_in_home_wins_only(self, maccabi_games):
        home_wins = maccabi_games.home_games.maccabi_wins
        # Game 5 IS a home win and a comeback, so this should still find it
        comebacks = home_wins.comebacks.won_from_any_goal_diff()
        assert len(comebacks) == 1
