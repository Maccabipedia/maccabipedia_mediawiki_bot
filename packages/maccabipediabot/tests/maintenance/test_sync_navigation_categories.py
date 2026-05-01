"""Unit tests for sync_navigation_categories pure functions."""
import pytest

from maccabipediabot.maintenance.sync_navigation_categories import (
    PageState,
    ParsedMatch,
    build_canonical_wikitext,
    classify_page_text,
    parse_category_title,
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
