#!/usr/bin/env bash
#
# prepare-skin-for-upload.sh — assemble the complete MaccabiPedia skin
# (vendored source + binary banner assets) at a path OUTSIDE this repo,
# ready to drag into an FTP client and upload to prod.
#
# Default output: ~/maccabipedia_skin/
# Override:       ./prepare-skin-for-upload.sh /some/other/path
#                 ./prepare-skin-for-upload.sh /mnt/c/Users/roee/Desktop/maccabipedia_skin
#                 (use a /mnt/c/... path on WSL if you want it on the
#                 Windows desktop where FileZilla can see it)
#
# What goes into the output tree:
#   <repo-root>/skins/Metrolook/                       — tracked source (~1.7 MB)
#   <repo-root>/infra/local-wiki/synced/skins/Metrolook/assets/
#                                                      — binary banners (~5.9 MB),
#                                                        last pulled from prod via
#                                                        sync-from-prod.sh
#
# The local .gitkeep mountpoint marker is stripped (it's irrelevant on
# prod). The output dir is named `maccabipedia_skin` per the requested
# local naming, but on prod the skin still lives at
# /public_html/skins/Metrolook/ — see the "next steps" section the
# script prints when it finishes.
#
# Refuses to run if the output dir already exists. Pass --force to wipe
# and re-create.

set -euo pipefail

usage() {
    awk 'NR < 2 { next } /^set -euo pipefail/ { exit } { sub(/^# ?/, ""); print }' "$0"
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_WIKI_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPO_ROOT="$(cd "${LOCAL_WIKI_DIR}/../.." && pwd)"

SOURCE_SKIN="${REPO_ROOT}/skins/Metrolook"
SOURCE_ASSETS="${LOCAL_WIKI_DIR}/synced/skins/Metrolook/assets"

DEFAULT_OUT="${HOME}/maccabipedia_skin"
FORCE=0
OUT=""

while [ $# -gt 0 ]; do
    case "$1" in
        -f|--force)  FORCE=1; shift ;;
        -h|--help)   usage; exit 0 ;;
        -*)          echo "ERROR: unknown flag: $1" >&2; usage >&2; exit 1 ;;
        *)
            if [ -n "$OUT" ]; then
                echo "ERROR: multiple output paths given (got $OUT and $1)" >&2
                exit 1
            fi
            OUT="$1"; shift
            ;;
    esac
done

OUT="${OUT:-$DEFAULT_OUT}"

if [ ! -d "$SOURCE_SKIN" ]; then
    echo "ERROR: skin source not found at $SOURCE_SKIN" >&2
    exit 1
fi
if [ ! -d "$SOURCE_ASSETS" ] || [ -z "$(ls -A "$SOURCE_ASSETS" 2>/dev/null)" ]; then
    echo "ERROR: binary skin assets not found or empty at:" >&2
    echo "  $SOURCE_ASSETS" >&2
    echo "  Run \`./scripts/sync-from-prod.sh maccabipedia-skin-assets\` first." >&2
    exit 1
fi

# Refuse to clobber. Cheap to check, expensive to forget.
if [ -e "$OUT" ]; then
    if [ "$FORCE" -ne 1 ]; then
        echo "ERROR: output path already exists: $OUT" >&2
        echo "       Pass --force to wipe and re-create, or choose a different path." >&2
        exit 1
    fi
    echo "==> --force given; removing existing $OUT"
    rm -rf "$OUT"
fi

# Don't let an output path inside the repo end up gitignored by mistake;
# but don't actively block it either — user might want a /tmp/... path
# they can drag from. Just warn.
case "$OUT" in
    "$REPO_ROOT"|"$REPO_ROOT"/*)
        echo "WARN: output path is inside the repo ($OUT)." >&2
        echo "      That's fine but defeats the 'outside the repo' intent." >&2
        ;;
esac

echo "==> assembling skin upload tree at $OUT"
echo "    source:  $SOURCE_SKIN"
echo "    assets:  $SOURCE_ASSETS"
mkdir -p "$OUT"

# Copy the tracked skin source. cp -a preserves perms and timestamps.
cp -a "$SOURCE_SKIN/." "$OUT/"

# The .gitkeep at skins/Metrolook/assets/ exists only to stabilize the
# docker bind-mount target locally; it has no purpose on prod and would
# look like cruft.
rm -f "$OUT/assets/.gitkeep"

# Replace the (empty) tracked assets/ directory with the real binary
# banners. Synced/ is the FTP mirror so this is exactly what prod
# currently serves.
rm -rf "$OUT/assets"
mkdir -p "$OUT/assets"
cp -a "$SOURCE_ASSETS/." "$OUT/assets/"

echo
echo "==> summary"
printf "  %-32s %s\n" "files:"   "$(find "$OUT" -type f | wc -l)"
printf "  %-32s %s\n" "size:"    "$(du -sh "$OUT" | awk '{print $1}')"
printf "  %-32s %s\n" "menu-helpers.php present:" \
    "$([ -f "$OUT/customize/includes/menu-helpers.php" ] && echo yes || echo NO)"
printf "  %-32s %s\n" "assets/ binary count:" \
    "$(find "$OUT/assets" -type f 2>/dev/null | wc -l)"

echo
echo "==> next steps for upload"
echo "  Local dir:   $OUT"
echo "  Prod path:   /public_html/skins/Metrolook/    (note: 'Metrolook',"
echo "               not 'maccabipedia_skin' — MediaWiki's skin loader"
echo "               resolves the directory name)"
echo
echo "  Safest pattern (atomic via remote rename):"
echo "    1. Upload $OUT to /public_html/skins/Metrolook_new/"
echo "    2. On the FTP server: rename Metrolook → Metrolook_old"
echo "    3. On the FTP server: rename Metrolook_new → Metrolook"
echo "    4. Smoke-test the live site, then delete Metrolook_old later."
echo
echo "  Simpler pattern (overwrite in place):"
echo "    1. Drag the CONTENTS of $OUT into /public_html/skins/Metrolook/"
echo "    2. Smoke-test the live site."
echo
echo "  Smoke test against prod (anonymous-only assertions will pass;"
echo "  admin-login and oldid tests will skip — that's expected):"
echo "    MACCABIPEDIA_LOCAL_URL=https://www.maccabipedia.co.il \\"
echo "      uv run pytest -m integration infra/local-wiki/tests"
