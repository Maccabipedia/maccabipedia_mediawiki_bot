"""Render tests for gamesbot_basketball."""
from datetime import datetime

from maccabipediabot.basketball.basketball_game import BasketballGame, PlayerSummary
from maccabipediabot.basketball.gamesbot_basketball import (
    render_basketball_game_to_wiki,
)


def _player(name: str, points: int) -> PlayerSummary:
    return PlayerSummary(
        name=name,
        is_starting_five=True,
        total_points=points,
        field_goals_attempts=10,
        field_goals_scored=4,
        three_scores_attempts=5,
        three_scores_scored=2,
        free_throws_attempts=4,
        free_throws_scored=4,
    )


def _game() -> BasketballGame:
    return BasketballGame(
        home_team_name="מכבי תל אביב",
        away_team_name="הפועל ירושלים",
        competition="ליגת העל",
        fixture="מחזור 5",
        game_date=datetime(2025, 1, 15, 20, 30),
        home_team_score=92,
        away_team_score=85,
        game_url=["https://basket.co.il/game-zone.asp?GameId=99999"],
        season="2024/25",
        arena="היכל מנורה מבטחים",
        crowd=11000,
        referee="עומר אסתרון",
        referee_assistants=["דן ילון", "אדר פאר"],
        maccabi_coach="עודד קטש",
        opponent_coach="יונתן אלון",
        maccabi_players=[_player("טל ברודי", 28), _player("מוטל'ה שפיגלר", 18)],
        opponent_players=[_player("ערן זהבי", 22)],
        first_quarter_maccabi_points=24,
        second_quarter_maccabi_points=21,
        third_quarter_maccabi_points=25,
        fourth_quarter_maccabi_points=22,
    )


def test_render_uses_basketball_template_name():
    text = render_basketball_game_to_wiki(_game())
    assert text.startswith("{{משחק כדורסל")
    assert text.endswith("}}")


def test_render_includes_iconic_players():
    text = render_basketball_game_to_wiki(_game())
    assert "טל ברודי" in text
    assert "מוטל'ה שפיגלר" in text


def test_render_includes_referees_joined():
    text = render_basketball_game_to_wiki(_game())
    assert "עומר אסתרון" in text
    assert "דן ילון, אדר פאר" in text


def test_render_includes_per_quarter_scores():
    text = render_basketball_game_to_wiki(_game())
    assert "נקודות מכבי רבע1=24" in text
    assert "נקודות מכבי רבע4=22" in text


def test_render_includes_arena_and_crowd():
    text = render_basketball_game_to_wiki(_game())
    assert "אולם=היכל מנורה מבטחים" in text
    assert "כמות קהל=11000" in text


# ---------------------------------------------------------------------------
# Upload pipeline — exercise CLI / dry-run / failure-isolation contracts
# without touching pywikibot or the network.
# ---------------------------------------------------------------------------

class _FakePage:
    """Minimal pywikibot.Page stand-in for upload tests."""
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


class _FakeSite:
    """Minimal site stand-in. Returns _FakePage instances and supplies preloadpages."""
    def __init__(self, pages: dict[str, _FakePage] | None = None):
        self._pages = pages or {}

    def get(self, title: str) -> _FakePage:
        return self._pages.setdefault(title, _FakePage(title))


def _patch_pwpage(monkeypatch, site: _FakeSite):
    """pywikibot.Page(site, title) is the constructor the gamesbot uses."""
    from maccabipediabot.basketball import gamesbot_basketball
    monkeypatch.setattr(gamesbot_basketball.pw, "Page", lambda s, t: s.get(t))


def _patch_site(monkeypatch, site: _FakeSite):
    from maccabipediabot.basketball import gamesbot_basketball
    monkeypatch.setattr(gamesbot_basketball, "_site", lambda: site)


def _patch_no_existing(monkeypatch):
    from maccabipediabot.basketball import gamesbot_basketball
    monkeypatch.setattr(gamesbot_basketball, "batch_check_existence", lambda site, titles: set())


def _patch_skip_prettify(monkeypatch):
    """Stub the lazy prettify import inside handle_game so we don't trigger pywikibot."""
    import sys, types
    mod = types.ModuleType("maccabipediabot.common.prettify_games_pages")
    mod.prettify_game_page_main_template = lambda page: None
    sys.modules["maccabipediabot.common.prettify_games_pages"] = mod


def test_dry_run_does_not_save_pages(monkeypatch):
    from maccabipediabot.basketball.gamesbot_basketball import (
        upload_basketball_games_to_maccabipedia,
    )
    site = _FakeSite()
    _patch_site(monkeypatch, site)
    _patch_pwpage(monkeypatch, site)
    _patch_no_existing(monkeypatch)
    _patch_skip_prettify(monkeypatch)

    upload_basketball_games_to_maccabipedia([_game()], skip_existing=False, dry_run=True)

    pages = list(site._pages.values())
    assert len(pages) == 1
    assert pages[0].saved is False, "dry_run must not call .save()"


def test_live_run_does_save_pages(monkeypatch):
    from maccabipediabot.basketball.gamesbot_basketball import (
        upload_basketball_games_to_maccabipedia,
    )
    site = _FakeSite()
    _patch_site(monkeypatch, site)
    _patch_pwpage(monkeypatch, site)
    _patch_no_existing(monkeypatch)
    _patch_skip_prettify(monkeypatch)

    upload_basketball_games_to_maccabipedia([_game()], skip_existing=False, dry_run=False)

    pages = list(site._pages.values())
    assert pages[0].saved is True


def test_per_game_failure_isolated_and_aggregated_at_end(monkeypatch):
    """Failure on one game does not block subsequent uploads, and the function
    raises at the end with the failure list."""
    import pytest

    from maccabipediabot.basketball.gamesbot_basketball import (
        upload_basketball_games_to_maccabipedia,
        generate_page_name_from_game,
    )

    bad_game = _game()
    good_game = _game()
    # Distinguish by changing the date so they generate different page titles
    from datetime import datetime as _dt
    object.__setattr__(good_game, "game_date", _dt(2025, 2, 16, 20, 30))

    bad_title = generate_page_name_from_game(bad_game)
    good_title = generate_page_name_from_game(good_game)
    site = _FakeSite({
        bad_title: _FakePage(bad_title, save_raises=True),
        good_title: _FakePage(good_title),
    })
    _patch_site(monkeypatch, site)
    _patch_pwpage(monkeypatch, site)
    _patch_no_existing(monkeypatch)
    _patch_skip_prettify(monkeypatch)

    with pytest.raises(RuntimeError, match="1/2 basketball games failed"):
        upload_basketball_games_to_maccabipedia(
            [bad_game, good_game], skip_existing=False, dry_run=False,
        )

    # The good game must still have saved despite the bad game's failure
    assert site._pages[good_title].saved is True
