"""Tests for gamesbot_basketball: render + upload pipeline contracts."""
from datetime import datetime

import pytest

from maccabipediabot.basketball.basketball_game import BasketballGame, PlayerSummary
from maccabipediabot.basketball.gamesbot_basketball import (
    render_basketball_game_to_wikitext,
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
    text = render_basketball_game_to_wikitext(_game())
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
    def __init__(self, title: str, exists: bool = False, save_raises: bool = False):
        self._title = title
        self._exists = exists
        self._save_raises = save_raises
        self.text = ""
        self.saved = False

    def title(self) -> str:
        return self._title

    def exists(self) -> bool:
        return self._exists

    def save(self, summary: str = "") -> None:
        if self._save_raises:
            raise RuntimeError("simulated edit conflict")
        self.saved = True


@pytest.fixture
def patched_pipeline(monkeypatch):
    """Stub get_site, pywikibot.Page, and prettify so the upload pipeline can
    run end-to-end against in-memory fakes."""
    pages: dict[str, _FakePage] = {}

    def fake_page(_site, title):
        return pages.setdefault(title, _FakePage(title))

    from maccabipediabot.basketball import gamesbot_basketball
    monkeypatch.setattr(gamesbot_basketball, "get_site", lambda: object())
    monkeypatch.setattr(gamesbot_basketball.pw, "Page", fake_page)
    monkeypatch.setattr(gamesbot_basketball, "prettify_game_page_main_template", lambda page: None)
    return pages


def test_dry_run_skips_save(patched_pipeline):
    upload_basketball_games_to_maccabipedia([_game()], skip_existing=False, dry_run=True)
    assert all(not page.saved for page in patched_pipeline.values())


def test_live_run_saves(patched_pipeline):
    upload_basketball_games_to_maccabipedia([_game()], skip_existing=False, dry_run=False)
    assert all(page.saved for page in patched_pipeline.values())


def test_failure_propagates_immediately(monkeypatch):
    """Per the fast-fail contract: a save failure on one game just propagates;
    no aggregation, no try/except wrapping."""
    pages: dict[str, _FakePage] = {}

    def fake_page(_site, title):
        return pages.setdefault(title, _FakePage(title, save_raises=True))

    from maccabipediabot.basketball import gamesbot_basketball
    monkeypatch.setattr(gamesbot_basketball, "get_site", lambda: object())
    monkeypatch.setattr(gamesbot_basketball.pw, "Page", fake_page)
    monkeypatch.setattr(gamesbot_basketball, "prettify_game_page_main_template", lambda page: None)

    with pytest.raises(RuntimeError, match="simulated edit conflict"):
        upload_basketball_games_to_maccabipedia([_game()], skip_existing=False, dry_run=False)
