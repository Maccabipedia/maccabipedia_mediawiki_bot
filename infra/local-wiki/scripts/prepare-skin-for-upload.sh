#!/usr/bin/env bash
#
# prepare-skin-for-upload.sh — assemble the complete MaccabiPedia skin
# (vendored source + binary banner assets) at a path OUTSIDE this repo,
# ready to drag into an FTP client and upload to prod.
#
# Each run snapshots into its OWN timestamped directory so previous
# preparations stay around for rollback / audit:
#
#     <base>/<UTC timestamp with ms>/maccabipedia_skin/...
#
# Default base: ~/maccabipedia_skins/
# Override:     ./prepare-skin-for-upload.sh /mnt/c/Users/roee/Desktop/maccabipedia_skins
#               (use a /mnt/c/... base on WSL if you want the snapshots
#               on the Windows desktop where FileZilla can see them)
#
# What goes into each snapshot's maccabipedia_skin/ tree:
#   <repo-root>/skins/Metrolook/                       — tracked source (~1.7 MB)
#   <repo-root>/infra/local-wiki/synced/skins/Metrolook/assets/
#                                                      — binary banners (~5.9 MB),
#                                                        last pulled from prod via
#                                                        sync-from-prod.sh
#
# The local .gitkeep mountpoint marker is stripped (it's irrelevant on
# prod). The leaf is named `maccabipedia_skin` per local convention,
# but on prod the skin still lives at /public_html/skins/Metrolook/ —
# the script's "next steps" output spells this out.

set -euo pipefail

usage() {
    awk 'NR < 2 { next } /^set -euo pipefail/ { exit } { sub(/^# ?/, ""); print }' "$0"
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_WIKI_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPO_ROOT="$(cd "${LOCAL_WIKI_DIR}/../.." && pwd)"

SOURCE_SKIN="${REPO_ROOT}/skins/Metrolook"
SOURCE_ASSETS="${LOCAL_WIKI_DIR}/synced/skins/Metrolook/assets"

DEFAULT_BASE="${HOME}/maccabipedia_skins"
BASE=""

while [ $# -gt 0 ]; do
    case "$1" in
        -h|--help) usage; exit 0 ;;
        -*)        echo "ERROR: unknown flag: $1" >&2; usage >&2; exit 1 ;;
        *)
            if [ -n "$BASE" ]; then
                echo "ERROR: multiple base paths given (got $BASE and $1)" >&2
                exit 1
            fi
            BASE="$1"; shift
            ;;
    esac
done

BASE="${BASE:-$DEFAULT_BASE}"

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

case "$BASE" in
    "$REPO_ROOT"|"$REPO_ROOT"/*)
        echo "WARN: base path is inside the repo ($BASE)." >&2
        echo "      That's allowed but defeats the 'outside the repo' intent." >&2
        ;;
esac

# ISO-8601-style UTC timestamp with milliseconds, with `:` swapped for `-`
# so the path is valid on Windows filesystems (relevant when BASE is on
# /mnt/c/...). Example: 2026-04-25T07-58-31-742Z
TIMESTAMP="$(date -u +"%Y-%m-%dT%H-%M-%S-%3NZ")"
SNAPSHOT_DIR="${BASE}/${TIMESTAMP}"
OUT="${SNAPSHOT_DIR}/maccabipedia_skin"

mkdir -p "$OUT"

echo "==> assembling skin upload snapshot"
echo "    source:   $SOURCE_SKIN"
echo "    assets:   $SOURCE_ASSETS"
echo "    snapshot: $SNAPSHOT_DIR"

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

# Show the few most recent snapshots so the user can see history at a
# glance (and remember to clean old ones up if too many accumulate).
existing=$(find "$BASE" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l)
echo
printf "  %-32s %s\n" "snapshots in $BASE:" "$existing"
if [ "$existing" -gt 1 ]; then
    echo "  recent snapshots:"
    find "$BASE" -mindepth 1 -maxdepth 1 -type d -printf '    %f\n' \
        2>/dev/null | sort -r | head -5
fi

echo
echo "==> next steps for upload"
echo "  Local snapshot: $OUT"
echo "  Prod path:      /public_html/skins/Metrolook/    (note: 'Metrolook',"
echo "                  not 'maccabipedia_skin' — MediaWiki's skin loader"
echo "                  resolves the directory name)"
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
