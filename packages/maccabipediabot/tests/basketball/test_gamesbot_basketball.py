"""Tests for gamesbot_basketball: render + upload pipeline contracts."""
import sys
import types
from datetime import datetime

import pytest

from maccabipediabot.basketball.basketball_game import BasketballGame, PlayerSummary
from maccabipediabot.basketball.gamesbot_basketball import (
    generate_page_name_from_game,
    render_basketball_game_to_wiki,
    upload_basketball_games_to_maccabipedia,
)


def _player(name: str, points: int) -> PlayerSummary:
    return PlayerSummary(
        name=name, is_starting_five=True, total_points=points,
        field_goals_attempts=10, field_goals_scored=4,
        three_scores_attempts=5, three_scores_scored=2,
        free_throws_attempts=4, free_throws_scored=4,
    )


def _game(game_date: datetime = datetime(2025, 1, 15, 20, 30)) -> BasketballGame:
    return BasketballGame(
        home_team_name="מכבי תל אביב", away_team_name="הפועל ירושלים",
        competition="ליגת העל", fixture="מחזור 5",
        game_date=game_date, home_team_score=92, away_team_score=85,
        game_url=["https://basket.co.il/game-zone.asp?GameId=99999"],
        season="2024/25", arena="היכל מנורה מבטחים", crowd=11000,
        referee="עומר אסתרון", referee_assistants=["דן ילון", "אדר פאר"],
        maccabi_coach="עודד קטש", opponent_coach="יונתן אלון",
        maccabi_players=[_player("טל ברודי", 28), _player("מוטל'ה שפיגלר", 18)],
        opponent_players=[_player("ערן זהבי", 22)],
        first_quarter_maccabi_points=24, second_quarter_maccabi_points=21,
        third_quarter_maccabi_points=25, fourth_quarter_maccabi_points=22,
    )


def test_render_full_template_includes_all_meta_fields():
    """Single check covering: template wrapper, iconic player names rendered,
    referees joined with ", ", per-quarter scores, arena, crowd, source URL label."""
    text = render_basketball_game_to_wiki(_game())
    assert text.startswith("{{משחק כדורסל")
    assert text.endswith("}}")
    assert "טל ברודי" in text and "מוטל'ה שפיגלר" in text
    assert "עומר אסתרון" in text
    assert "דן ילון, אדר פאר" in text
    assert "נקודות מכבי רבע1=24" in text
    assert "נקודות מכבי רבע4=22" in text
    assert "אולם=היכל מנורה מבטחים" in text
    assert "כמות קהל=11000" in text
    assert "עמוד המשחק באתר מנהלת ליגת העל בכדורסל" in text


# ---------------------------------------------------------------------------
# Upload pipeline — exercised without touching pywikibot or the network.
# ---------------------------------------------------------------------------

class _FakePage:
    def __init__(self, title: str, save_raises: bool = False):
        self._title = title
        self._save_raises = save_raises
        self.text = ""
        self.saved = False

    def title(self) -> str:
        return self._title

    def exists(self) -> bool:
        return False

    def save(self, summary: str = "") -> None:
        if self._save_raises:
            raise RuntimeError("simulated edit conflict")
        self.saved = True


class _FakeSite:
    def __init__(self, pages: dict[str, _FakePage] | None = None):
        self._pages = pages or {}

    def get_or_create(self, title: str) -> _FakePage:
        return self._pages.setdefault(title, _FakePage(title))


@pytest.fixture
def fake_pipeline(monkeypatch):
    """Patch out pywikibot login, page constructor, batch existence, and prettify
    so upload_basketball_games_to_maccabipedia can run against fake objects."""
    site = _FakeSite()
    from maccabipediabot.basketball import gamesbot_basketball
    monkeypatch.setattr(gamesbot_basketball, "_site", lambda: site)
    monkeypatch.setattr(gamesbot_basketball.pw, "Page", lambda s, t: s.get_or_create(t))
    monkeypatch.setattr(gamesbot_basketball, "batch_check_existence", lambda s, titles: set())
    prettify_module = types.ModuleType("maccabipediabot.common.prettify_games_pages")
    prettify_module.prettify_game_page_main_template = lambda page: None
    sys.modules["maccabipediabot.common.prettify_games_pages"] = prettify_module
    return site


def test_dry_run_skips_save(fake_pipeline):
    upload_basketball_games_to_maccabipedia([_game()], skip_existing=False, dry_run=True)
    assert all(not page.saved for page in fake_pipeline._pages.values())


def test_live_run_saves(fake_pipeline):
    upload_basketball_games_to_maccabipedia([_game()], skip_existing=False, dry_run=False)
    assert all(page.saved for page in fake_pipeline._pages.values())


def test_per_game_failure_isolated_and_aggregated(monkeypatch):
    """One bad game must not block the others; failures aggregate into one raise."""
    bad_game = _game(game_date=datetime(2025, 1, 15, 20, 30))
    good_game = _game(game_date=datetime(2025, 2, 16, 20, 30))
    bad_title = generate_page_name_from_game(bad_game)
    good_title = generate_page_name_from_game(good_game)

    site = _FakeSite({
        bad_title: _FakePage(bad_title, save_raises=True),
        good_title: _FakePage(good_title),
    })
    from maccabipediabot.basketball import gamesbot_basketball
    monkeypatch.setattr(gamesbot_basketball, "_site", lambda: site)
    monkeypatch.setattr(gamesbot_basketball.pw, "Page", lambda s, t: s.get_or_create(t))
    monkeypatch.setattr(gamesbot_basketball, "batch_check_existence", lambda s, titles: set())
    prettify_module = types.ModuleType("maccabipediabot.common.prettify_games_pages")
    prettify_module.prettify_game_page_main_template = lambda page: None
    sys.modules["maccabipediabot.common.prettify_games_pages"] = prettify_module

    with pytest.raises(RuntimeError, match="1/2 basketball games failed"):
        upload_basketball_games_to_maccabipedia(
            [bad_game, good_game], skip_existing=False, dry_run=False,
        )
    assert site._pages[good_title].saved is True
