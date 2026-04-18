#!/bin/bash
# Crawl + upload latest Euroleague Maccabi games. MUST run from a residential
# network — euroleaguebasketball.net's Vercel WAF blocks every datacenter IP
# we tested (GH Actions, CF Workers/Browser Run, Vercel functions, regional
# Israeli ISP hosting), so this can't live in CI.
#
# Usage:
#   ./scripts/run_euroleague_locally.sh           # latest 1 game
#   ./scripts/run_euroleague_locally.sh 5         # latest 5 games
#
# Idempotent — `--skip-existing` means already-uploaded games are skipped, so
# scheduling this on a cron / Windows Task Scheduler is safe.
set -euo pipefail

LIMIT="${1:-1}"
JSON_FILE="$(mktemp -t euroleague.XXXXXX.json)"
trap 'rm -f "$JSON_FILE"' EXIT

uv run python -m maccabipediabot.basketball.crawl_euroleague \
    --season latest --limit "$LIMIT" --output "$JSON_FILE"

uv run python -m maccabipediabot.basketball.gamesbot_basketball \
    --input "$JSON_FILE" --skip-existing
