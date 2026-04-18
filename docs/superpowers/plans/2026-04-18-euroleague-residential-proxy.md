# Euroleague Residential Proxy — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run a tiny always-on HTTP proxy on a residential PC so GitHub Actions CI can crawl `euroleaguebasketball.net` (Vercel WAF blocks all datacenter IPs).

**Architecture:** A Python stdlib proxy server runs in WSL2 as a systemd service, exposed via a permanent Cloudflare Tunnel URL. `crawl_euroleague.py`'s `fetch_html()` rewrites URLs through the proxy when `EUROLEAGUE_PROXY_URL` is set. CI sends requests through the tunnel; the server forwards them from the residential IP and returns the raw response.

**Tech Stack:** Python 3 stdlib (`http.server`, `urllib.request`), systemd, cloudflared, GitHub Actions secrets.

---

## File Map

| Action | Path | Responsibility |
|--------|------|---------------|
| Merge | (entire `remove-euroleague-from-ci` branch) | Basketball crawl+upload machinery |
| Modify | `packages/maccabipediabot/src/maccabipediabot/basketball/crawl_euroleague.py` | Add proxy support to `fetch_html()` |
| Modify | `packages/maccabipediabot/tests/basketball/test_crawl_euroleague.py` | Tests for proxy URL rewriting |
| Create | `infra/euroleague-proxy/server.py` | Proxy server (stdlib only) |
| Create | `infra/euroleague-proxy/euroleague-proxy.service` | systemd unit (Restart=always) |
| Create | `infra/euroleague-proxy/cloudflared.service` | systemd unit for tunnel |
| Create | `infra/euroleague-proxy/install.sh` | One-shot WSL2 setup script |
| Create | `infra/euroleague-proxy/start-wsl.bat` | Windows Task Scheduler trigger |
| Modify | `.github/workflows/basketball_games_uploader.yaml` | Restore euroleague steps + proxy env vars |

---

## Task 1: Merge basketball machinery from `remove-euroleague-from-ci`

The `crawl_euroleague.py` and all supporting files (translations, _crawler_utils, gamesbot updates, tests, fixtures) live on the `remove-euroleague-from-ci` branch, not master. Merge it as the base.

**Files:** (all files listed in the file map above originate here)

- [ ] **Step 1: Merge the branch**

```bash
git merge origin/remove-euroleague-from-ci --no-edit
```

Expected: merge commit created with no conflicts (branches diverge from the same master base).

- [ ] **Step 2: Verify tests pass**

```bash
uv run pytest packages/maccabipediabot/tests/basketball/ -v
```

Expected: all tests pass.

- [ ] **Step 3: Commit if merge left unstaged changes**

If `git status` shows nothing staged, the merge commit already captured everything — skip this step.

---

## Task 2: Add proxy support to `fetch_html()`

Modify `fetch_html()` to rewrite the URL through the proxy when `EUROLEAGUE_PROXY_URL` is set. The rest of `crawl_euroleague.py` is untouched.

**Files:**
- Modify: `packages/maccabipediabot/src/maccabipediabot/basketball/crawl_euroleague.py`
- Modify: `packages/maccabipediabot/tests/basketball/test_crawl_euroleague.py`

- [ ] **Step 1: Write the failing tests**

Add to `packages/maccabipediabot/tests/basketball/test_crawl_euroleague.py`:

```python
from unittest.mock import MagicMock, patch


def _mock_response(text: str = "<html/>") -> MagicMock:
    m = MagicMock()
    m.text = text
    m.raise_for_status = MagicMock()
    return m


def test_fetch_html_rewrites_url_and_adds_auth_when_proxy_set(monkeypatch):
    monkeypatch.setenv("EUROLEAGUE_PROXY_URL", "https://proxy.example.com")
    monkeypatch.setenv("EUROLEAGUE_PROXY_TOKEN", "tok123")
    captured: dict = {}

    def fake_get(url, headers, timeout):
        captured["url"] = url
        captured["headers"] = headers
        return _mock_response()

    with patch("maccabipediabot.basketball.crawl_euroleague.requests.get", fake_get):
        from maccabipediabot.basketball.crawl_euroleague import fetch_html
        fetch_html("https://www.euroleaguebasketball.net/en/euroleague/teams/maccabi/games/tel/")

    assert captured["url"] == "https://proxy.example.com/proxy/en/euroleague/teams/maccabi/games/tel/"
    assert captured["headers"]["Authorization"] == "Bearer tok123"


def test_fetch_html_hits_euroleague_directly_when_no_proxy(monkeypatch):
    monkeypatch.delenv("EUROLEAGUE_PROXY_URL", raising=False)
    captured: dict = {}

    def fake_get(url, headers, timeout):
        captured["url"] = url
        captured["headers"] = headers
        return _mock_response()

    with patch("maccabipediabot.basketball.crawl_euroleague.requests.get", fake_get):
        from maccabipediabot.basketball.crawl_euroleague import fetch_html
        fetch_html("https://www.euroleaguebasketball.net/en/euroleague/teams/maccabi/games/tel/")

    assert captured["url"] == "https://www.euroleaguebasketball.net/en/euroleague/teams/maccabi/games/tel/"
    assert "Authorization" not in captured["headers"]
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
uv run pytest packages/maccabipediabot/tests/basketball/test_crawl_euroleague.py \
  -k "test_fetch_html" -v
```

Expected: `FAILED` — `fetch_html` doesn't yet rewrite URLs.

- [ ] **Step 3: Implement proxy support in `fetch_html()`**

In `packages/maccabipediabot/src/maccabipediabot/basketball/crawl_euroleague.py`:

Add `import os` after the existing `import argparse` line.

Replace the existing `fetch_html` function (lines 55–58):

```python
_EUROLEAGUE_BASE = "https://www.euroleaguebasketball.net"


def fetch_html(url: str) -> str:
    proxy_url = os.environ.get("EUROLEAGUE_PROXY_URL")
    if proxy_url:
        path = url.removeprefix(_EUROLEAGUE_BASE)
        url = f"{proxy_url.rstrip('/')}/proxy{path}"
        headers = {**HTTP_HEADERS, "Authorization": f"Bearer {os.environ['EUROLEAGUE_PROXY_TOKEN']}"}
    else:
        headers = HTTP_HEADERS
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.text
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
uv run pytest packages/maccabipediabot/tests/basketball/test_crawl_euroleague.py -v
```

Expected: all tests pass including the two new ones.

- [ ] **Step 5: Check types**

```bash
uv run mypy packages/maccabipediabot/src/maccabipediabot/basketball/crawl_euroleague.py
```

Expected: `Success: no issues found`.

- [ ] **Step 6: Commit**

```bash
git add packages/maccabipediabot/src/maccabipediabot/basketball/crawl_euroleague.py \
        packages/maccabipediabot/tests/basketball/test_crawl_euroleague.py
git commit -m "feat(basketball): route euroleague fetch through residential proxy when EUROLEAGUE_PROXY_URL set"
```

---

## Task 3: Proxy server

A self-contained Python stdlib HTTP server — no dependencies, runs with bare `python3`.

**Files:**
- Create: `infra/euroleague-proxy/server.py`

- [ ] **Step 1: Create `infra/euroleague-proxy/server.py`**

```python
#!/usr/bin/env python3
import os
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

_TOKEN = os.environ["EUROLEAGUE_PROXY_TOKEN"]
_PORT = int(os.environ.get("EUROLEAGUE_PROXY_PORT", "8787"))
_TARGET_HOST = "https://www.euroleaguebasketball.net"
_STRIP_HEADERS = {"authorization", "host"}


class _ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.headers.get("Authorization") != f"Bearer {_TOKEN}":
            self.send_response(401)
            self.end_headers()
            return

        if not self.path.startswith("/proxy/"):
            self.send_response(404)
            self.end_headers()
            return

        target_url = _TARGET_HOST + self.path[len("/proxy"):]
        forward_headers = {
            k: v for k, v in self.headers.items()
            if k.lower() not in _STRIP_HEADERS
        }
        req = urllib.request.Request(target_url, headers=forward_headers)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read()
                self.send_response(resp.status)
                self.send_header("Content-Type", resp.headers.get("Content-Type", "text/html"))
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
        except urllib.error.HTTPError as exc:
            self.send_response(exc.code)
            self.end_headers()

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"{self.address_string()} {fmt % args}", flush=True)


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", _PORT), _ProxyHandler)
    print(f"Listening on port {_PORT}", flush=True)
    server.serve_forever()
```

- [ ] **Step 2: Smoke-test the server locally**

In one terminal:
```bash
EUROLEAGUE_PROXY_TOKEN=test123 python3 infra/euroleague-proxy/server.py
```

In another:
```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8787/proxy/en/test
```
Expected: `200` or `404` from euroleague (anything except a connection error confirms the server runs and auth passed).

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8787/proxy/en/test
```
Expected: `401` (no auth header).

- [ ] **Step 3: Commit**

```bash
git add infra/euroleague-proxy/server.py
git commit -m "feat(basketball): add euroleague residential proxy server"
```

---

## Task 4: Systemd units

**Files:**
- Create: `infra/euroleague-proxy/euroleague-proxy.service`
- Create: `infra/euroleague-proxy/cloudflared.service`

- [ ] **Step 1: Create `infra/euroleague-proxy/euroleague-proxy.service`**

```ini
[Unit]
Description=Euroleague residential HTTP proxy
After=network.target

[Service]
EnvironmentFile=/etc/euroleague-proxy.env
ExecStart=/usr/bin/python3 /opt/euroleague-proxy/server.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

- [ ] **Step 2: Create `infra/euroleague-proxy/cloudflared.service`**

```ini
[Unit]
Description=Cloudflare Tunnel for Euroleague proxy
After=network.target

[Service]
ExecStart=/usr/local/bin/cloudflared tunnel run maccabipedia-euroleague
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

- [ ] **Step 3: Commit**

```bash
git add infra/euroleague-proxy/euroleague-proxy.service \
        infra/euroleague-proxy/cloudflared.service
git commit -m "feat(basketball): add systemd units for proxy and cloudflare tunnel"
```

---

## Task 5: Install script and Windows auto-start

**Files:**
- Create: `infra/euroleague-proxy/install.sh`
- Create: `infra/euroleague-proxy/start-wsl.bat`

- [ ] **Step 1: Create `infra/euroleague-proxy/install.sh`**

```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if ! command -v cloudflared >/dev/null 2>&1; then
    echo "Installing cloudflared..."
    curl -fsSL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 \
        -o /usr/local/bin/cloudflared
    chmod +x /usr/local/bin/cloudflared
fi

mkdir -p /opt/euroleague-proxy
cp "$SCRIPT_DIR/server.py" /opt/euroleague-proxy/server.py

if [ ! -f /etc/euroleague-proxy.env ]; then
    read -rp "Enter EUROLEAGUE_PROXY_TOKEN (shared secret for CI): " token
    printf 'EUROLEAGUE_PROXY_TOKEN=%s\nEUROLEAGUE_PROXY_PORT=8787\n' "$token" \
        > /etc/euroleague-proxy.env
    chmod 600 /etc/euroleague-proxy.env
fi

cp "$SCRIPT_DIR/euroleague-proxy.service" /etc/systemd/system/
cp "$SCRIPT_DIR/cloudflared.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now euroleague-proxy cloudflared

echo ""
echo "=== Services installed and started ==="
systemctl status euroleague-proxy --no-pager
echo ""
echo "=== One-time Cloudflare setup (skip if already done) ==="
echo "  cloudflared login"
echo "  cloudflared tunnel create maccabipedia-euroleague"
echo "  cloudflared tunnel route dns maccabipedia-euroleague <your-hostname>"
echo ""
echo "Then add to GitHub secrets:"
echo "  EUROLEAGUE_PROXY_URL=https://<your-hostname>"
echo "  EUROLEAGUE_PROXY_TOKEN=<the token you just entered>"
```

- [ ] **Step 2: Make install script executable**

```bash
chmod +x infra/euroleague-proxy/install.sh
```

- [ ] **Step 3: Create `infra/euroleague-proxy/start-wsl.bat`**

```bat
wsl.exe --exec /usr/bin/true
```

This wakes WSL2 on Windows logon so systemd starts the services. Add it to Windows Task Scheduler: Trigger = "At log on", Action = run this `.bat` file.

- [ ] **Step 4: Commit**

```bash
git add infra/euroleague-proxy/install.sh infra/euroleague-proxy/start-wsl.bat
git commit -m "feat(basketball): add proxy install script and Windows auto-start bat"
```

---

## Task 6: Restore euroleague steps in CI workflow

PR #98 (`remove-euroleague-from-ci`) removed the two euroleague steps. Now that we have the proxy, add them back with proxy env vars.

**Files:**
- Modify: `.github/workflows/basketball_games_uploader.yaml`

- [ ] **Step 1: Add euroleague steps back to the workflow**

In `.github/workflows/basketball_games_uploader.yaml`, add the following two steps after the `Upload basket.co.il games` step, replacing the comment block:

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

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/basketball_games_uploader.yaml
git commit -m "ci(basketball): restore euroleague steps using residential proxy"
```

---

## Task 7: Final verification

- [ ] **Step 1: Run full test suite**

```bash
uv run pytest packages/maccabipediabot/tests/ -v
```

Expected: all tests pass.

- [ ] **Step 2: Run mypy**

```bash
uv run mypy packages/maccabipediabot/src/
```

Expected: no new errors beyond any pre-existing ones on the merged branch.

- [ ] **Step 3: Push branch and open PR**

```bash
git push -u origin run-euroleague-remotely
```

Then open a PR against `master`. The PR description should note:
- Merges `remove-euroleague-from-ci` basketball machinery
- Adds residential proxy server in `infra/euroleague-proxy/`
- Adds `EUROLEAGUE_PROXY_URL` + `EUROLEAGUE_PROXY_TOKEN` to GitHub secrets (manual step)
- Closes PR #98

- [ ] **Step 4: After the proxy is running locally, verify CI end-to-end**

Trigger `basketball_games_uploader` via `workflow_dispatch` and confirm both basket.co.il and Euroleague steps pass.
