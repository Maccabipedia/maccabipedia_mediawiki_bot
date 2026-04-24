<?php
# Bootstrap for production. Loads env-specific values first, then the
# site-wide shared config. All three files must be uploaded as siblings
# to the wiki root.
if (!defined('MEDIAWIKI')) { exit; }
require_once __DIR__ . '/LocalSettings.env.prod.php';
require_once __DIR__ . '/LocalSettings.shared.php';
