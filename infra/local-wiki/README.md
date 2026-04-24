# Local MaccabiPedia (Docker) — v0

A minimal local MediaWiki 1.39.11 + MariaDB running in Docker, matching prod's
PHP 7.4 for extension parity. No prod skin/extensions/content yet — just a
blank wiki so we have something running to iterate from.

## Prerequisites

- **Linux / WSL (Ubuntu/Debian):** run `./scripts/setup-host.sh` once. It
  installs `docker.io`, `docker-compose-v2`, and `lftp`, starts the docker
  daemon, and adds you to the `docker` group. After running it for the first
  time, open a new shell (or `newgrp docker`) so `docker` works without sudo.
- **macOS / Windows:** install Docker Desktop manually (with WSL 2 integration
  on Windows). `lftp` is only needed for the prod-sync scripts and can be
  installed via Homebrew / Scoop when you reach that step.

## Bring it up

```bash
cd infra/local-wiki
docker compose up -d --build
```

First boot takes a few minutes — builds the PHP 7.4 + MW 1.39.11 image and
runs `maintenance/install.php`. Subsequent boots are fast.

Then open http://localhost:8080.

Admin user: `admin` / `devadminpass` (values from `docker-compose.yml`;
local-only, not secrets).

## Tear down

```bash
docker compose down          # keep data
docker compose down -v       # wipe DB + uploaded images + LocalSettings
```

## What's here

- `Dockerfile` — `FROM php:7.4-apache`, installs MW 1.39.11 + required PHP
  extensions (intl, gd, mysqli, zip, mbstring, calendar, opcache, apcu).
- `docker-compose.yml` — `mediawiki` service (built from `Dockerfile`) +
  `mariadb:10`. Three named volumes: `mw_db`, `mw_images`, `mw_config`
  (LocalSettings.php lives in `mw_config` so it survives container recreation).
- `entrypoint.sh` — on first boot runs `install.php`, appends dev overrides to
  the generated `LocalSettings.php`, symlinks it into place, then runs
  `update.php --quick` on every boot.
- `scripts/setup-host.sh` — one-shot host-prereq installer (docker, compose,
  lftp). Idempotent; safe to re-run.
- `scripts/sync-from-prod.sh` — named-op wrapper around `lftp` for pulling
  files from the production FTP server. See `.env.example` for the required
  environment variables; copy it to `.env` (gitignored) and `chmod 600`.

## Not here yet

- MaccabiPedia skin (pulled from prod via FTP in a future step)
- Extensions from prod (Cargo, ParserFunctions, etc.)
- Any seeded content
- Bot-target integration

These come in follow-up iterations once v0 is verified.
