"""Unit tests for sync_navigation_categories pure functions."""
from unittest.mock import MagicMock

from maccabipediabot.maintenance.sync_navigation_categories import (
    ParsedMatch,
    build_canonical_wikitext,
    discover_matches,
    parse_category_title,
)


class TestParseCategoryTitle:
    def test_trophy_players(self):
        result = parse_category_title("שחקני כדורגל שזכו ב-3 אליפויות")
        assert result == ParsedMatch(
            kind="זכיה",
            sport="כדורגל",
            role="שחקנים",
            count=3,
            trophy_type="אליפויות",
        )

    def test_trophy_staff(self):
        result = parse_category_title("אנשי צוות כדורסל שזכו ב-19 תארים")
        assert result == ParsedMatch(
            kind="זכיה",
            sport="כדורסל",
            role="צוות",
            count=19,
            trophy_type="תארים",
        )

    def test_trophy_with_multi_word_type(self):
        result = parse_category_title("שחקני כדורסל שזכו ב-1 הגביע הבין יבשתי")
        assert result == ParsedMatch(
            kind="זכיה",
            sport="כדורסל",
            role="שחקנים",
            count=1,
            trophy_type="הגביע הבין יבשתי",
        )

    def test_seasons_players(self):
        result = parse_category_title("שחקני כדורגל ששיחקו 5 עונות במכבי")
        assert result == ParsedMatch(
            kind="עונות",
            sport="כדורגל",
            role="שחקנים",
            count=5,
            trophy_type=None,
        )

    def test_seasons_staff(self):
        result = parse_category_title("אנשי צוות כדורעף שהיו 7 עונות במכבי")
        assert result == ParsedMatch(
            kind="עונות",
            sport="כדורעף",
            role="צוות",
            count=7,
            trophy_type=None,
        )

    def test_unrelated_returns_none(self):
        assert parse_category_title("קטגוריה:משחקי כדורגל") is None
        assert parse_category_title("שחקני כדורגל") is None

    def test_zero_count_returns_none(self):
        # N=0 categories exist in the data but the templates can't render them
        # (DPL regex is [1-9]). Skip so we don't waste edits / create useless pages.
        assert parse_category_title("שחקני כדורסל ששיחקו 0 עונות במכבי") is None
        assert parse_category_title("אנשי צוות כדורגל שהיו 0 עונות במכבי") is None
        assert parse_category_title("שחקני כדורגל שזכו ב-0 אליפויות") is None

    def test_count_above_99_returns_none(self):
        # The DPL templates' regex caps at [1-9][0-9], so N≥100 wouldn't render.
        assert parse_category_title("שחקני כדורגל שזכו ב-100 אליפויות") is None
        assert parse_category_title("שחקני כדורגל ששיחקו 150 עונות במכבי") is None

    def test_count_99_is_accepted(self):
        result = parse_category_title("שחקני כדורגל שזכו ב-99 אליפויות")
        assert result is not None
        assert result.count == 99

    def test_unknown_sport_passes_through(self):
        # No sport allowlist — any future sport flows through.
        result = parse_category_title("שחקני האנדבול שזכו ב-1 אליפויות")
        assert result == ParsedMatch(
            kind="זכיה",
            sport="האנדבול",
            role="שחקנים",
            count=1,
            trophy_type="אליפויות",
        )


class TestBuildCanonicalWikitext:
    def test_trophy_players(self):
        parsed = ParsedMatch(
            kind="זכיה", sport="כדורגל", role="שחקנים", count=3, trophy_type="אליפויות"
        )
        assert build_canonical_wikitext(parsed) == (
            "{{ניווט קטגוריות זכיה בתארים |ענף=כדורגל |תואר=אליפויות}}"
        )

    def test_trophy_staff(self):
        parsed = ParsedMatch(
            kind="זכיה", sport="כדורסל", role="צוות", count=19, trophy_type="תארים"
        )
        assert build_canonical_wikitext(parsed) == (
            "{{ניווט קטגוריות זכיה בתארים |ענף=כדורסל |תואר=תארים |האם אנשי צוות=כן}}"
        )

    def test_seasons_players(self):
        parsed = ParsedMatch(
            kind="עונות", sport="כדורגל", role="שחקנים", count=5, trophy_type=None
        )
        assert build_canonical_wikitext(parsed) == (
            "{{ניווט קטגוריות עונות במכבי |ענף=כדורגל}}"
        )

    def test_seasons_staff(self):
        parsed = ParsedMatch(
            kind="עונות", sport="כדורעף", role="צוות", count=7, trophy_type=None
        )
        assert build_canonical_wikitext(parsed) == (
            "{{ניווט קטגוריות עונות במכבי |ענף=כדורעף |האם אנשי צוות=כן}}"
        )


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
        kinds = {(parsed.kind, parsed.sport, parsed.role, parsed.count) for _title, parsed in matches}
        assert kinds == {
            ("זכיה", "כדורגל", "שחקנים", 3),
            ("עונות", "כדורגל", "שחקנים", 5),
            ("זכיה", "כדורסל", "צוות", 19),
            ("עונות", "כדורעף", "צוות", 7),
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
        for _title, parsed in matches:
            assert parsed.sport == "כדורגל"

