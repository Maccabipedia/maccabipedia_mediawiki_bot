"""Tests for MaccabiGamesTeamsStats."""


class TestTeamsStats:
    def test_teams_ordered_by_games_played(self, maccabi_games):
        teams = maccabi_games.teams.teams_ordered_by_games_played()
        top_team_name, top_team_games = teams[0]
        # מכבי חיפה: 3 games (most played opponent)
        assert top_team_games == 3

    def test_teams_ordered_by_maccabi_wins(self, maccabi_games):
        teams = dict(maccabi_games.teams.teams_ordered_by_maccabi_wins())
        assert len(teams) > 0

    def test_teams_ordered_by_maccabi_losses(self, maccabi_games):
        teams = dict(maccabi_games.teams.teams_ordered_by_maccabi_losses())
        assert len(teams) > 0

    def test_teams_ordered_by_goals_diff(self, maccabi_games):
        teams = maccabi_games.teams.teams_ordered_by_goals_diff()
        # Returns list of (team_name, goals_diff)
        assert len(teams) > 0

    def test_teams_with_minimum_games_filter(self, maccabi_games):
        # Only teams with >= 3 games
        teams = maccabi_games.teams.teams_ordered_by_games_played(minimum_games_against_team=3)
        assert all(count >= 3 for _, count in teams)

    def test_teams_top_count_limit(self, maccabi_games):
        teams = maccabi_games.teams.teams_ordered_by_games_played(top_teams_count=2)
        assert len(teams) <= 2

    def test_teams_ordered_by_clean_sheets_count(self, maccabi_games):
        teams = dict(maccabi_games.teams.teams_ordered_by_maccabi_clean_sheets_count())
        assert len(teams) > 0

    def test_teams_ordered_by_wins_minus_losses(self, maccabi_games):
        teams = maccabi_games.teams.teams_ordered_by_wins_minus_losses()
        assert len(teams) > 0
