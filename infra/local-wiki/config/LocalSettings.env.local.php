<?php
# Env-specific config for the local docker wiki.
# Loaded by LocalSettings.php BEFORE LocalSettings.shared.php, so shared
# code can reference vars set here ($wgScriptPath, $wgDBname, etc).
#
# Prod gets its own sibling (LocalSettings.env.prod.php, never committed
# here) with the matching set of assignments. Keep the *set of variables*
# in lock-step with that file — add a var here only after the prod
# counterpart has a value for it.

if (!defined('MEDIAWIKI')) {
	exit;
}

## URL — no rewrite rules in the docker image, so article path keeps the
## /index.php/ segment. Prod uses "/$1" with mod_rewrite.
$wgServer = getenv('MW_SITE_SERVER') ?: 'http://localhost:8080';
$wgScriptPath = '';
$wgArticlePath = '/index.php/$1';

## Email — disabled locally, no SMTP reachable.
$wgEnableEmail = false;
$wgEmailAuthentication = false;
$wgEmergencyContact = 'dev@localhost';
$wgPasswordSender = 'dev@localhost';

## Database — values come from docker-compose environment.
$wgDBtype = 'mysql';
$wgDBserver = getenv('MW_DB_HOST') ?: 'mariadb';
$wgDBname = getenv('MW_DB_NAME') ?: 'maccabipedia';
$wgDBuser = getenv('MW_DB_USER') ?: 'mw';
$wgDBpassword = getenv('MW_DB_PASSWORD') ?: 'devpass';
$wgDBprefix = getenv('MW_DB_PREFIX') ?: 'MPMW_';

## Cache — disabled so edits and template changes show immediately.
$wgMainCacheType = CACHE_NONE;
$wgMemCachedServers = [];

## Secrets — placeholders only. Prod's env file carries the real values.
$wgSecretKey = 'dev-secret-not-a-real-key-local-only';
$wgUpgradeKey = 'dev-upgrade-key-local-only';

## Logging — no files written (no /MyLogs dir in the container). Errors
## surface on Apache's stderr, which docker compose captures.
$wgDBerrorLog = false;
$wgDebugLogGroups = [];
$wgResourceLoaderDebug = true;
$wgJobRunRate = 0;

## Verbose error output — local debugging.
$wgShowExceptionDetails = true;
$wgShowDBErrorBacktrace = true;
$wgShowSQLErrors = true;
$wgDevelopmentWarnings = true;

## SecureHTML — placeholder. The real prod secret never lives in this repo.
$wgSecureHTMLSecrets = [
	'Wiki admin' => 'dev-local-not-real',
];

## Google Analytics — empty id disables tracking from dev.
$wgGTagAnalyticsId = '';
