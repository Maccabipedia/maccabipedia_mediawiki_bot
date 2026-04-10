from maccabipediabot.maintenance.events.find_illegal_events import (
    AutoFixedPage,
    NeedsManualReviewPage,
    ROW_SEPARATOR,
    TRACKING_CATEGORY,
    _page_url,
)


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
