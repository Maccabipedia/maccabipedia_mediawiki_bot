"""Scaffold-level invariants the Maccabipedia skin must hold on every page.

Tests scoped to skin chrome the rest of the suite doesn't naturally cover:
  - exactly one <body>; no PHP errors leak through; correct skin body class
  - mobile viewport meta is emitted (without it iPhones render at 1000px)
  - <h1 class="firstHeading"> never reaches the rendered HTML (otherwise
    the .firstHeading 140% font-size scales the title bar ~40% bigger)
  - search input keeps its .text-field class hook (5 LESS rules in
    app-header.less depend on it)

Menu / footer / link / user-panel assertions live in `test_menu.py`.
"""
from __future__ import annotations

import re

import pytest

from skin_test_constants import PHP_ERROR_RE

pytestmark = pytest.mark.integration


def test_no_php_errors(maccabipedia_anon_html: str) -> None:
    matches = PHP_ERROR_RE.findall(maccabipedia_anon_html)
    assert not matches, f"PHP errors leaked into body: {matches[:5]}"


def test_exactly_one_body_tag(maccabipedia_anon_html: str) -> None:
    body_tag_count = len(re.findall(r"<body\b", maccabipedia_anon_html))
    assert body_tag_count == 1, f"expected exactly 1 <body>, found {body_tag_count}"


def test_body_has_skin_maccabipedia_class(maccabipedia_anon_html: str) -> None:
    body_open_match = re.search(r"<body[^>]*>", maccabipedia_anon_html)
    assert body_open_match, "no <body> tag in response"
    assert "skin-maccabipedia" in body_open_match.group(0), (
        f"skin-maccabipedia not in body classes: {body_open_match.group(0)}"
    )


def test_mobile_viewport_meta_present(maccabipedia_anon_html: str) -> None:
    """Without this, iPhones render the page at 1000px-wide desktop layout."""
    assert re.search(
        r'<meta[^>]*name="viewport"[^>]*content="[^"]*width=device-width',
        maccabipedia_anon_html,
    ), "mobile viewport meta tag missing — mobile UX would render at desktop width"


def test_title_not_wrapped_in_firstheading(maccabipedia_anon_html: str) -> None:
    """SkinMustache's default `html-title-heading` wraps the title in
    <h1 class="firstHeading">, but our `.firstHeading` rule has font-size:140%
    which scales the .mw-page-title-main span ~40% bigger inside the yellow
    .maccabipedia-page-title bar. SkinMaccabipedia overrides html-title-heading
    to use OutputPage::getPageTitle() instead. Assert nothing leaked."""
    assert "firstHeading" not in maccabipedia_anon_html, (
        "found .firstHeading in rendered HTML — would scale the title to ~25px "
        "instead of 17.6px. See SkinMaccabipedia::getTemplateData()."
    )


def test_search_input_has_text_field_class(maccabipedia_anon_html: str) -> None:
    """Five LESS rules in `app-header.less` (white text, padding, transition,
    ::placeholder, focus opacity) target `.search-content .text-field`."""
    assert re.search(
        r'<input[^>]*id="searchInput"[^>]*class="[^"]*\btext-field\b',
        maccabipedia_anon_html,
    ), "search input missing the text-field class hook"
