# Local MaccabiPedia (Docker)

Runs a local MediaWiki 1.39.11 + PHP 7.4 + MariaDB mirror of the production
MaccabiPedia site. Pulls prod's skin, extensions, `LocalSettings.php`, and
selected page wikitext over FTP + `Special:Export`; wraps them in a dev-safe
override layer so prod DB/URLs/secrets never leak into local runtime.

## Prerequisites

- **Linux / WSL (Ubuntu/Debian):** run `./scripts/setup-host.sh` once. It
  installs `docker.io`, `docker-compose-v2`, and `lftp`, starts the docker
  daemon, and adds you to the `docker` group. After running it for the first
  time, open a new shell (or `newgrp docker`) so `docker` works without sudo.
- **macOS / Windows:** install Docker Desktop manually (with WSL 2 integration
  on Windows). `lftp` is only needed for the prod-sync scripts and can be
  installed via Homebrew / Scoop when you reach that step.

## First-time setup

```bash
# Prereqs
cd infra/local-wiki
./scripts/setup-host.sh               # docker + lftp + group membership

# FTP credentials for pulling prod files
cp .env.example .env
chmod 600 .env                        # fill in host/user/pass/remote-root

# Pull prod code + config (skin, extensions, LocalSettings.php)
./scripts/sync-from-prod.sh skins
./scripts/sync-from-prod.sh extensions
./scripts/sync-from-prod.sh localsettings

# Bring up the stack (first build takes a few minutes)
docker compose up -d --build
```

Then open http://localhost:8080 — you'll see the `מכביפדיה` site with the
real Metrolook skin and prod's extension set, backed by a fresh empty DB.

Admin user: `admin` / `devadminpass` (from `docker-compose.yml`; local-only).

## Seed real content

After the wiki is up, pull page wikitext from prod and import it:

```bash
# Edit the starter manifest to add pages you care about
$EDITOR scripts/content-manifests/starter.txt

# Pull those pages + their referenced templates via Special:Export (HTTP)
./scripts/sync-from-prod.sh pages scripts/content-manifests/starter.txt

# Import the XML dump into the running container
./scripts/seed-content.sh starter
```

Now browse to a seeded page (e.g.
`http://localhost:8080/index.php/ערן_זהבי`) to see real content rendering
with the Metrolook skin.

**Limitation**: Cargo data tables aren't populated — only page wikitext
comes in via `Special:Export`. Populating Cargo requires a full DB dump
(see "Follow-ups" below).

## Tear down

```bash
docker compose down          # keep data
docker compose down -v       # wipe DB + uploaded images + LocalSettings
```

## Files

- `Dockerfile` — `FROM php:7.4.33-apache-bullseye`, installs MW 1.39.11 +
  PHP extensions (intl, gd, mysqli, zip, mbstring, calendar, opcache, apcu
  pinned to 5.1.24). Version tags pinned for reproducibility.
- `docker-compose.yml` — `mediawiki` (built from `Dockerfile`) + `mariadb:10.11`.
  Named volumes: `mw_db`, `mw_images`, `mw_config` (`LocalSettings.php` lives
  in `mw_config` so it survives container recreation). Mediawiki healthcheck
  polls `http://localhost/`.
- `entrypoint.sh` — on first boot runs `install.php` with prefix `MPMW_`,
  generates random `$wgSecretKey` / `$wgUpgradeKey`, appends dev overrides,
  requires the prod snapshot, re-asserts dev-only values AFTER the snapshot
  (managed-block — re-assert updates on env var change), syntax-checks the
  generated `LocalSettings.php`, then runs `update.php --quick`.
- `scripts/setup-host.sh` — one-shot host-prereq installer (docker, compose,
  lftp). Idempotent; safe to re-run.
- `scripts/sync-from-prod.sh` — named-op wrapper around `lftp` (+ `curl` for
  HTTP ops) for pulling files from prod. Download-only, scoped to a fixed
  menu of ops. See `.env.example` for the env vars.
  Ops: `skins`, `extensions`, `logo-assets`, `localsettings`, `versions`,
  `pages <manifest>`.
- `scripts/seed-content.sh` — imports pulled `synced/pages/*.xml` dumps into
  the running container via `importDump.php`, then `rebuildall.php` +
  `runJobs.php` to flush deferred work.
- `scripts/content-manifests/starter.txt` — editable list of page titles to
  pull; extend with games, seasons, stadiums, coaches, categories as needed.

## Follow-ups (not yet shipped)

- Split `LocalSettings.php` into a shared file (committed both sides) + an
  env-specific file per deployment. Removes the override dance in
  `entrypoint.sh`.
- Prod DB dump importer for full Cargo-table parity. Requires a `.sql` from
  the hosting panel's phpMyAdmin export.
- Bot-target integration: a `[maccabipedia-local]` profile in
  `pywikibot_configs/user-password.py` + `MACCABIPEDIA_SITE=local` env switch
  so the Python bots target the local wiki.
