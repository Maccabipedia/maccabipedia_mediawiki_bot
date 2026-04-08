def test__all_opponents_games_when_filtered__equal_to_total_games_count(maccabipedia_maccabistats):
    total_games_count = len(maccabipedia_maccabistats)

    opponents_games_count = sum(len(maccabipedia_maccabistats.get_games_against_team(opponent)) for opponent in
                                maccabipedia_maccabistats.available_opponents)

    assert total_games_count == opponents_games_count
