"""Opponent filtering tests using synthetic fixture."""


def test__all_opponents_games_when_filtered__equal_to_total_games_count(maccabi_games):
    total_games_count = len(maccabi_games)

    opponents_games_count = sum(len(maccabi_games.get_games_against_team(opponent)) for opponent in
                                maccabi_games.available_opponents)

    assert total_games_count == opponents_games_count
