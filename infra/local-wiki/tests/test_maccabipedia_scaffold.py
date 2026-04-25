"""Smoke tests for the Maccabipedia skin (scaffold + visual/menu parity).

Asserts the new skin (?useskin=maccabipedia):
  - registers and renders the main page without PHP errors
  - emits both `skin-maccabipedia` and `skin-metrolook` body classes
  - emits exactly one `<body>` tag
  - emits the mobile viewport meta (without it iPhones render at 1000px)
  - suppresses `<h1>` on the main page (parity with Metrolook)
  - keeps the `text-field` class on the search input (CSS hook in app-header.less)
  - emits the same menu links Metrolook does (every `MENU_LABELS` entry
    reaches the rendered page)

`MENU_LABELS` and `PHP_ERROR_RE` come from conftest.py — single source for
both this suite and `test_menu.py`.

Run with: ``uv run pytest -m integration infra/local-wiki/tests/test_maccabipedia_scaffold.py``
"""
from __future__ import annotations

import re

import pytest

from skin_test_constants import MENU_LABELS, PHP_ERROR_RE

pytestmark = pytest.mark.integration


def test_no_php_errors(maccabipedia_anon_html: str) -> None:
    matches = PHP_ERROR_RE.findall(maccabipedia_anon_html)
    assert not matches, f"PHP errors leaked into body: {matches[:5]}"


def test_exactly_one_body_tag(maccabipedia_anon_html: str) -> None:
    """SkinMustache + our template should emit one <body>; a duplicate would
    indicate the legacy bodyOnly=true mismatch (re-flagged by the principal review)."""
    body_tag_count = len(re.findall(r"<body\b", maccabipedia_anon_html))
    assert body_tag_count == 1, (
        f"expected exactly 1 <body> tag, found {body_tag_count}"
    )


def test_body_has_skin_maccabipedia_class(maccabipedia_anon_html: str) -> None:
    """MW emits skin-<validname> on <body>; assert the new skin's class is present."""
    body_open_match = re.search(r"<body[^>]*>", maccabipedia_anon_html)
    assert body_open_match, "no <body> tag in response"
    assert "skin-maccabipedia" in body_open_match.group(0), (
        f"skin-maccabipedia not in body classes: {body_open_match.group(0)}"
    )


def test_body_has_skin_metrolook_compat_class(maccabipedia_anon_html: str) -> None:
    """Compat body class — see SkinMaccabipedia::getPageClasses() docblock.
    Drops on or after 2026-05-09 (Trello https://trello.com/c/dMO1FPCj)."""
    body_open_match = re.search(r"<body[^>]*>", maccabipedia_anon_html)
    assert body_open_match, "no <body> tag in response"
    assert "skin-metrolook" in body_open_match.group(0), (
        f"compat skin-metrolook missing from body: {body_open_match.group(0)}"
    )


def test_mobile_viewport_meta_present(maccabipedia_anon_html: str) -> None:
    """Without this, iPhones render the page at 1000px-wide desktop layout.
    Metrolook gates this on $wgMetrolookMobile=true; the new skin always emits."""
    assert re.search(
        r'<meta[^>]*name="viewport"[^>]*content="[^"]*width=device-width',
        maccabipedia_anon_html,
    ), "mobile viewport meta tag missing — mobile UX would render at desktop width"


def test_no_h1_on_main_page(maccabipedia_anon_html: str) -> None:
    """The main page should not display its title heading — the app-header chrome
    already carries the site identity, so an extra <h1> above the lead paragraph
    is visual noise (parity with Metrolook's implicit suppression)."""
    h1_count = len(re.findall(r'<h1[^>]*class="[^"]*firstHeading', maccabipedia_anon_html))
    assert h1_count == 0, (
        f"main page emits {h1_count} firstHeading <h1>; expected 0"
    )


def test_title_not_wrapped_in_firstheading(maccabipedia_anon_html: str) -> None:
    """SkinMustache's default `html-title-heading` wraps the title in
    <h1 class="firstHeading">, but our `.firstHeading` rule has font-size:140%
    which scales the .mw-page-title-main span ~40% bigger than intended inside
    the yellow .maccabipedia-page-title bar. SkinMaccabipedia overrides
    html-title-heading to use OutputPage::getPageTitle() instead — assert no
    `firstHeading` wrapper reaches the rendered output anywhere on the page."""
    assert "firstHeading" not in maccabipedia_anon_html, (
        "found .firstHeading in rendered HTML — would scale the title to ~25px "
        "instead of 17.6px. See SkinMaccabipedia::getTemplateData()."
    )


def test_search_input_has_text_field_class(maccabipedia_anon_html: str) -> None:
    """Five LESS rules in `app-header.less` (white text, padding, transition,
    ::placeholder, focus opacity) target `.search-content .text-field`; without
    this class the search box silently loses its styling."""
    assert re.search(
        r'<input[^>]*id="searchInput"[^>]*class="[^"]*\btext-field\b',
        maccabipedia_anon_html,
    ), "search input missing the text-field class hook"


def test_app_header_renders(maccabipedia_anon_html: str) -> None:
    assert '<header class="app-header">' in maccabipedia_anon_html


def test_app_footer_renders(maccabipedia_anon_html: str) -> None:
    assert "about-maccabipedia" in maccabipedia_anon_html
    assert "all-rights-reserved" in maccabipedia_anon_html


def test_search_form_renders(maccabipedia_anon_html: str) -> None:
    assert 'id="searchform"' in maccabipedia_anon_html
    assert 'id="searchInput"' in maccabipedia_anon_html


def test_no_prod_url_leakage(maccabipedia_anon_html: str) -> None:
    assert "maccabipedia.co.il" not in maccabipedia_anon_html


@pytest.mark.parametrize("label", MENU_LABELS)
def test_menu_link_renders(maccabipedia_anon_html: str, label: str) -> None:
    """Every Metrolook menu link must also reach the Maccabipedia output.
    Skin-name diverges; menu contract does not."""
    assert f">{label}</a>" in maccabipedia_anon_html


def test_no_broken_dropdown_hrefs(maccabipedia_anon_html: str) -> None:
    """A dead link from the pageUrl helper degrades to href="#" — never intended."""
    broken = re.findall(r'<a href="#">', maccabipedia_anon_html)
    assert not broken, f"found {len(broken)} menu link(s) degraded to href=\"#\""
