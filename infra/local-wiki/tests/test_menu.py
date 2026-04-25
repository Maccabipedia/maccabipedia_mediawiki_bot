"""End-to-end smoke tests for the MaccabiPedia Metrolook menu + footer.

Mirrors the assertions from ``infra/local-wiki/scripts/test-menu.sh`` against
a running local docker stack (default http://localhost:8080). All tests are
marked ``integration`` and deselected by default; run with::

    uv run pytest -m integration infra/local-wiki/tests
"""
from __future__ import annotations

import re

import pytest
import requests

pytestmark = pytest.mark.integration


# Mirror of the menu definitions in
# skins/Metrolook/customize/includes/{app-header,app-footer}.php.
# Adding/removing/renaming a menu link must be a coordinated change in
# both the PHP and this list — the duplication is the point.
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

_PHP_ERROR_RE = re.compile(r"Fatal error|Warning:|Notice:|Deprecated:")


def test_main_page_renders(anon_html: str) -> None:
    """HTTP 200 already asserted in fixture; body must have no PHP errors."""
    matches = _PHP_ERROR_RE.findall(anon_html)
    assert not matches, f"PHP errors leaked into body: {matches[:5]}"


def test_no_prod_url_leakage(anon_html: str) -> None:
    """No hrefs/text mentioning the production wiki should leak through."""
    assert "maccabipedia.co.il" not in anon_html


@pytest.mark.parametrize("asset", ["logo", "powered-by"])
def test_static_asset_loads(anon_html: str, asset: str) -> None:
    """Logo + powered-by-MediaWiki <img src> must be present and HTTP 200."""
    pattern = {
        "logo": r'src="([^"]*logo\.png[^"]*)"',
        "powered-by": r'src="([^"]*poweredby[^"]*)"',
    }[asset]
    match = re.search(pattern, anon_html)
    assert match, f"<img src> for {asset} not found in main page"
    asset_url = match.group(1)
    response = requests.get(asset_url, timeout=15)
    assert response.status_code == 200, (
        f"{asset} URL {asset_url} -> HTTP {response.status_code}"
    )


def test_menu_links_title_encoded(anon_html: str) -> None:
    """No literal-space hrefs and at least one %D7-encoded Hebrew href present.

    A Title->getLocalURL() href is fully URL-encoded so it never contains a
    literal space. The pre-fix string-concat code produced hrefs like
    /פורטל מתקנים with a raw space.
    """
    literal_space = re.findall(r'href="[^"]* [^"]*"', anon_html)
    assert not literal_space, f"menu hrefs with literal spaces: {literal_space[:3]}"
    # With $wgArticlePath = "/$1" the local stack mirrors prod's pretty URLs,
    # so a Hebrew menu link should land on "/%D7…" with no /index.php/ segment.
    encoded = re.findall(r'href="/%D7', anon_html)
    assert encoded, "expected at least one Title-encoded Hebrew menu link"


@pytest.mark.parametrize("label", _MENU_LABELS)
def test_menu_link_renders(anon_html: str, label: str) -> None:
    """Each menu link from $primaryDropdowns + standalone + footer must render."""
    assert f">{label}</a>" in anon_html


def test_no_broken_dropdown_hrefs(anon_html: str) -> None:
    """A dead link from mp_page_url() degrades to href="#" — never intended."""
    broken = re.findall(r'<a href="#">', anon_html)
    assert not broken, f"found {len(broken)} menu link(s) degraded to href=\"#\""


@pytest.mark.parametrize(
    "label, present",
    [
        ("כניסה לחשבון", True),    # login link should be rendered
        ("יצירת חשבון", True),     # create-account link should be rendered
        (">התנתק</a>", False),     # logout must not appear for anon
        (">מחיקה</a>", False),     # delete (admin-only) must not appear for anon
    ],
)
def test_anonymous_user_panel(anon_html: str, label: str, present: bool) -> None:
    """Anonymous (no-cookies) user sees login + create-account, no admin items."""
    if present:
        assert label in anon_html
    else:
        assert label not in anon_html


@pytest.mark.parametrize(
    "label, present",
    [
        # Logged-in user panel: username + talk + preferences + contributions + logout,
        # instead of the anonymous login/create-account links.
        (">התנתק</a>", True),
        (">העדפות</a>", True),
        (">התרומות שלי</a>", True),
        (">עמוד השיחה שלי</a>", True),
        (">כניסה לחשבון</a>", False),
        (">יצירת חשבון</a>", False),
        # Edit panel (default 'edit' permission for any registered user):
        (">עריכה</a>", True),
        # Admin-only items gated on $user->isAllowed('protect'):
        (">מחיקה</a>", True),
        (">העברה</a>", True),
        (">הגנה</a>", True),
    ],
)
def test_admin_user_panel(admin_html: str, label: str, present: bool) -> None:
    """Logged-in admin sees user panel + admin-only options, not anon links."""
    if present:
        assert label in admin_html
    else:
        assert label not in admin_html


def test_oldid_preserved_in_action_urls(main_url: str) -> None:
    """Viewing ?oldid=N must keep that oldid in edit/history action hrefs.

    The only $actionURL behavior the rest of the suite doesn't exercise.
    """
    history = requests.get(main_url, params={"action": "history"}, timeout=15)
    assert history.status_code == 200, f"history fetch -> HTTP {history.status_code}"
    oldid_match = re.search(r"oldid=(\d+)", history.text)
    if not oldid_match:
        pytest.skip("couldn't find an oldid in page history — only 1 revision?")
    oldid = oldid_match.group(1)

    revision = requests.get(main_url, params={"oldid": oldid}, timeout=15)
    assert revision.status_code == 200

    # Param order in the href is not guaranteed; accept either ordering.
    edit_re = re.compile(
        rf'href="[^"]*action=edit[^"]*oldid={oldid}'
        rf'|href="[^"]*oldid={oldid}[^"]*action=edit'
    )
    history_re = re.compile(
        rf'href="[^"]*action=history[^"]*oldid={oldid}'
        rf'|href="[^"]*oldid={oldid}[^"]*action=history'
    )
    assert edit_re.search(revision.text), f"edit href on ?oldid={oldid} dropped oldid"
    assert history_re.search(revision.text), f"history href on ?oldid={oldid} dropped oldid"
