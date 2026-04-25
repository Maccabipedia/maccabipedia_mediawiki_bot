#!/usr/bin/env bash
#
# End-to-end smoke test for the Metrolook header + footer.
#
# Hits a running MaccabiPedia wiki and asserts:
#   - The main page renders (HTTP 200).
#   - Zero hardcoded https://www.maccabipedia.co.il/ hrefs leak through.
#   - The logo image and the powered-by-MediaWiki image both load (HTTP 200).
#   - Menu links are properly URL-encoded by Title->getLocalURL() (i.e.
#     they go through /index.php/ with %XX-encoded Hebrew + underscore
#     instead of literal Hebrew + space).
#
# Usage:
#   ./scripts/test-menu.sh                           # default: http://localhost:8080
#   ./scripts/test-menu.sh https://maccabipedia.co.il
#
# Exits non-zero with a one-line diagnostic on the first failure.

set -euo pipefail

BASE_URL="${1:-http://localhost:8080}"
BASE_URL="${BASE_URL%/}"
# The Hebrew main page title, percent-encoded.
MAIN_PAGE_PATH='/index.php/%D7%A2%D7%9E%D7%95%D7%93_%D7%A8%D7%90%D7%A9%D7%99'
MAIN_URL="${BASE_URL}${MAIN_PAGE_PATH}"

PASS=0
FAIL=0

assert() {
    local name="$1"
    local condition="$2"
    if eval "$condition"; then
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
echo "Page renders:"
assert "main page returns HTTP 200" "[ '$HTTP_CODE' = '200' ]"

echo
echo "No prod-URL leakage:"
prod_count=$(grep -c 'maccabipedia\.co\.il' "$HTML" || true)
assert "zero hardcoded www.maccabipedia.co.il hrefs (found $prod_count)" "[ '$prod_count' = '0' ]"

echo
echo "Static assets load:"
LOGO=$(grep -oE 'src="[^"]*logo\.png[^"]*"' "$HTML" | head -1 | sed 's/src="//; s/"$//')
assert "<img src> for logo present" "[ -n \"\$LOGO\" ]"
if [ -n "$LOGO" ]; then
    LOGO_CODE=$(curl -sL -o /dev/null -w '%{http_code}' "$LOGO")
    assert "logo URL returns 200 ($LOGO -> $LOGO_CODE)" "[ '$LOGO_CODE' = '200' ]"
fi

PB=$(grep -oE 'src="[^"]*poweredby[^"]*"' "$HTML" | head -1 | sed 's/src="//; s/"$//')
assert "<img src> for powered-by present" "[ -n \"\$PB\" ]"
if [ -n "$PB" ]; then
    PB_CODE=$(curl -sL -o /dev/null -w '%{http_code}' "$PB")
    assert "powered-by URL returns 200 ($PB -> $PB_CODE)" "[ '$PB_CODE' = '200' ]"
fi

echo
echo "Menu links use Title-encoded form:"
# A Title->getLocalURL() href is fully URL-encoded so it never contains a
# literal space (spaces become %20, _, or +). The pre-fix string-concat code
# produced hrefs like /index.php/פורטל מתקנים with a raw space — assert
# that no href in the page contains one.
literal_space_links=$(grep -cE 'href="[^"]* [^"]*"' "$HTML" || true)
assert "no menu hrefs with literal spaces (found $literal_space_links)" \
    "[ '$literal_space_links' = '0' ]"

encoded_count=$(grep -cE 'href="/index.php/%D7' "$HTML" || true)
assert "at least one Title-encoded menu link present (found $encoded_count)" \
    "[ '$encoded_count' -gt 0 ]"

echo
echo "Result: ${PASS} passed, ${FAIL} failed"
[ "$FAIL" = "0" ]
