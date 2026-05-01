"""Parser tests for crawl_basket_co_il."""
import json
from datetime import datetime
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from maccabipediabot.basketball.basketball_game import BasketballGame
from maccabipediabot.basketball.crawl_basket_co_il import (
    _parse_player_rows,
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


def _player_row_html(jersey_link_html: str) -> str:
    """Minimal player table: 1 header row.row + 1 player row.row + totals row.
    The player row has 21 <td>s with the column layout _parse_player_rows expects.
    `jersey_link_html` goes in tds[0]; pass an `<a>` to simulate a linked number,
    or empty string to simulate no link."""
    cells = [f"<td>{jersey_link_html}</td>"]                       # 0: number
    cells += ['<td><a href="x">איפה לונדברג</a></td>']            # 1: name
    cells += ['<td></td>']                                         # 2: starting *
    cells += ['<td>10</td>']                                       # 3: minutes
    cells += ['<td>0</td>']                                        # 4: total points
    cells += ['<td>0/3</td>', '<td>0</td>']                        # 5,6: 2pt
    cells += ['<td>0/3</td>', '<td>0</td>']                        # 7,8: 3pt
    cells += ['<td>0/0</td>', '<td>0</td>']                        # 9,10: ft
    cells += ['<td>4</td>', '<td>0</td>']                          # 11,12: rebounds
    cells += ['<td>0</td>']                                        # 13: total rebounds (unused)
    cells += ['<td>2</td>']                                        # 14: fouls
    cells += ['<td>0</td>']                                        # 15: pad
    cells += ['<td>0</td>', '<td>1</td>', '<td>0</td>', '<td>0</td>']  # 16-19: steals, to, ast, blk
    cells += ['<td>0</td>']                                        # 20: pad to reach 21
    return f"""
    <table>
      <tr class="row"><td>header</td></tr>
      <tr class="row">{''.join(cells)}</tr>
      <tr><td>totals</td></tr>
    </table>
    """


@pytest.mark.parametrize("jersey_link_html, expected_number", [
    ('<a href="player.asp?PlayerId=1">0</a>', 0),    # jersey #0 must stay 0, not collapse to None
    ('<a href="player.asp?PlayerId=1">23</a>', 23),
    ('', None),                                       # no <a> in the cell → number unknown
])
def test_parse_player_rows_preserves_jersey_zero(jersey_link_html, expected_number):
    table = BeautifulSoup(_player_row_html(jersey_link_html), "html.parser").select_one("table")
    players = _parse_player_rows(table)
    assert len(players) == 1
    assert players[0].number == expected_number


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
