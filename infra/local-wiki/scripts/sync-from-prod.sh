#!/usr/bin/env bash
#
# Pull selected files/directories from the production MaccabiPedia FTP server
# into the (gitignored) infra/local-wiki/synced/ directory.
#
# Security model:
#   - Only the named operations below are supported — no arbitrary paths.
#   - Download-only. lftp mirror is invoked without -R; no `put`/`rm`/reverse
#     sync is available through this script. A scoped read-only FTP account
#     is recommended but not enforced here.
#   - Credentials come from env vars; never hardcoded, never logged.
#   - Every invocation appends a timestamped line to SYNC_LOG.
#
# Required for FTP-based ops (skins, extensions, logo-assets, localsettings,
# versions):
#   MACCABIPEDIA_FTP_HOST        — FTP hostname (e.g. ftp.maccabipedia.co.il)
#   MACCABIPEDIA_FTP_USER        — FTP username
#   MACCABIPEDIA_FTP_PASS        — FTP password
#   MACCABIPEDIA_FTP_REMOTE_ROOT — absolute path of the MediaWiki webroot on
#                                  the FTP server (e.g. /public_html)
#
# Required for HTTP-based ops (pages):
#   MACCABIPEDIA_WEB_URL         — public site base URL
#                                  (default: https://maccabipedia.co.il)
#
# Optional:
#   MACCABIPEDIA_FTP_REQUIRE_TLS=1   — fail unless the control channel is TLS
#   MACCABIPEDIA_FTP_TLS_VERIFY=1    — require a system-trusted FTP TLS cert
#
# Usage:
#   ./sync-from-prod.sh <op> [args...]
#
# Allowed <op> values:
#   skins             — mirror <root>/skins/           → synced/skins/
#   extensions        — mirror <root>/extensions/      → synced/extensions/
#   localsettings     — fetch   <root>/LocalSettings.php
#                       → synced/LocalSettings.prod-snapshot.php
#   logo-assets       — mirror <root>/resources/assets/ → synced/resources/assets/
#   versions          — list remote directory names under the webroot for audit
#                       (no downloads; prints remote listing only)
#   pages <manifest>  — pull page wikitext via Special:Export (HTTP) for every
#                       title in <manifest> (one title per line; blanks and
#                       lines starting with '#' ignored). Templates referenced
#                       by the pages are included automatically. Output:
#                       synced/pages/<manifest-stem>.xml  (MediaWiki XML dump)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_WIKI_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
SYNCED_DIR="${LOCAL_WIKI_DIR}/synced"

REPO_ROOT="$(cd "${LOCAL_WIKI_DIR}/../.." && pwd)"
SYNC_LOG="${REPO_ROOT}/.claude/tmp/ftp-sync.log"

# Auto-load local .env if present. It's gitignored; intended for FTP creds.
# Only MACCABIPEDIA_FTP_* vars are honored downstream, other vars in the file
# will be set but not used by this script.
ENV_FILE="${LOCAL_WIKI_DIR}/.env"
if [ -f "$ENV_FILE" ]; then
    echo "==> sourcing ${ENV_FILE}"
    set -a
    # shellcheck disable=SC1090
    . "$ENV_FILE"
    set +a
fi

usage() {
    sed -n '2,45p' "$0" | sed 's/^# \{0,1\}//'
}

require_env() {
    local missing=()
    for var in "$@"; do
        if [ -z "${!var-}" ]; then
            missing+=("$var")
        fi
    done
    if [ ${#missing[@]} -gt 0 ]; then
        echo "ERROR: missing required env var(s): ${missing[*]}" >&2
        exit 1
    fi
}

log_event() {
    mkdir -p "$(dirname "$SYNC_LOG")"
    printf '%s  %s  remote=%s  local=%s\n' \
        "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        "$1" "$2" "${3:-}" \
        >> "$SYNC_LOG"
}

run_lftp() {
    local script="$1"
    # Shared hosts often present self-signed / untrusted TLS certs. Default is
    # TLS encryption *without* strict cert verification — encrypts password on
    # the wire, accepts untrusted cert. Set MACCABIPEDIA_FTP_TLS_VERIFY=1 to
    # require a system-trusted cert. Set MACCABIPEDIA_FTP_REQUIRE_TLS=1 to
    # refuse the connection entirely if the server does not offer TLS.
    local tls_line="set ftp:ssl-allow yes; set ftp:ssl-force no; set ssl:verify-certificate no;"
    if [ "${MACCABIPEDIA_FTP_REQUIRE_TLS:-0}" = "1" ]; then
        tls_line="set ftp:ssl-allow yes; set ftp:ssl-force yes; set ssl:verify-certificate no;"
    fi
    if [ "${MACCABIPEDIA_FTP_TLS_VERIFY:-0}" = "1" ]; then
        tls_line="${tls_line//verify-certificate no/verify-certificate yes}"
    fi
    lftp -u "${MACCABIPEDIA_FTP_USER},${MACCABIPEDIA_FTP_PASS}" \
         "${MACCABIPEDIA_FTP_HOST}" \
         -e "${tls_line} set net:max-retries 3; set net:timeout 20; ${script}; bye"
}

op_mirror_dir() {
    require_env MACCABIPEDIA_FTP_HOST MACCABIPEDIA_FTP_USER MACCABIPEDIA_FTP_PASS MACCABIPEDIA_FTP_REMOTE_ROOT
    local remote_sub="$1"
    local local_sub="$2"
    local remote="${MACCABIPEDIA_FTP_REMOTE_ROOT%/}/${remote_sub}"
    local local_dir="${SYNCED_DIR}/${local_sub}"

    mkdir -p "$local_dir"
    echo "==> lftp mirror  ${remote}  ->  ${local_dir}"
    run_lftp "mirror --verbose --only-missing --parallel=4 '${remote}' '${local_dir}'"
    log_event "mirror" "${remote}" "${local_dir}"
}

op_localsettings() {
    require_env MACCABIPEDIA_FTP_HOST MACCABIPEDIA_FTP_USER MACCABIPEDIA_FTP_PASS MACCABIPEDIA_FTP_REMOTE_ROOT
    local remote="${MACCABIPEDIA_FTP_REMOTE_ROOT%/}/LocalSettings.php"
    local local_file="${SYNCED_DIR}/LocalSettings.prod-snapshot.php"

    mkdir -p "${SYNCED_DIR}"
    echo "==> lftp get  ${remote}  ->  ${local_file}"
    run_lftp "get '${remote}' -o '${local_file}'"
    log_event "get" "${remote}" "${local_file}"
    echo "   snapshot saved. Scrub secrets before committing anything derived from it."
}

op_versions() {
    require_env MACCABIPEDIA_FTP_HOST MACCABIPEDIA_FTP_USER MACCABIPEDIA_FTP_PASS MACCABIPEDIA_FTP_REMOTE_ROOT
    local remote="${MACCABIPEDIA_FTP_REMOTE_ROOT%/}"
    echo "==> lftp cls -l  ${remote}"
    run_lftp "cls -l '${remote}'"
    log_event "list" "${remote}" ""
}

op_pages() {
    local manifest="${1-}"
    if [ -z "$manifest" ]; then
        echo "ERROR: 'pages' op requires a manifest file path" >&2
        echo "       example: $0 pages scripts/content-manifests/starter.txt" >&2
        exit 1
    fi
    if [ ! -f "$manifest" ]; then
        echo "ERROR: manifest not found: $manifest" >&2
        exit 1
    fi

    local base_url="${MACCABIPEDIA_WEB_URL:-https://maccabipedia.co.il}"
    local export_url="${base_url%/}/index.php?title=Special:Export"
    local out_dir="${SYNCED_DIR}/pages"
    local stem
    stem="$(basename "$manifest")"
    stem="${stem%.txt}"
    local out_file="${out_dir}/${stem}.xml"

    mkdir -p "$out_dir"

    # Strip comments / blanks from the manifest before sending. Special:Export
    # treats each non-empty line as a page title. Use a script-level temp var
    # so the EXIT trap can reference it without tripping `set -u`.
    cleaned="$(mktemp)"
    trap 'rm -f "${cleaned:-}"' EXIT
    grep -vE '^\s*(#|$)' "$manifest" > "$cleaned"

    local title_count
    title_count=$(wc -l < "$cleaned")
    if [ "$title_count" -eq 0 ]; then
        echo "ERROR: manifest contains no page titles after stripping comments/blanks" >&2
        exit 1
    fi

    echo "==> GET ${export_url}"
    echo "    titles: ${title_count}  ->  ${out_file}"

    # GET with -G: curl appends --data* as query params. POST was silently
    # returning the HTML form on this site (prod has an edge layer that
    # rejects the POST form submission); GET with the same params works.
    curl -fsSLG \
        --data-urlencode "pages@${cleaned}" \
        --data "curonly=1" \
        --data "templates=1" \
        --data "action=submit" \
        -o "$out_file" \
        "$export_url"

    # Quick sanity check: Special:Export returns MediaWiki XML on success; if
    # the server returned an HTML error page, the opening tag will be wrong.
    if ! head -c 256 "$out_file" | grep -q '<mediawiki'; then
        echo "ERROR: response is not a MediaWiki XML dump — check ${out_file}" >&2
        exit 1
    fi

    local size
    size=$(wc -c < "$out_file")
    echo "    OK — ${size} bytes"
    log_event "export" "${export_url}" "${out_file}"
}

if [ $# -lt 1 ]; then
    usage
    exit 1
fi

op="$1"
shift

case "$op" in
    skins)         op_mirror_dir "skins"             "skins" ;;
    extensions)    op_mirror_dir "extensions"        "extensions" ;;
    logo-assets)   op_mirror_dir "resources/assets"  "resources/assets" ;;
    localsettings) op_localsettings ;;
    versions)      op_versions ;;
    pages)         op_pages "$@" ;;
    -h|--help|help)
        usage
        exit 0
        ;;
    *)
        echo "ERROR: unknown op '$op'" >&2
        echo >&2
        usage >&2
        exit 1
        ;;
esac

echo "done."
