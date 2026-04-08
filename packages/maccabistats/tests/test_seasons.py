"""Tests for MaccabiGamesSeasonsStats."""
import pytest

from maccabistats.stats.maccabi_games_stats import MaccabiGamesStats

from game_fixtures import GAMES


@pytest.fixture
def fresh_games() -> MaccabiGamesStats:
    """A fresh instance per test so sort mutations don't leak between tests."""
    return MaccabiGamesStats(GAMES)


class TestSeasonsBasics:
    def test_seasons_count(self, fresh_games):
        assert len(fresh_games.seasons) == 2

    def test_seasons_getitem_by_string(self, fresh_games):
        s = fresh_games.seasons["2019/20"]
        assert len(s) == 6

    def test_seasons_getitem_by_index(self, fresh_games):
        s = fresh_games.seasons[0]
        assert len(s) > 0


class TestSeasonsSorting:
    def test_sort_by_wins_count(self, fresh_games):
        fresh_games.seasons.sort_by_wins_count()
        top_season = fresh_games.seasons[0]
        # 2019/20 has 4 wins, 2020/21 has 2 wins
        assert top_season.results.wins_count == 4

    def test_sort_by_games_count(self, fresh_games):
        fresh_games.seasons.sort_by_games_count()
        top = fresh_games.seasons[0]
        assert len(top) == 6  # 2019/20

    def test_sort_by_losses_count(self, fresh_games):
        fresh_games.seasons.sort_by_losses_count()
        top = fresh_games.seasons[0]
        assert top.results.losses_count >= 1

    def test_sort_by_total_goals_for_maccabi(self, fresh_games):
        fresh_games.seasons.sort_by_total_goals_for_maccabi()
        top = fresh_games.seasons[0]
        # 2019/20: 3+0+1+2+4+1=11, 2020/21: 2+1+0+3=6
        assert top.results.total_goals_for_maccabi == 11

    def test_sort_by_clean_sheet_count(self, fresh_games):
        fresh_games.seasons.sort_by_clean_sheet_count()
        top = fresh_games.seasons[0]
        assert top.results.clean_sheets_count >= 2

    def test_repr_after_sort(self, fresh_games):
        fresh_games.seasons.sort_by_wins_count()
        r = repr(fresh_games.seasons)
        assert "sort by wins count" in r
