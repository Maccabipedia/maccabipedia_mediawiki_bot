"""Unit tests for sync_navigation_categories pure functions."""
from unittest.mock import MagicMock

import pytest

from maccabipediabot.maintenance.sync_navigation_categories import (
    PageState,
    ParsedMatch,
    build_canonical_wikitext,
    classify_page_text,
    discover_matches,
    parse_category_title,
    process_page,
)


class TestParseCategoryTitle:
    def test_trophy_players(self):
        result = parse_category_title("שחקני כדורגל שזכו ב-3 אליפויות")
        assert result == ParsedMatch(
            kind="trophy",
            sport="כדורגל",
            role="players",
            n=3,
            trophy_type="אליפויות",
        )

    def test_trophy_staff(self):
        result = parse_category_title("אנשי צוות כדורסל שזכו ב-19 תארים")
        assert result == ParsedMatch(
            kind="trophy",
            sport="כדורסל",
            role="staff",
            n=19,
            trophy_type="תארים",
        )

    def test_trophy_with_multi_word_type(self):
        result = parse_category_title("שחקני כדורסל שזכו ב-1 הגביע הבין יבשתי")
        assert result == ParsedMatch(
            kind="trophy",
            sport="כדורסל",
            role="players",
            n=1,
            trophy_type="הגביע הבין יבשתי",
        )

    def test_seasons_players(self):
        result = parse_category_title("שחקני כדורגל ששיחקו 5 עונות במכבי")
        assert result == ParsedMatch(
            kind="seasons",
            sport="כדורגל",
            role="players",
            n=5,
            trophy_type=None,
        )

    def test_seasons_staff(self):
        result = parse_category_title("אנשי צוות כדורעף שהיו 7 עונות במכבי")
        assert result == ParsedMatch(
            kind="seasons",
            sport="כדורעף",
            role="staff",
            n=7,
            trophy_type=None,
        )

    def test_unrelated_returns_none(self):
        assert parse_category_title("קטגוריה:משחקי כדורגל") is None
        assert parse_category_title("שחקני כדורגל") is None

    def test_unknown_sport_returns_none(self):
        assert parse_category_title("שחקני קוקיה שזכו ב-1 אליפויות") is None


class TestBuildCanonicalWikitext:
    def test_trophy_players(self):
        match = ParsedMatch(
            kind="trophy", sport="כדורגל", role="players", n=3, trophy_type="אליפויות"
        )
        assert build_canonical_wikitext(match) == (
            "{{ניווט קטגוריות זכיה בתארים |ענף=כדורגל |תואר=אליפויות}}"
        )

    def test_trophy_staff(self):
        match = ParsedMatch(
            kind="trophy", sport="כדורסל", role="staff", n=19, trophy_type="תארים"
        )
        assert build_canonical_wikitext(match) == (
            "{{ניווט קטגוריות זכיה בתארים |ענף=כדורסל |תואר=תארים |האם אנשי צוות=כן}}"
        )

    def test_seasons_players(self):
        match = ParsedMatch(
            kind="seasons", sport="כדורגל", role="players", n=5, trophy_type=None
        )
        assert build_canonical_wikitext(match) == (
            "{{ניווט קטגוריות עונות במכבי |ענף=כדורגל}}"
        )

    def test_seasons_staff(self):
        match = ParsedMatch(
            kind="seasons", sport="כדורעף", role="staff", n=7, trophy_type=None
        )
        assert build_canonical_wikitext(match) == (
            "{{ניווט קטגוריות עונות במכבי |ענף=כדורעף |האם אנשי צוות=כן}}"
        )


class TestClassifyPageText:
    @pytest.fixture
    def trophy_match(self):
        return ParsedMatch(
            kind="trophy",
            sport="כדורגל",
            role="players",
            n=3,
            trophy_type="אליפויות",
        )

    def test_canonical_exact(self, trophy_match):
        text = "{{ניווט קטגוריות זכיה בתארים |ענף=כדורגל |תואר=אליפויות}}"
        assert classify_page_text(text, trophy_match) == PageState.CANONICAL

    def test_canonical_with_extra_whitespace(self, trophy_match):
        text = "  {{ניווט קטגוריות זכיה בתארים  |ענף=כדורגל  |תואר=אליפויות}}\n"
        assert classify_page_text(text, trophy_match) == PageState.CANONICAL

    def test_canonical_with_trailing_newline(self, trophy_match):
        text = "{{ניווט קטגוריות זכיה בתארים |ענף=כדורגל |תואר=אליפויות}}\n"
        assert classify_page_text(text, trophy_match) == PageState.CANONICAL

    def test_empty_page(self, trophy_match):
        assert classify_page_text("", trophy_match) == PageState.EMPTY
        assert classify_page_text("   \n  ", trophy_match) == PageState.EMPTY

    def test_stub_boilerplate(self, trophy_match):
        text = (
            "זהו דף קטגוריה.\n"
            'כאן מופיעים כל הדפים בקטגוריה "שחקני כדורגל שזכו ב-3 אליפויות"…'
        )
        assert classify_page_text(text, trophy_match) == PageState.STUB

    def test_other_content_warned(self, trophy_match):
        text = "Some hand-curated content about this category."
        assert classify_page_text(text, trophy_match) == PageState.OTHER

    def test_canonical_with_wrong_params_is_other(self, trophy_match):
        text = "{{ניווט קטגוריות זכיה בתארים |ענף=כדורגל |תואר=גביעי מדינה}}"
        assert classify_page_text(text, trophy_match) == PageState.OTHER

    def test_seasons_canonical(self):
        match = ParsedMatch(
            kind="seasons", sport="כדורסל", role="staff", n=7, trophy_type=None
        )
        text = "{{ניווט קטגוריות עונות במכבי |ענף=כדורסל |האם אנשי צוות=כן}}"
        assert classify_page_text(text, match) == PageState.CANONICAL


def _fake_cat(title_str: str) -> MagicMock:
    cat = MagicMock()
    cat.title.return_value = title_str
    return cat


class TestDiscoverMatches:
    def test_discovers_and_filters(self):
        site = MagicMock()
        prefix_to_titles = {
            "שחקני ": [
                "שחקני כדורגל שזכו ב-3 אליפויות",
                "שחקני כדורגל ששיחקו 5 עונות במכבי",
                "שחקני קוקיה שזכו ב-1 אליפויות",  # unknown sport — filtered
                "שחקני כדורגל",  # doesn't match any pattern — filtered
            ],
            "אנשי צוות ": [
                "אנשי צוות כדורסל שזכו ב-19 תארים",
                "אנשי צוות כדורעף שהיו 7 עונות במכבי",
            ],
        }

        def fake_allcategories(prefix: str):
            return [_fake_cat(t) for t in prefix_to_titles[prefix]]

        site.allcategories.side_effect = fake_allcategories

        matches = list(discover_matches(site))

        assert len(matches) == 4
        kinds = {(m.kind, m.sport, m.role, m.n) for _title, m in matches}
        assert kinds == {
            ("trophy", "כדורגל", "players", 3),
            ("seasons", "כדורגל", "players", 5),
            ("trophy", "כדורסל", "staff", 19),
            ("seasons", "כדורעף", "staff", 7),
        }

    def test_sport_filter(self):
        site = MagicMock()
        site.allcategories.return_value = [
            _fake_cat("שחקני כדורגל שזכו ב-3 אליפויות"),
            _fake_cat("שחקני כדורסל שזכו ב-3 אליפויות"),
        ]
        matches = list(discover_matches(site, sport_filter="כדורגל"))
        # allcategories.return_value is shared across both prefix calls;
        # filter keeps only כדורגל. Two prefixes × one matching item = 2 results.
        assert len(matches) == 2
        for _title, match in matches:
            assert match.sport == "כדורגל"


class TestProcessPage:
    @pytest.fixture
    def trophy_match(self):
        return ParsedMatch(
            kind="trophy",
            sport="כדורגל",
            role="players",
            n=3,
            trophy_type="אליפויות",
        )

    def test_skip_canonical(self, trophy_match):
        site = MagicMock()
        page = MagicMock()
        page.text = "{{ניווט קטגוריות זכיה בתארים |ענף=כדורגל |תואר=אליפויות}}"
        action = process_page(site, page, trophy_match, dry_run=False)
        assert action == "skip"
        page.save.assert_not_called()

    def test_install_on_stub(self, trophy_match):
        site = MagicMock()
        page = MagicMock()
        page.text = "זהו דף קטגוריה.\nכאן מופיעים כל הדפים בקטגוריה..."
        action = process_page(site, page, trophy_match, dry_run=False)
        assert action == "install"
        assert page.text == (
            "{{ניווט קטגוריות זכיה בתארים |ענף=כדורגל |תואר=אליפויות}}"
        )
        page.save.assert_called_once()

    def test_install_on_empty(self, trophy_match):
        site = MagicMock()
        page = MagicMock()
        page.text = ""
        action = process_page(site, page, trophy_match, dry_run=False)
        assert action == "install"
        page.save.assert_called_once()

    def test_warn_on_other(self, trophy_match):
        site = MagicMock()
        page = MagicMock()
        page.text = "Some hand-curated description."
        action = process_page(site, page, trophy_match, dry_run=False)
        assert action == "warn"
        page.save.assert_not_called()

    def test_dry_run_does_not_save(self, trophy_match):
        site = MagicMock()
        page = MagicMock()
        page.text = ""
        action = process_page(site, page, trophy_match, dry_run=True)
        assert action == "install"
        page.save.assert_not_called()
