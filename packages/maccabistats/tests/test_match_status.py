"""Sanity tests for the maccabi-tlv finished-match detector."""
import pytest
from bs4 import BeautifulSoup

from maccabistats.parse.maccabi_tlv_site.match_status import is_match_finished


def _page_with_banner_classes(*classes: str) -> BeautifulSoup:
    cls = " ".join(classes)
    return BeautifulSoup(f'<html><div class="{cls}"></div></html>', "html.parser")


@pytest.mark.parametrize(
    "banner_classes, expected",
    [
        # In play (incl. half-time and stoppage) — site keeps `live` on the banner.
        (("site-top-banner", "fixtures-list", "live"), False),
        # Final whistle blown — site strips `live`.
        (("site-top-banner", "fixtures-list"), True),
    ],
)
def test_is_match_finished(banner_classes, expected):
    assert is_match_finished(_page_with_banner_classes(*banner_classes)) is expected


def test_missing_top_banner_treated_as_unfinished():
    """If maccabi-tlv renames `site-top-banner.fixtures-list` we'd rather fail
    closed (skip everything) than silently treat every match as finished."""
    soup = BeautifulSoup("<html><body><p>no banner</p></body></html>", "html.parser")
    assert is_match_finished(soup) is False
