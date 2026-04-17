"""Parser tests for crawl_basket_co_il."""
from datetime import datetime
from pathlib import Path

from maccabipediabot.basketball.crawl_basket_co_il import (
    GameDiscoveryMeta,
    parse_game_page,
)

FIXTURES = Path(__file__).parent / "fixtures"


def _meta() -> GameDiscoveryMeta:
    """Game 26383: Hapoel Holon (home) vs Maccabi Tel-Aviv (away), 30/05/2025, semi-final."""
    return GameDiscoveryMeta(
        game_id=26383,
        scrape_url="https://basket.co.il/game-zone.asp?GameId=26383",
        page_title="כדורסל:30-05-2025 הפועל חולון נגד מכבי תל אביב - ליגת העל",
        game_date=datetime(2025, 5, 30, 20, 30),
        is_maccabi_home=False,
        opponent_name="הפועל חולון",
        home_team_score=73,
        away_team_score=85,
        competition="ליגת העל",
    )


def _read_fixture() -> str:
    return (FIXTURES / "basket_co_il_game_26383.html").read_bytes().decode("utf-8")


def test_parse_game_page_extracts_stadium():
    game = parse_game_page(_read_fixture(), _meta())
    assert "טוטו" in game.arena  # "היכל טוטו, חולון"


def test_parse_game_page_extracts_referees():
    game = parse_game_page(_read_fixture(), _meta())
    assert game.referee
    assert isinstance(game.referee_assistants, list)
    assert len(game.referee_assistants) >= 1


def test_parse_game_page_extracts_per_quarter_scores():
    game = parse_game_page(_read_fixture(), _meta())
    # Maccabi was AWAY; per the spec probe the away row was [17, 27, 20, 21]
    assert game.first_quarter_maccabi_points == 17
    assert game.second_quarter_maccabi_points == 27
    assert game.third_quarter_maccabi_points == 20
    assert game.fourth_quarter_maccabi_points == 21
    # Hapoel Holon HOME row was [20, 17, 22, 14]
    assert game.first_quarter_opponent_points == 20
    assert game.fourth_quarter_opponent_points == 14


def test_parse_game_page_extracts_coaches():
    game = parse_game_page(_read_fixture(), _meta())
    assert game.maccabi_coach
    assert game.opponent_coach


def test_parse_game_page_extracts_player_lists():
    game = parse_game_page(_read_fixture(), _meta())
    # Real box scores list full rosters; accept 8+ to tolerate minor fixture noise.
    assert len(game.maccabi_players) >= 8
    assert len(game.opponent_players) >= 8
    assert any(p.name and p.total_points > 0 for p in game.maccabi_players)


def test_parse_game_page_starting_five_matches_star_only():
    """Regression guard: is_starting_five must be true only when the HE cell is '*'."""
    game = parse_game_page(_read_fixture(), _meta())
    starters = [p for p in game.maccabi_players if p.is_starting_five]
    assert len(starters) == 5, f"expected exactly 5 starters, got {len(starters)}"


def test_parse_game_page_raises_when_header_missing():
    """A page without #wrap_inner_3 should raise — silent stub-uploads are unacceptable."""
    import pytest
    with pytest.raises(RuntimeError, match="#wrap_inner_3"):
        parse_game_page("<html><body>maintenance page</body></html>", _meta())


def test_parse_game_page_raises_when_box_score_tables_missing():
    """A page with header + scores but missing player tables should raise, not return empties."""
    import pytest
    minimal = """
    <div id="wrap_inner_3">
      <h4></h4>
      <h5>אולם, עיר</h5>
      <h6>שופטים: ראשי</h6>
    </div>
    <table class="stats_tbl categories">
      <tr><td></td><td>1</td><td>2</td><td>3</td><td>4</td></tr>
      <tr><td>home</td><td>20</td><td>20</td><td>20</td><td>20</td></tr>
      <tr><td>away</td><td>20</td><td>20</td><td>20</td><td>20</td></tr>
    </table>
    <table class="stats_tbl categories">
      <tr><td>filler</td></tr>
    </table>
    """
    with pytest.raises(RuntimeError, match="fewer than 4 stats_tbl"):
        parse_game_page(minimal, _meta())


def test_parse_game_page_sets_team_names():
    game = parse_game_page(_read_fixture(), _meta())
    assert game.home_team_name == "הפועל חולון"
    assert game.away_team_name == "מכבי תל אביב"


# ---------------------------------------------------------------------------
# Live discovery (integration — hits basket.co.il)
# ---------------------------------------------------------------------------

import pytest

from maccabipediabot.basketball.crawl_basket_co_il import discover_games_latest_season


@pytest.mark.integration
def test_discover_games_latest_season_hits_live_api():
    games = discover_games_latest_season(limit=5)
    assert isinstance(games, list)
    # During the off-season this could be empty; only assert structure when populated.
    for meta in games:
        assert meta.scrape_url.startswith("https://basket.co.il/game-zone.asp?GameId=")
        assert meta.opponent_name
        assert meta.competition
