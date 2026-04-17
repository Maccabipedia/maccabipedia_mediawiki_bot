"""Parser tests for crawl_basket_co_il."""
import json
from datetime import datetime
from pathlib import Path

import pytest

from maccabipediabot.basketball.basketball_game import BasketballGame
from maccabipediabot.basketball.crawl_basket_co_il import (
    discover_games_latest_season,
    parse_game_page,
)

FIXTURES = Path(__file__).parent / "fixtures"


def _partial_game() -> BasketballGame:
    """The discovery-stage BasketballGame for fixture game 26383
    (Hapoel Holon home vs Maccabi away, 30/05/2025, semi-final game 2)."""
    return BasketballGame(
        home_team_name="הפועל חולון",
        away_team_name="מכבי תל אביב",
        competition="ליגת העל",
        fixture="",  # filled by parse_game_page
        game_date=datetime(2025, 5, 30, 20, 30),
        home_team_score=73,
        away_team_score=85,
        game_url=["https://basket.co.il/game-zone.asp?GameId=26383"],
    )


def test_parse_game_page_against_real_fixture():
    """Round-trip the captured game-zone HTML against a hand-verified expected
    BasketballGame snapshot. One assert covers everything."""
    html = (FIXTURES / "basket_co_il_game_26383.html").read_bytes().decode("utf-8")
    expected = BasketballGame.model_validate_json(
        (FIXTURES / "basket_co_il_game_26383.expected.json").read_text("utf-8")
    )
    actual = parse_game_page(html, _partial_game())
    assert actual.model_dump() == expected.model_dump()


def test_parse_game_page_raises_when_header_missing():
    with pytest.raises(RuntimeError, match="#wrap_inner_3"):
        parse_game_page("<html><body>maintenance page</body></html>", _partial_game())


def test_parse_game_page_raises_when_box_score_tables_missing():
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
    <table class="stats_tbl categories"><tr><td>filler</td></tr></table>
    """
    with pytest.raises(RuntimeError, match="fewer than 4 stats_tbl"):
        parse_game_page(minimal, _partial_game())


# ---------------------------------------------------------------------------
# Discovery (synthetic feed via monkeypatched requests.get)
# ---------------------------------------------------------------------------

def _stub_feed(monkeypatch, games: list[dict]) -> None:
    payload = [{"games": games}]
    class _Resp:
        status_code = 200
        headers = {"Content-Type": "text/html"}
        content = json.dumps(payload).encode("utf-8")
        text = "stub"
    from maccabipediabot.basketball import crawl_basket_co_il
    monkeypatch.setattr(crawl_basket_co_il.requests, "get", lambda *a, **kw: _Resp())


def _maccabi_game(**overrides) -> dict:
    base = {
        "id": 1, "team_name_eng_1": "Maccabi Tel-Aviv", "team_name_eng_2": "Hapoel Tel-Aviv",
        "score_team1": 90, "score_team2": 80, "game_date_txt": "01/01/2026",
        "game_time": "20:30", "game_type": 5,
    }
    return {**base, **overrides}


def test_discover_filters_score_edge_cases(monkeypatch):
    """0-0 = unplayed placeholder (drop). 0-N = forfeit (keep)."""
    _stub_feed(monkeypatch, [
        _maccabi_game(id=1, score_team1=0, score_team2=0),    # placeholder, drop
        _maccabi_game(id=2, score_team1=0, score_team2=20),   # forfeit, keep
        _maccabi_game(id=3, score_team1=90, score_team2=80),  # normal, keep
    ])
    discovered = discover_games_latest_season()
    # Each discovered game's URL encodes its source id; check the surviving set.
    surviving_ids = {int(game.game_url[0].rsplit("=", 1)[1]) for game in discovered}
    assert surviving_ids == {2, 3}


def test_discover_raises_on_unknown_game_type(monkeypatch):
    """Unknown game_type codes must raise so we don't silently lose a competition."""
    _stub_feed(monkeypatch, [_maccabi_game(id=1, game_type=999)])
    with pytest.raises(RuntimeError, match="unknown game_type"):
        discover_games_latest_season()
