"""Smoke tests for the Maccabipedia skin scaffold.

Asserts the new skin registers, loads via ?useskin=maccabipedia, renders
the main page without PHP errors, and emits the expected body classes.

Visual / menu parity with Metrolook is NOT checked here — that lands in
Plan 2 (style port) and Plan 3 (template port).

Run with: ``uv run pytest -m integration infra/local-wiki/tests/test_maccabipedia_scaffold.py``
"""
from __future__ import annotations

import re

import pytest

pytestmark = pytest.mark.integration

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
