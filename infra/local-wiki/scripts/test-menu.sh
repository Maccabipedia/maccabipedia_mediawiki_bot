#!/usr/bin/env bash
#
# End-to-end smoke test for the MaccabiPedia skin's header + footer.
#
# Hits a running MaccabiPedia wiki and asserts:
#   - The main page renders (HTTP 200) with no PHP errors/warnings/notices
#     in the body — this is the primary catch for a broken skin rewrite.
#   - Zero hardcoded https://www.maccabipedia.co.il/ hrefs leak through.
#   - Logo image and powered-by-MediaWiki image both load (HTTP 200).
#   - Menu links are properly URL-encoded by Title->getLocalURL() (i.e.
#     they go through /index.php/ with %XX-encoded Hebrew + underscore
#     instead of literal Hebrew + space).
#   - All four primary dropdown headings appear in the rendered HTML.
#   - A representative sample of menu entries (Hebrew titles) render with
#     properly Title-encoded hrefs (catches mp_page_url() returning '#').
#   - Anonymous-user panel renders with login + create-account links.
#   - Viewing an old revision (?oldid=N) preserves the oldid in the
#     edit/history/purge action URLs (the only $actionURL behavior that
#     the rest of the suite doesn't exercise).
#
# Usage:
#   ./scripts/test-menu.sh                           # default: http://localhost:8080
#   ./scripts/test-menu.sh https://maccabipedia.co.il
#
# Exits 0 on all-pass, 1 on any failure, 2 on missing dependency.

set -euo pipefail

command -v curl >/dev/null || { echo "ERROR: curl required but not found" >&2; exit 2; }

BASE_URL="${1:-http://localhost:8080}"
BASE_URL="${BASE_URL%/}"
# Hebrew main page title ("עמוד ראשי"), percent-encoded.
MAIN_PAGE_PATH='/index.php/%D7%A2%D7%9E%D7%95%D7%93_%D7%A8%D7%90%D7%A9%D7%99'
MAIN_URL="${BASE_URL}${MAIN_PAGE_PATH}"

PASS=0
FAIL=0

# Run a command (passed as remaining args); pass if it exits 0, fail if not.
# Avoids the eval-with-shell-string footgun of the previous version.
assert() {
    local name="$1"
    shift
    if "$@" >/dev/null 2>&1; then
        echo "  ✓ ${name}"
        PASS=$((PASS + 1))
    else
        echo "  ✗ ${name}"
        FAIL=$((FAIL + 1))
    fi
}

echo "==> GET ${MAIN_URL}"
HTML="$(mktemp)"
trap 'rm -f "$HTML"' EXIT
HTTP_CODE=$(curl -sL -o "$HTML" -w '%{http_code}' "$MAIN_URL")

echo
echo "Page renders cleanly:"
assert "main page returns HTTP 200 (got $HTTP_CODE)" \
    test "$HTTP_CODE" = "200"
# Catches a 200 response that nonetheless contains a PHP fatal/warning
# in the body — the single most important assertion for a PHP rewrite.
php_errors=$(grep -cE 'Fatal error|Warning:|Notice:|Deprecated:' "$HTML" || true)
assert "no PHP errors/warnings/notices in body (found $php_errors)" \
    test "$php_errors" = "0"

echo
echo "No prod-URL leakage:"
prod_count=$(grep -c 'maccabipedia\.co\.il' "$HTML" || true)
assert "zero hardcoded www.maccabipedia.co.il hrefs (found $prod_count)" \
    test "$prod_count" = "0"

echo
echo "Static assets load:"
LOGO=$(grep -oE 'src="[^"]*logo\.png[^"]*"' "$HTML" | head -1 | sed 's/src="//; s/"$//')
assert "<img src> for logo present" test -n "$LOGO"
if [ -n "$LOGO" ]; then
    LOGO_CODE=$(curl -sL -o /dev/null -w '%{http_code}' "$LOGO")
    assert "logo URL returns 200 ($LOGO -> $LOGO_CODE)" \
        test "$LOGO_CODE" = "200"
fi

PB=$(grep -oE 'src="[^"]*poweredby[^"]*"' "$HTML" | head -1 | sed 's/src="//; s/"$//')
assert "<img src> for powered-by present" test -n "$PB"
if [ -n "$PB" ]; then
    PB_CODE=$(curl -sL -o /dev/null -w '%{http_code}' "$PB")
    assert "powered-by URL returns 200 ($PB -> $PB_CODE)" \
        test "$PB_CODE" = "200"
fi

echo
echo "Menu links use Title-encoded form:"
# A Title->getLocalURL() href is fully URL-encoded so it never contains a
# literal space (spaces become %20 or _). The pre-fix string-concat code
# produced hrefs like /index.php/פורטל מתקנים with a raw space.
literal_space_links=$(grep -cE 'href="[^"]* [^"]*"' "$HTML" || true)
assert "no menu hrefs with literal spaces (found $literal_space_links)" \
    test "$literal_space_links" = "0"
encoded_count=$(grep -cE 'href="/index.php/%D7' "$HTML" || true)
assert "at least one Title-encoded menu link present (found $encoded_count)" \
    test "$encoded_count" -gt 0

echo
echo "All four primary dropdown headings render:"
for heading in 'מכבי תל אביב' 'שחקנים וצוות' 'אוהדים ותרבות' 'משחקים'; do
    assert "dropdown heading '$heading' present" \
        grep -qF "$heading" "$HTML"
done

echo
echo "Representative menu entries render with Title-encoded hrefs:"
# Each pair = (Hebrew display label, percent-encoded title in the href)
# שירי קהל     -> %D7%A9%D7%99%D7%A8%D7%99_%D7%A7%D7%94%D7%9C
# פורטל שחקנים  -> %D7%A4%D7%95%D7%A8%D7%98%D7%9C_%D7%A9%D7%97%D7%A7%D7%A0%D7%99%D7%9D
# ארגוני אוהדים -> %D7%90%D7%A8%D7%92%D7%95%D7%A0%D7%99_%D7%90%D7%95%D7%94%D7%93%D7%99%D7%9D
sample_entries=(
    "שירי קהל:%D7%A9%D7%99%D7%A8%D7%99_%D7%A7%D7%94%D7%9C"
    "פורטל שחקנים:%D7%A4%D7%95%D7%A8%D7%98%D7%9C_%D7%A9%D7%97%D7%A7%D7%A0%D7%99%D7%9D"
    "ארגוני אוהדים:%D7%90%D7%A8%D7%92%D7%95%D7%A0%D7%99_%D7%90%D7%95%D7%94%D7%93%D7%99%D7%9D"
)
for entry in "${sample_entries[@]}"; do
    label="${entry%%:*}"
    encoded="${entry##*:}"
    assert "menu entry '$label' rendered with Title-encoded href" \
        grep -qF "$encoded" "$HTML"
done

echo
echo "Anonymous user panel renders with login + create-account links:"
# We curl with no cookies, so the page is rendered for an anonymous user.
# Match by the menu's Hebrew labels (specific enough to be unique).
assert "anonymous: 'כניסה לחשבון' link rendered" \
    grep -qF 'כניסה לחשבון' "$HTML"
assert "anonymous: 'יצירת חשבון' link rendered" \
    grep -qF 'יצירת חשבון' "$HTML"

echo
echo "oldid is preserved in action URLs when viewing an old revision:"
# Pull the first oldid from the page history, then fetch that revision and
# confirm the menu's edit/history hrefs target it (the one $actionURL
# behavior the rest of the suite doesn't exercise).
HISTORY_HTML="$(mktemp)"
curl -sL -o "$HISTORY_HTML" "${MAIN_URL}?action=history"
oldid=$(grep -oE 'oldid=[0-9]+' "$HISTORY_HTML" | head -1 | sed 's/oldid=//')
rm -f "$HISTORY_HTML"
if [ -z "$oldid" ]; then
    echo "  · skipped (couldn't find an oldid in page history — only 1 revision?)"
else
    OLDREV_HTML="$(mktemp)"
    curl -sL -o "$OLDREV_HTML" "${MAIN_URL}?oldid=${oldid}"
    # The action URL on an old revision must keep oldid=$oldid AND add an
    # action=…; the order of params is not guaranteed, so grep for both
    # appearing in the same href.
    edit_with_oldid=$(grep -cE "href=\"[^\"]*action=edit[^\"]*oldid=${oldid}|href=\"[^\"]*oldid=${oldid}[^\"]*action=edit" "$OLDREV_HTML" || true)
    assert "edit href on ?oldid=${oldid} preserves oldid (found $edit_with_oldid match(es))" \
        test "$edit_with_oldid" -gt 0
    history_with_oldid=$(grep -cE "href=\"[^\"]*action=history[^\"]*oldid=${oldid}|href=\"[^\"]*oldid=${oldid}[^\"]*action=history" "$OLDREV_HTML" || true)
    assert "history href on ?oldid=${oldid} preserves oldid (found $history_with_oldid match(es))" \
        test "$history_with_oldid" -gt 0
    rm -f "$OLDREV_HTML"
fi

echo
echo "Result: ${PASS} passed, ${FAIL} failed"
[ "$FAIL" = "0" ]
