# Euroleague Residential Proxy — Design Spec

## Problem

`euroleaguebasketball.net` runs on Vercel; its WAF returns 429 for every datacenter IP (GitHub Actions, CF Workers, Vercel functions, Israeli ISP hosting). Only residential IPs pass. CI cannot run the euroleague crawler directly.

## Solution

A tiny HTTP proxy server runs on the user's residential PC (WSL2), exposed via a permanent Cloudflare Tunnel URL. CI sends requests through the tunnel instead of hitting euroleaguebasketball.net directly.

---

## Architecture

```
GitHub Actions CI
    │  GET /proxy/en/euroleague/teams/...
    │  Authorization: Bearer <token>
    ▼
Cloudflare Tunnel (permanent public HTTPS URL)
    │
    ▼
cloudflared  (WSL2 systemd service)
    │  forwards to localhost:8787
    ▼
Proxy Server  (WSL2 systemd service, port 8787)
    │  validates token → strips Authorization + Host headers
    ▼
euroleaguebasketball.net  ← residential IP ✅
```

**Boot sequence:** Windows logon → Task Scheduler runs `start-wsl.bat` → WSL2 boots → systemd auto-starts both services → tunnel is live within ~10 s.

---

## Components

### 1. Proxy Server — `infra/euroleague-proxy/server.py`

- Python stdlib only (`http.server` + `urllib.request`), no dependencies, runs with bare `python3`
- Listens on `0.0.0.0:$EUROLEAGUE_PROXY_PORT` (default `8787`)
- Single route: `GET /proxy/<path>?<query>` (any method other than GET → 405)
- Auth: rejects requests without `Authorization: Bearer $EUROLEAGUE_PROXY_TOKEN` → 401
- Forwarding:
  - Target URL: `https://www.euroleaguebasketball.net/<path>?<query>` (host is hardcoded — cannot be redirected to arbitrary URLs)
  - Passes through all request headers except `Authorization` and `Host`
  - Returns raw status code, `Content-Type`, and body
- Logs every request + response status to stdout (captured by journald)

Config via env vars (loaded from `/etc/euroleague-proxy.env`):
- `EUROLEAGUE_PROXY_TOKEN` — required; shared secret
- `EUROLEAGUE_PROXY_PORT` — optional; default `8787`

### 2. `crawl_euroleague.py` — proxy hook

Modify `fetch_html(url: str) -> str` to support an optional proxy:

- If `EUROLEAGUE_PROXY_URL` env var is set:
  - Rewrite `url` by replacing the `https://www.euroleaguebasketball.net` prefix with `$EUROLEAGUE_PROXY_URL/proxy`
  - Add `Authorization: Bearer $EUROLEAGUE_PROXY_TOKEN` header
- Otherwise: fetch directly (unchanged behaviour for local runs)

No other changes to crawl logic. The proxy is invisible to all callers of `fetch_html`.

### 3. Systemd Units

**`infra/euroleague-proxy/euroleague-proxy.service`**
```
[Unit]
After=network.target

[Service]
EnvironmentFile=/etc/euroleague-proxy.env
ExecStart=/usr/bin/python3 /opt/euroleague-proxy/server.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**`infra/euroleague-proxy/cloudflared.service`**
```
[Unit]
After=network.target

[Service]
ExecStart=/usr/local/bin/cloudflared tunnel run maccabipedia-euroleague
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 4. Install Script — `infra/euroleague-proxy/install.sh`

One-shot setup (idempotent). Steps:
1. Installs `cloudflared` binary if missing (downloads from Cloudflare's release page)
2. Copies `server.py` to `/opt/euroleague-proxy/server.py`
3. Prompts for `EUROLEAGUE_PROXY_TOKEN`; writes `/etc/euroleague-proxy.env` (chmod 600)
4. Copies both `.service` files to `/etc/systemd/system/`
5. `systemctl daemon-reload && systemctl enable --now euroleague-proxy cloudflared`
6. Prints instructions for the one-time `cloudflared login` + `cloudflared tunnel create maccabipedia-euroleague` step

### 5. Windows Auto-Start — `infra/euroleague-proxy/start-wsl.bat`

A minimal `.bat` file the user drops into Task Scheduler (trigger: at logon, run whether or not user is logged in):
```bat
wsl.exe --distribution Ubuntu --exec /usr/bin/true
```
This wakes WSL2; systemd starts both services inside it automatically.

### 6. CI Workflow — `.github/workflows/basketball_games_uploader.yaml`

Restore the two euroleague steps (removed in PR #98), adding proxy env vars:

```yaml
- name: Crawl Euroleague (via residential proxy)
  env:
    EUROLEAGUE_PROXY_URL: ${{ secrets.EUROLEAGUE_PROXY_URL }}
    EUROLEAGUE_PROXY_TOKEN: ${{ secrets.EUROLEAGUE_PROXY_TOKEN }}
  run: |
    uv run python -m maccabipediabot.basketball.crawl_euroleague \
      --season latest --limit 1 --output /tmp/euroleague.json

- name: Upload Euroleague games
  env:
    PYWIKIBOT_DIR: packages/maccabipediabot/src/maccabipediabot/pywikibot_configs/
    MACCABIPEDIA_BOT_USERNAME: ${{ secrets.MACCABIPEDIA_BOT_USERNAME }}
    MACCABIPEDIA_BOT_PASSWORD: ${{ secrets.MACCABIPEDIA_BOT_PASSWORD }}
  run: |
    uv run python -m maccabipediabot.basketball.gamesbot_basketball \
      --input /tmp/euroleague.json --skip-existing
```

Two new GitHub secrets: `EUROLEAGUE_PROXY_URL` (permanent Cloudflare Tunnel URL) and `EUROLEAGUE_PROXY_TOKEN`.

---

## Security

- Proxy host is hardcoded to `euroleaguebasketball.net` — a leaked token cannot proxy arbitrary URLs
- `/etc/euroleague-proxy.env` is chmod 600, owned by root
- Token transmitted over HTTPS (Cloudflare Tunnel terminates TLS)

## Out of Scope

- `crawl_euroleague.py` logic (already implemented on the `remove-euroleague-from-ci` branch)
- Table standings (`update_euroleague_table_basketball.py`) — fetches livescore.com, not blocked
