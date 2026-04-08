"""Integration tests that hit the live MaccabiPedia API.

Run with: uv run pytest -m integration
Skipped by default in CI.
"""
import pytest

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def maccabipedia_maccabistats():
    from maccabistats import load_from_maccabipedia_source
    return load_from_maccabipedia_source()


def test_can_access_all_games_and_maccabi_teams_object__sanity(maccabipedia_maccabistats):
    for game in maccabipedia_maccabistats:
        for maccabi_player in game.maccabi_team.players:
            assert maccabi_player.name


def test_calculate_general_summary__should_work_without_exceptions(maccabipedia_maccabistats):
    assert maccabipedia_maccabistats.get_summary()


def test_calculate_players_events_summary__should_work_without_exceptions(maccabipedia_maccabistats):
    assert str(maccabipedia_maccabistats.players_events_summary)


def test_all_opponents_games_when_filtered_equal_to_total_games_count(maccabipedia_maccabistats):
    total_games_count = len(maccabipedia_maccabistats)
    opponents_games_count = sum(
        len(maccabipedia_maccabistats.get_games_against_team(opponent))
        for opponent in maccabipedia_maccabistats.available_opponents
    )
    assert total_games_count == opponents_games_count


def test_export_all_formats(tmp_path, maccabipedia_maccabistats):
    maccabipedia_maccabistats.export.export_everything_json(folder_path=tmp_path)
    maccabipedia_maccabistats.export.export_everything_csv(folder_path=tmp_path)
