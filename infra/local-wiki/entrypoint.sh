#!/bin/bash
set -euo pipefail

GENERATED_DIR=/generated
GENERATED_LS="${GENERATED_DIR}/LocalSettings.php"
KEYS_FILE="${GENERATED_DIR}/dev-keys.php"
ACTIVE_LS=/var/www/html/LocalSettings.php
SNAPSHOT=/var/www/html/LocalSettings.prod-snapshot.php

mkdir -p "$GENERATED_DIR"

# append_once: for static blocks whose contents never depend on runtime state.
append_once() {
    local marker="$1"
    local block="$2"
    if ! grep -qF "$marker" "$GENERATED_LS"; then
        printf '\n%s\n%s\n' "$marker" "$block" >> "$GENERATED_LS"
    fi
}

# replace_trailing_block: for blocks whose content may change across boots
# (e.g. the dev re-assert block that pulls DB creds / URL from env vars).
# Truncates the file from the marker line onward, then re-appends fresh.
# Requires the block to be the *last* thing in the file.
replace_trailing_block() {
    local marker="$1"
    local block="$2"
    if grep -qF "$marker" "$GENERATED_LS"; then
        local line
        line=$(grep -nF "$marker" "$GENERATED_LS" | head -n1 | cut -d: -f1)
        head -n "$((line - 1))" "$GENERATED_LS" > "${GENERATED_LS}.tmp"
        mv "${GENERATED_LS}.tmp" "$GENERATED_LS"
    fi
    printf '\n%s\n%s\n' "$marker" "$block" >> "$GENERATED_LS"
}

if [ ! -f "$GENERATED_LS" ]; then
    echo "[entrypoint] No LocalSettings.php found — running MediaWiki install.php"

    php maintenance/install.php \
        --dbtype=mysql \
        --dbserver="${MW_DB_HOST}" \
        --dbname="${MW_DB_NAME}" \
        --dbuser="${MW_DB_USER}" \
        --dbpass="${MW_DB_PASSWORD}" \
        --dbprefix="${MW_DB_PREFIX:-}" \
        --installdbuser="${MW_DB_USER}" \
        --installdbpass="${MW_DB_PASSWORD}" \
        --server="${MW_SITE_SERVER}" \
        --scriptpath="" \
        --lang="${MW_SITE_LANG}" \
        --pass="${MW_ADMIN_PASSWORD}" \
        --confpath="${GENERATED_DIR}" \
        "${MW_SITE_NAME}" \
        "${MW_ADMIN_USER}"

    if [ ! -s "$GENERATED_LS" ]; then
        echo "[entrypoint] ERROR: install.php exited 0 but did not write a non-empty $GENERATED_LS" >&2
        exit 1
    fi

    echo "[entrypoint] Install complete."
fi

# Generate dev-only keys once, persist across container restarts. These go in
# a separate file that the re-assert block will require_once; that way the
# re-assert block itself stays env-derived and idempotent-across-boots while
# the keys remain stable (regenerating would invalidate all local sessions).
if [ ! -f "$KEYS_FILE" ]; then
    secret="$(openssl rand -hex 32)"
    upgrade="$(openssl rand -hex 16)"
    {
        echo '<?php'
        echo "// Auto-generated on first boot by entrypoint.sh. Local dev only."
        echo "\$wgSecretKey = '${secret}';"
        echo "\$wgUpgradeKey = '${upgrade}';"
    } > "$KEYS_FILE"
    unset secret upgrade
fi

# First layer of dev overrides — applied even when no prod snapshot is present.
append_once "# --- dev overrides (appended by entrypoint.sh) ---" \
'$wgMainCacheType = CACHE_NONE;
$wgShowExceptionDetails = true;
$wgShowDBErrorBacktrace = true;
$wgShowSQLErrors = true;
$wgDevelopmentWarnings = true;'

# If the prod snapshot is mounted we load it, then re-assert dev-only values
# AFTER the include so that prod secrets/URLs don't leak into runtime. PHP
# executes top-to-bottom and the last assignment wins, so this block is our
# "sanitization by override" in place of editing the snapshot on disk.
if [ -f "$SNAPSHOT" ]; then
    append_once "# --- prod snapshot include ---" \
"if ( is_readable( '${SNAPSHOT}' ) ) {
    require_once '${SNAPSHOT}';
}"

    # Re-assert block uses managed-block replacement so changing env vars in
    # docker-compose.yml / .env actually takes effect on next `docker compose
    # up` rather than silently keeping the first-boot values.
    replace_trailing_block "# --- dev re-assert AFTER prod snapshot (wins by load order) ---" \
"\$wgServer = '${MW_SITE_SERVER}';
\$wgScriptPath = '';
\$wgArticlePath = '/index.php/\$1';
\$wgDBtype = 'mysql';
\$wgDBserver = '${MW_DB_HOST}';
\$wgDBname = '${MW_DB_NAME}';
\$wgDBuser = '${MW_DB_USER}';
\$wgDBpassword = '${MW_DB_PASSWORD}';
\$wgDBprefix = '${MW_DB_PREFIX:-}';
require_once '${KEYS_FILE}';
\$wgMainCacheType = CACHE_NONE;
\$wgMemCachedServers = [];
\$wgCacheDirectory = false;
\$wgDBerrorLog = false;
\$wgDebugLogFile = '';
\$wgDebugLogGroups = [];
\$wgShowExceptionDetails = true;
\$wgShowDBErrorBacktrace = true;
\$wgShowSQLErrors = true;
\$wgDevelopmentWarnings = true;"
else
    # No snapshot — load just the skin so the wiki at least has branding.
    if [ -d /var/www/html/skins/Metrolook ]; then
        append_once "# --- skin: Metrolook (fallback when no snapshot) ---" \
"wfLoadSkin( 'Metrolook' );
\$wgDefaultSkin = 'metrolook';"
    fi
fi

# Syntax-check the generated LocalSettings before symlinking it into place or
# running update.php. A typo in an env var interpolation could otherwise
# leave MW loading a PHP parse error and serving 500s without a clear cause.
if ! php -l "$GENERATED_LS" >/dev/null; then
    echo "[entrypoint] ERROR: $GENERATED_LS failed php -l syntax check" >&2
    exit 1
fi

ln -sf "$GENERATED_LS" "$ACTIVE_LS"

if [ ! -e "$ACTIVE_LS" ]; then
    echo "[entrypoint] ERROR: $ACTIVE_LS is a dangling symlink after ln -sf" >&2
    exit 1
fi

echo "[entrypoint] Running maintenance/update.php --quick"
php maintenance/update.php --quick

exec "$@"
