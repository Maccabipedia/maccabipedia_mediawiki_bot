"""Tests for MaccabiGamesResultsStats."""


class TestResultsCounts:
    def test_total_games_count(self, maccabi_games):
        assert maccabi_games.results.total_games_count == 10

    def test_wins_count(self, maccabi_games):
        assert maccabi_games.results.wins_count == 6

    def test_losses_count(self, maccabi_games):
        assert maccabi_games.results.losses_count == 2

    def test_ties_count(self, maccabi_games):
        assert maccabi_games.results.ties_count == 2


class TestResultsPercentages:
    def test_wins_percentage(self, maccabi_games):
        assert maccabi_games.results.wins_percentage == 0.6

    def test_losses_percentage(self, maccabi_games):
        assert maccabi_games.results.losses_percentage == 0.2

    def test_ties_percentage(self, maccabi_games):
        assert maccabi_games.results.ties_percentage == 0.2


class TestGoalsStats:
    def test_total_goals_for_maccabi(self, maccabi_games):
        assert maccabi_games.results.total_goals_for_maccabi == 17

    def test_total_goals_against_maccabi(self, maccabi_games):
        assert maccabi_games.results.total_goals_against_maccabi == 10

    def test_total_goals_diff_for_maccabi(self, maccabi_games):
        assert maccabi_games.results.total_goals_diff_for_maccabi == 7

    def test_goals_ratio(self, maccabi_games):
        # 17 / 10 = 1.7
        assert maccabi_games.results.goals_ratio == 1.7


class TestCleanSheets:
    def test_clean_sheets_count(self, maccabi_games):
        # Games 4 (2-0), 6 (1-0), 9 (0-0), 10 (3-0 technical)
        assert maccabi_games.results.clean_sheets_count == 4

    def test_clean_sheets_percentage(self, maccabi_games):
        assert maccabi_games.results.clean_sheets_percentage == 0.4


class TestResultsJsonDict:
    def test_json_dict_keys(self, maccabi_games):
        d = maccabi_games.results.json_dict()
        expected_keys = {
            'total_games_count', 'wins_count', 'losses_count', 'ties_count',
            'clean_sheets_count', 'wins_percentage', 'losses_percentage',
            'ties_percentage', 'clean_sheets_percentage',
            'total_goals_for_maccabi', 'total_goals_against_maccabi',
            'total_goals_diff_for_maccabi', 'goals_ratio',
        }
        assert set(d.keys()) == expected_keys


class TestGetSummary:
    def test_get_summary_returns_dict(self, maccabi_games):
        summary = maccabi_games.get_summary()
        assert summary['games'] == 10
        assert summary['wins'] == 6
        assert summary['goals_for_maccabi'] == 17


class TestEmptyGames:
    def test_empty_results(self):
        from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats
        empty = MaccabiGamesStats([])
        assert empty.results.total_games_count == 0
        assert empty.results.wins_count == 0
