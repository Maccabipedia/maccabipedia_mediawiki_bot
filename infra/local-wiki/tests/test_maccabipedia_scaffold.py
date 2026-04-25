"""Smoke tests for the Maccabipedia skin scaffold + menu parity with Metrolook.

Asserts the new skin (?useskin=maccabipedia):
  - registers and renders the main page without PHP errors
  - emits both `skin-maccabipedia` and `skin-metrolook` body classes
  - emits the same menu links Metrolook does (every label from
    `test_menu._MENU_LABELS` reaches the rendered page)

Run with: ``uv run pytest -m integration infra/local-wiki/tests/test_maccabipedia_scaffold.py``
"""
from __future__ import annotations

import re

import pytest

pytestmark = pytest.mark.integration


# Mirror of `_MENU_LABELS` in test_menu.py — keep the two lists in sync.
# Both sets of tests verify the same menu contract; the duplication exists
# because the test directory has no `__init__.py` (per project convention),
# so cross-test-file imports aren't available.
_MENU_LABELS = [
    # מכבי תל אביב dropdown
    "ההיסטוריה", "עונות", "מתקנים", "מפעלים", "מדים", "תארים",
    # שחקנים וצוות dropdown
    "שחקנים", "אנשי צוות",
    # אוהדים ותרבות dropdown
    "שירים", "כרטיסים ומנויים", "כרזות", "קלפים ומדבקות",
    "תפאורות", "ארגונים", "ספרים", "פנזינים",
    # משחקים dropdown
    "חיפוש משחק", "סטטיסטיקות",
    # standalone link
    "מכבימדיה",
    # footer about-section links (app-footer.php)
    "תרומות", "יצירת קשר",
]

# Anchor on PHP's own display_errors markup (`<b>type</b>: …`) so we don't
# false-positive on wiki content that happens to contain the words "Notice:" /
# "Warning:" / etc. in prose.
_PHP_ERROR_RE = re.compile(r"<b>(?:Fatal error|Warning|Notice|Deprecated)</b>:")


def test_no_php_errors(maccabipedia_anon_html: str) -> None:
    matches = _PHP_ERROR_RE.findall(maccabipedia_anon_html)
    assert not matches, f"PHP errors leaked into body: {matches[:5]}"


def test_body_has_skin_maccabipedia_class(maccabipedia_anon_html: str) -> None:
    """MW emits skin-<validname> on <body>; assert the new skin's class is present."""
    body_open_match = re.search(r"<body[^>]*>", maccabipedia_anon_html)
    assert body_open_match, "no <body> tag in response"
    assert "skin-maccabipedia" in body_open_match.group(0), (
        f"skin-maccabipedia not in body classes: {body_open_match.group(0)}"
    )


def test_body_has_skin_metrolook_compat_class(maccabipedia_anon_html: str) -> None:
    """Compat body class — see spec §0. Drops at Phase 2 + 2 weeks."""
    body_open_match = re.search(r"<body[^>]*>", maccabipedia_anon_html)
    assert body_open_match, "no <body> tag in response"
    assert "skin-metrolook" in body_open_match.group(0), (
        f"compat skin-metrolook missing from body: {body_open_match.group(0)}"
    )


def test_main_page_title_renders(maccabipedia_anon_html: str) -> None:
    """The Hebrew main-page title must reach <h1>."""
    assert "עמוד ראשי" in maccabipedia_anon_html, "main page title not in body"


def test_no_prod_url_leakage(maccabipedia_anon_html: str) -> None:
    assert "maccabipedia.co.il" not in maccabipedia_anon_html


def test_app_header_renders(maccabipedia_anon_html: str) -> None:
    """Maccabipedia must emit the Metrolook-style top header so the shared
    skins.metrolook.styles CSS targets resolve."""
    assert '<header class="app-header">' in maccabipedia_anon_html


def test_app_footer_renders(maccabipedia_anon_html: str) -> None:
    """Footer with the about-section and credits must render."""
    assert "about-maccabipedia" in maccabipedia_anon_html
    assert "all-rights-reserved" in maccabipedia_anon_html


def test_search_form_renders(maccabipedia_anon_html: str) -> None:
    """The header search form is rendered from SkinMustache's data-search-box."""
    assert 'id="searchform"' in maccabipedia_anon_html
    assert 'id="searchInput"' in maccabipedia_anon_html


@pytest.mark.parametrize("label", _MENU_LABELS)
def test_menu_link_renders(maccabipedia_anon_html: str, label: str) -> None:
    """Every Metrolook menu link (`_MENU_LABELS`) must also reach the
    Maccabipedia output. Skin-name diverges, menu contract does not."""
    assert f">{label}</a>" in maccabipedia_anon_html


def test_no_broken_dropdown_hrefs(maccabipedia_anon_html: str) -> None:
    """A dead link from mp_page_url() degrades to href=\"#\" — never intended."""
    broken = re.findall(r'<a href="#">', maccabipedia_anon_html)
    assert not broken, f"found {len(broken)} menu link(s) degraded to href=\"#\""
