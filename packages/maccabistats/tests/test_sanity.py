def test_can_access_all_games_and_maccabi_teams_object__sanity(maccabipedia_maccabistats):
    # Just make sure we can iterate every game and access maccabi team object
    for game in maccabipedia_maccabistats:
        for maccabi_player in game.maccabi_team.players:
            assert maccabi_player.name


def test_calculate_general_summary__should_work_without_exceptions(maccabipedia_maccabistats):
    assert maccabipedia_maccabistats.get_summary()


def test_calculate_players_events_summary__should_work_without_exceptions(maccabipedia_maccabistats):
    assert str(maccabipedia_maccabistats.players_events_summary)
