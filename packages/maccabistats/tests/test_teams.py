"""Tests for MaccabiGamesTeamsStats."""


class TestTeamsStats:
    def test_teams_ordered_by_games_played(self, maccabi_games):
        teams = dict(maccabi_games.teams.teams_ordered_by_games_played())
        assert teams['מכבי ת"א אלי פוקס'] == 3
        assert teams['מכבי ת"א שחר'] == 2
        assert teams['מכבי ת"א עודד'] == 2
        assert teams['מכבי ת"א אלדד'] == 2
        assert teams["קבוצה זרה"] == 1

    def test_teams_ordered_by_maccabi_wins(self, maccabi_games):
        teams = dict(maccabi_games.teams.teams_ordered_by_maccabi_wins())
        # מכבי ת"א שחר: 2 wins (games 1, 5)
        assert teams['מכבי ת"א שחר'] == 2

    def test_teams_ordered_by_maccabi_losses(self, maccabi_games):
        teams = dict(maccabi_games.teams.teams_ordered_by_maccabi_losses())
        assert teams['מכבי ת"א עודד'] == 1
        assert teams['מכבי ת"א אלי פוקס'] == 1

    def test_teams_ordered_by_clean_sheets(self, maccabi_games):
        teams = dict(maccabi_games.teams.teams_ordered_by_maccabi_clean_sheets_count())
        # מכבי ת"א אלדד: 2 clean sheets (game 4: 2-0, game 9: 0-0)
        assert teams['מכבי ת"א אלדד'] == 2

    def test_teams_ordered_by_wins_minus_losses(self, maccabi_games):
        teams = dict(maccabi_games.teams.teams_ordered_by_wins_minus_losses())
        # מכבי ת"א שחר: 2 wins - 0 losses = 2
        assert teams['מכבי ת"א שחר'] == 2
        # מכבי ת"א עודד: 1 win - 1 loss = 0
        assert teams['מכבי ת"א עודד'] == 0

    def test_teams_with_minimum_games_filter(self, maccabi_games):
        teams = maccabi_games.teams.teams_ordered_by_games_played(minimum_games_against_team=3)
        assert len(teams) == 1  # Only מכבי ת"א אלי פוקס has >= 3 games
        assert teams[0][0] == 'מכבי ת"א אלי פוקס'

    def test_teams_top_count_limit(self, maccabi_games):
        teams = maccabi_games.teams.teams_ordered_by_games_played(top_teams_count=2)
        assert len(teams) == 2

    def test_teams_ordered_by_goals_diff(self, maccabi_games):
        teams = dict(maccabi_games.teams.teams_ordered_by_goals_diff())
        # מכבי ת"א שחר: (3-1)+(4-2) = +4
        assert teams['מכבי ת"א שחר'] == 4
