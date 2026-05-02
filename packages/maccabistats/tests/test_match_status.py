"""Sanity tests for the maccabi-tlv finished-match detector."""
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from maccabistats.parse.maccabi_tlv_site.match_status import is_match_finished

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "maccabi_tlv_site"


def _load(name: str) -> BeautifulSoup:
    return BeautifulSoup((FIXTURES_DIR / name).read_bytes(), "html.parser")


@pytest.mark.parametrize(
    "fixture_name, expected",
    [
        # Captured 2026-05-02 ~17:46Z while Maccabi TA – Beitar JLM was 16 minutes in
        ("match_live_2026-05-02.html", False),
        # Same match at half-time — live class still set; not yet finished
        ("match_halftime_2026-05-02.html", False),
        # Maccabi TA – Hapoel BS 28-04-2026, captured post-match
        ("match_finished_2026-04-28.html", True),
        # Maccabi TA – Bnei Sakhnin 28-09-2025, finished but no attendance reported
        ("match_finished_no_attendance_2025-09-28.html", True),
    ],
)
def test_is_match_finished(fixture_name: str, expected: bool) -> None:
    assert is_match_finished(_load(fixture_name)) is expected


def test_missing_top_banner_treated_as_unfinished() -> None:
    """If the site renames `site-top-banner.fixtures-list` we'd rather fail
    closed (skip everything) than silently treat every match as finished."""
    soup = BeautifulSoup("<html><body><p>no banner</p></body></html>", "html.parser")
    assert is_match_finished(soup) is False
