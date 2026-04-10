import pytest
from unittest.mock import Mock, patch

from maccabipediabot.maintenance.events.find_illegal_events import (
    AutoFixedPage,
    NeedsManualReviewPage,
    ROW_SEPARATOR,
    TRACKING_CATEGORY,
    _page_url,
)


# ── Task 1: Module skeleton ──────────────────────────────────────────────────

def test_module_imports_cleanly():
    assert TRACKING_CATEGORY == "אירועי שחקנים לא חוקיים"
    assert ROW_SEPARATOR == ","


def test_page_url_handles_spaces_and_hebrew():
    url = _page_url("משחק:01-01-2001 א נגד ב - ליגה")
    assert url.startswith("https://www.maccabipedia.co.il/")
    assert " " not in url  # spaces replaced with underscores or encoded


def test_auto_fixed_page_is_dataclass():
    page = AutoFixedPage(page_name="משחק:test", fixes_count=3)
    assert page.page_name == "משחק:test"
    assert page.fixes_count == 3


def test_needs_manual_review_is_dataclass():
    page = NeedsManualReviewPage(page_name="משחק:test")
    page.malformed_rows.append("אבי נמני::10::גול-רגל")  # only 3 fields
    page.events_param_value = "..."
    assert len(page.malformed_rows) == 1


# ── Task 2: fetch_category_pages ─────────────────────────────────────────────

def test_fetch_category_pages_returns_pages_from_category():
    from maccabipediabot.maintenance.events.find_illegal_events import fetch_category_pages

    mock_page1 = Mock()
    mock_page1.title.return_value = "משחק:01-01-2001 א נגד ב - ליגה"
    mock_page2 = Mock()
    mock_page2.title.return_value = "משחק:02-02-2002 ג נגד ד - ליגה"

    with patch("maccabipediabot.maintenance.events.find_illegal_events.pw.Category"), \
         patch(
             "maccabipediabot.maintenance.events.find_illegal_events.pagegenerators.CategorizedPageGenerator",
             return_value=[mock_page1, mock_page2],
         ):
        pages = fetch_category_pages(Mock(), "אירועי שחקנים לא חוקיים")

    assert [p.title() for p in pages] == [
        "משחק:01-01-2001 א נגד ב - ליגה",
        "משחק:02-02-2002 ג נגד ד - ליגה",
    ]


def test_fetch_category_pages_returns_empty_when_category_is_empty():
    from maccabipediabot.maintenance.events.find_illegal_events import fetch_category_pages

    with patch("maccabipediabot.maintenance.events.find_illegal_events.pw.Category"), \
         patch(
             "maccabipediabot.maintenance.events.find_illegal_events.pagegenerators.CategorizedPageGenerator",
             return_value=[],
         ):
        pages = fetch_category_pages(Mock(), "אירועי שחקנים לא חוקיים")

    assert pages == []


# ── Task 3: fix_single_colon_trap ────────────────────────────────────────────

def test_fix_single_colon_trap_fixes_single_event():
    from maccabipediabot.maintenance.events.find_illegal_events import fix_single_colon_trap

    text = "אבי נמני::10::גול-רגל:45::מכבי"
    fixed, count = fix_single_colon_trap(text)

    assert fixed == "אבי נמני::10::גול-רגל::45::מכבי"
    assert count == 1


def test_fix_single_colon_trap_fixes_multiple_events():
    from maccabipediabot.maintenance.events.find_illegal_events import fix_single_colon_trap

    text = (
        "אבי נמני::10::גול-רגל:45::מכבי,"
        "אלי דריקס::7::גול-נגיחה:67::מכבי,"
        "חיים רביבו::8::בישול-קלאסי:45::מכבי"
    )
    fixed, count = fix_single_colon_trap(text)

    assert "גול-רגל::45" in fixed
    assert "גול-נגיחה::67" in fixed
    assert "בישול-קלאסי::45" in fixed
    # None of the single-colon patterns should remain
    assert "גול-רגל:45" not in fixed
    assert "גול-נגיחה:67" not in fixed
    assert "בישול-קלאסי:45" not in fixed
    assert count == 3


def test_fix_single_colon_trap_fixes_card_event_with_space_in_type():
    from maccabipediabot.maintenance.events.find_illegal_events import fix_single_colon_trap

    text = "טל בן חיים::3::כרטיס צהוב-שני:65::מכבי"
    fixed, count = fix_single_colon_trap(text)

    assert fixed == "טל בן חיים::3::כרטיס צהוב-שני::65::מכבי"
    assert count == 1


def test_fix_single_colon_trap_leaves_correct_double_colons_alone():
    from maccabipediabot.maintenance.events.find_illegal_events import fix_single_colon_trap

    text = "אבי נמני::10::גול-רגל::45::מכבי"
    fixed, count = fix_single_colon_trap(text)

    assert fixed == text
    assert count == 0


def test_fix_single_colon_trap_fixes_even_for_unknown_event_type():
    """
    The structural regex is deliberately type-agnostic. If a page has
    `גול-קלאסי:45` (unknown subtype AND single colon), we fix the colon.
    The unknown subtype will still keep the page in the tracking category
    on next run — surfaced as manual review then.
    """
    from maccabipediabot.maintenance.events.find_illegal_events import fix_single_colon_trap

    text = "אבי נמני::10::גול-קלאסי:45::מכבי"
    fixed, count = fix_single_colon_trap(text)

    assert fixed == "אבי נמני::10::גול-קלאסי::45::מכבי"
    assert count == 1


def test_fix_single_colon_trap_requires_double_colon_on_both_sides():
    """Don't touch single colons that aren't in the event-row position."""
    from maccabipediabot.maintenance.events.find_illegal_events import fix_single_colon_trap

    # Not sandwiched between `::` separators → not an event row single-colon
    text = "random:text:with:single:colons"
    fixed, count = fix_single_colon_trap(text)

    assert fixed == text
    assert count == 0


# ── Task 4: get_events_param_value + find_malformed_rows ─────────────────────

def test_get_events_param_value_returns_value_from_template():
    from maccabipediabot.maintenance.events.find_illegal_events import get_events_param_value

    wikitext = (
        "{{קטלוג משחקים\n"
        "|תאריך המשחק=01-01-2001\n"
        "|אירועי שחקנים=אבי נמני::10::גול-רגל::45::מכבי\n"
        "}}"
    )
    value = get_events_param_value(wikitext)
    assert "אבי נמני::10::גול-רגל::45::מכבי" in value


def test_get_events_param_value_returns_empty_string_when_template_missing():
    from maccabipediabot.maintenance.events.find_illegal_events import get_events_param_value

    wikitext = "Some text with no קטלוג משחקים template at all."
    assert get_events_param_value(wikitext) == ""


def test_get_events_param_value_returns_empty_string_when_events_param_missing():
    from maccabipediabot.maintenance.events.find_illegal_events import get_events_param_value

    wikitext = "{{קטלוג משחקים\n|תאריך המשחק=01-01-2001\n}}"
    assert get_events_param_value(wikitext) == ""


def test_find_malformed_rows_returns_empty_for_all_correct_rows():
    from maccabipediabot.maintenance.events.find_illegal_events import find_malformed_rows

    value = (
        "אבי נמני::10::גול-רגל::45::מכבי,"
        "אלי דריקס::7::גול-נגיחה::67::מכבי"
    )
    assert find_malformed_rows(value) == []


def test_find_malformed_rows_flags_row_with_too_few_fields():
    from maccabipediabot.maintenance.events.find_illegal_events import find_malformed_rows

    value = (
        "אבי נמני::10::גול-רגל::45::מכבי,"
        "רפי לוי::4::גול-רגל"  # only 3 fields
    )
    rows = find_malformed_rows(value)
    assert rows == ["רפי לוי::4::גול-רגל"]


def test_find_malformed_rows_flags_row_with_non_integer_minute():
    """PlayerEvent.from_maccabipedia_format raises ValueError for non-int minute."""
    from maccabipediabot.maintenance.events.find_illegal_events import find_malformed_rows

    value = "אבי נמני::10::גול-רגל::not_a_number::מכבי"
    rows = find_malformed_rows(value)
    assert rows == ["אבי נמני::10::גול-רגל::not_a_number::מכבי"]


def test_find_malformed_rows_accepts_row_with_half_info_field():
    """Six fields (name::jersey::type::minute::team::half) is also valid."""
    from maccabipediabot.maintenance.events.find_illegal_events import find_malformed_rows

    value = "אבי נמני::10::גול-רגל::45::מכבי::ראשונה"
    assert find_malformed_rows(value) == []


def test_find_malformed_rows_leaves_unknown_event_types_alone():
    """Unknown event types have valid shape — handled via full-value report, not here."""
    from maccabipediabot.maintenance.events.find_illegal_events import find_malformed_rows

    value = "אבי נמני::10::גול-קלאסי::45::מכבי"
    assert find_malformed_rows(value) == []


def test_find_malformed_rows_handles_newline_around_comma_separator():
    """Real pages use '\\n,' between rows for UI readability; split by ',' tolerates newlines."""
    from maccabipediabot.maintenance.events.find_illegal_events import find_malformed_rows

    value = "אבי נמני::10::גול-רגל::45::מכבי\n,רפי לוי::4::גול-רגל"
    rows = find_malformed_rows(value)
    assert rows == ["רפי לוי::4::גול-רגל"]


def test_find_malformed_rows_ignores_empty_rows():
    from maccabipediabot.maintenance.events.find_illegal_events import find_malformed_rows

    value = "אבי נמני::10::גול-רגל::45::מכבי,,"  # trailing empty rows
    assert find_malformed_rows(value) == []


# ── Task 5: format_report ────────────────────────────────────────────────────

from datetime import date


def test_format_report_returns_empty_string_when_nothing_to_report():
    from maccabipediabot.maintenance.events.find_illegal_events import format_report

    report = format_report([], [], date(2026, 4, 10))
    assert report == ""


def test_format_report_shows_auto_fixed_section():
    from maccabipediabot.maintenance.events.find_illegal_events import (
        AutoFixedPage,
        format_report,
    )

    fixed = [
        AutoFixedPage(
            page_name='משחק:29-03-1971 בנגקוק בנק נגד מכבי תל אביב - גביע אסיה',
            fixes_count=1,
        )
    ]
    report = format_report(fixed, [], date(2026, 4, 10))

    assert "תוקנו אוטומטית" in report
    assert "2026-04-10" in report
    assert "29-03-1971" in report
    assert '<a href="https://www.maccabipedia.co.il/' in report


def test_format_report_shows_manual_review_with_malformed_rows():
    from maccabipediabot.maintenance.events.find_illegal_events import (
        NeedsManualReviewPage,
        format_report,
    )

    needs_review = [
        NeedsManualReviewPage(
            page_name="משחק:13-12-2020 הפועל חיפה נגד מכבי תל אביב - ליגת העל",
            malformed_rows=["חנן ממן::9::גול-רגל"],  # too few fields
        )
    ]
    report = format_report([], needs_review, date(2026, 4, 10))

    assert "דורש בדיקה ידנית" in report
    assert "13-12-2020" in report
    assert "חנן ממן::9::גול-רגל" in report


def test_format_report_shows_manual_review_with_events_param_fallback():
    """When no malformed rows but page is still in category, show the full value."""
    from maccabipediabot.maintenance.events.find_illegal_events import (
        NeedsManualReviewPage,
        format_report,
    )

    needs_review = [
        NeedsManualReviewPage(
            page_name="משחק:18-02-1961 בני יהודה נגד מכבי תל אביב - ליגה לאומית",
            malformed_rows=[],
            events_param_value="אבי נמני::10::גול-קלאסי::45::מכבי,רפי לוי::4::גול-קלאסי::60::מכבי",
        )
    ]
    report = format_report([], needs_review, date(2026, 4, 10))

    assert "דורש בדיקה ידנית" in report
    assert "18-02-1961" in report
    # Full events value is included for human scanning
    assert "אבי נמני::10::גול-קלאסי::45::מכבי" in report


def test_format_report_shows_both_sections_when_both_non_empty():
    from maccabipediabot.maintenance.events.find_illegal_events import (
        AutoFixedPage,
        NeedsManualReviewPage,
        format_report,
    )

    fixed = [AutoFixedPage("משחק:a", fixes_count=2)]
    needs_review = [NeedsManualReviewPage("משחק:b", malformed_rows=["x::y::z"])]

    report = format_report(fixed, needs_review, date(2026, 4, 10))
    assert "תוקנו אוטומטית" in report
    assert "דורש בדיקה ידנית" in report
    assert "משחק:a" in report
    assert "משחק:b" in report


def test_format_report_lists_multiple_malformed_rows_on_same_page():
    from maccabipediabot.maintenance.events.find_illegal_events import (
        NeedsManualReviewPage,
        format_report,
    )

    needs_review = [
        NeedsManualReviewPage(
            page_name="משחק:11-04-1942 מכבי תל אביב נגד שבאב אל ערב - ליגה לאומית",
            malformed_rows=[
                "פלוני אלמוני::1::גול-רגל",
                "פלוני אחר::2::גול-רגל",
            ],
        )
    ]
    report = format_report([], needs_review, date(2026, 4, 10))

    assert "פלוני אלמוני" in report
    assert "פלוני אחר" in report


# ── Task 6: process_page ─────────────────────────────────────────────────────

def test_process_page_returns_auto_fixed_when_single_colon_fix_applied():
    from maccabipediabot.maintenance.events.find_illegal_events import (
        AutoFixedPage,
        process_page,
    )

    before = (
        "{{קטלוג משחקים\n"
        "|אירועי שחקנים=אבי נמני::10::גול-נגיחה:67::מכבי"
        "}}"
    )
    mock_page = Mock()
    mock_page.text = before

    result = process_page(mock_page, page_name="משחק:test")

    assert isinstance(result, AutoFixedPage)
    assert result.page_name == "משחק:test"
    assert result.fixes_count == 1
    # Page text was updated and saved
    assert "גול-נגיחה::67" in mock_page.text
    mock_page.save.assert_called_once()


def test_process_page_returns_needs_review_with_malformed_rows():
    """Malformed row shape is surfaced explicitly."""
    from maccabipediabot.maintenance.events.find_illegal_events import (
        NeedsManualReviewPage,
        process_page,
    )

    before = (
        "{{קטלוג משחקים\n"
        "|אירועי שחקנים=חנן ממן::9::גול-רגל"  # only 3 fields
        "}}"
    )
    mock_page = Mock()
    mock_page.text = before

    result = process_page(mock_page, page_name="משחק:test")

    assert isinstance(result, NeedsManualReviewPage)
    assert result.malformed_rows == ["חנן ממן::9::גול-רגל"]
    mock_page.save.assert_not_called()


def test_process_page_returns_needs_review_with_events_param_fallback():
    """Valid shape but still broken (unknown event type) → surface full value."""
    from maccabipediabot.maintenance.events.find_illegal_events import (
        NeedsManualReviewPage,
        process_page,
    )

    before = (
        "{{קטלוג משחקים\n"
        "|אירועי שחקנים=חנן ממן::9::גול-קלאסי::45::מכבי"  # unknown type, valid shape
        "}}"
    )
    mock_page = Mock()
    mock_page.text = before

    result = process_page(mock_page, page_name="משחק:test")

    assert isinstance(result, NeedsManualReviewPage)
    assert result.malformed_rows == []
    assert "חנן ממן::9::גול-קלאסי::45::מכבי" in result.events_param_value
    mock_page.save.assert_not_called()
