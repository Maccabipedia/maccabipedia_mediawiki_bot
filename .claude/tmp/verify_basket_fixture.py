"""Sanity check: the captured basket.co.il fixture has every element parse_game_page needs."""
from pathlib import Path
from bs4 import BeautifulSoup

html = Path("packages/maccabipediabot/tests/basketball/fixtures/basket_co_il_game_26383.html").read_bytes().decode("utf-8")
soup = BeautifulSoup(html, "html.parser")

assert soup.select_one("#wrap_inner_3") is not None, "missing #wrap_inner_3"
assert len(soup.select("table.stats_tbl.categories")) >= 2, "need 2 categories tables"
assert len(soup.select("table.stats_tbl")) >= 4, "need at least 4 stats_tbl tables"
assert "מכבי" in html, "missing Maccabi text"
print("fixture OK")
