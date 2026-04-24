#!/bin/bash
set -euo pipefail

GENERATED_DIR=/generated
INSTALLED_MARKER="${GENERATED_DIR}/.installed"
ACTIVE_LS=/var/www/html/LocalSettings.php
STUB=/var/www/html/LocalSettings.stub.php

mkdir -p "$GENERATED_DIR"

if [ ! -f "$STUB" ]; then
    echo "[entrypoint] ERROR: $STUB not bind-mounted — check docker-compose.yml" >&2
    exit 1
fi

# First-boot install — writes the MediaWiki schema into the DB. The generated
# LocalSettings.php from install.php goes to /tmp and is discarded; our
# split-config stub is copied into place below. A marker file in the
# persistent /generated volume tracks install state across container
# restarts, so we don't re-run install.php every boot.
if [ ! -f "$INSTALLED_MARKER" ]; then
    echo "[entrypoint] First boot — running MediaWiki install.php"

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
        --confpath=/tmp \
        "${MW_SITE_NAME}" \
        "${MW_ADMIN_USER}"

    touch "$INSTALLED_MARKER"
    echo "[entrypoint] Install complete."
fi

# Copy the split-config stub into place every boot. /var/www/html/ is image
# filesystem and resets on container recreation, so this must run each time.
# A real file (not symlink) is required: PHP's __DIR__ resolves to the real
# path of the script, so symlinking the stub would break the sibling
# require_once of LocalSettings.env.local.php / LocalSettings.shared.php
# which are bind-mounted as siblings in /var/www/html/.
cp "$STUB" "$ACTIVE_LS"

# Safety net: if someone edits the stub and breaks PHP syntax, catch it at
# boot rather than at page load time.
if ! php -l "$ACTIVE_LS" >/dev/null; then
    echo "[entrypoint] ERROR: $ACTIVE_LS failed php -l syntax check" >&2
    exit 1
fi

echo "[entrypoint] Running maintenance/update.php --quick"
php maintenance/update.php --quick

exec "$@"
