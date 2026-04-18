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
