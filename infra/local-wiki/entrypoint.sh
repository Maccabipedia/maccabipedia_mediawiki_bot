#!/bin/bash
set -euo pipefail

GENERATED_DIR=/generated
GENERATED_LS="${GENERATED_DIR}/LocalSettings.php"
ACTIVE_LS=/var/www/html/LocalSettings.php
SNAPSHOT=/var/www/html/LocalSettings.prod-snapshot.php

mkdir -p "$GENERATED_DIR"

append_once() {
    local marker="$1"
    local block="$2"
    if ! grep -qF "$marker" "$GENERATED_LS"; then
        printf '\n%s\n%s\n' "$marker" "$block" >> "$GENERATED_LS"
    fi
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

    echo "[entrypoint] Install complete."
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

    append_once "# --- dev re-assert AFTER prod snapshot (wins by load order) ---" \
"\$wgServer = '${MW_SITE_SERVER}';
\$wgScriptPath = '';
\$wgArticlePath = '/index.php/\$1';
\$wgDBtype = 'mysql';
\$wgDBserver = '${MW_DB_HOST}';
\$wgDBname = '${MW_DB_NAME}';
\$wgDBuser = '${MW_DB_USER}';
\$wgDBpassword = '${MW_DB_PASSWORD}';
\$wgDBprefix = '${MW_DB_PREFIX:-}';
\$wgSecretKey = 'dev-secret-not-a-real-key-local-only';
\$wgUpgradeKey = 'dev-upgrade-key-local-only';
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

ln -sf "$GENERATED_LS" "$ACTIVE_LS"

echo "[entrypoint] Running maintenance/update.php --quick"
php maintenance/update.php --quick

exec "$@"
