<?php
# Bootstrap stub. Copied into place by entrypoint.sh after install.php runs.
# Do NOT add config here — env-specific lines go in LocalSettings.env.*.php,
# everything else in LocalSettings.shared.php.
if (!defined('MEDIAWIKI')) { exit; }
require_once __DIR__ . '/LocalSettings.env.local.php';
require_once __DIR__ . '/LocalSettings.shared.php';
