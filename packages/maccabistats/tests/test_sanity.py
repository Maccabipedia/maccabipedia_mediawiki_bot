"""Sanity tests using synthetic fixture (converted from live API tests)."""


def test_can_access_all_games_and_maccabi_teams_object__sanity(maccabi_games):
    for game in maccabi_games:
        for maccabi_player in game.maccabi_team.players:
            assert maccabi_player.name


def test_calculate_general_summary__should_work_without_exceptions(maccabi_games):
    assert maccabi_games.get_summary()


def test_calculate_players_events_summary__should_work_without_exceptions(maccabi_games):
    assert str(maccabi_games.players_events_summary)
