#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

apt-get install -y tinyproxy

if ! command -v cloudflared >/dev/null 2>&1; then
    echo "Installing cloudflared..."
    curl -fsSL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 \
        -o /usr/local/bin/cloudflared
    chmod +x /usr/local/bin/cloudflared
fi

if [ ! -f /etc/tinyproxy/maccabipedia.conf ]; then
    read -rp "Enter proxy username: " proxy_user
    read -rsp "Enter proxy password: " proxy_pass
    echo ""
    cat "$SCRIPT_DIR/tinyproxy.conf" > /etc/tinyproxy/maccabipedia.conf
    echo "BasicAuth $proxy_user $proxy_pass" >> /etc/tinyproxy/maccabipedia.conf
    chmod 600 /etc/tinyproxy/maccabipedia.conf
fi

cp "$SCRIPT_DIR/maccabipedia.filter" /etc/tinyproxy/maccabipedia.filter
cp "$SCRIPT_DIR/cloudflared.service" /etc/systemd/system/

systemctl daemon-reload
systemctl enable --now tinyproxy cloudflared

echo ""
echo "=== Services installed and started ==="
systemctl status tinyproxy --no-pager
echo ""
echo "=== One-time Cloudflare setup (skip if already done) ==="
echo "  cloudflared login"
echo "  cloudflared tunnel create maccabipedia-euroleague"
echo "  cloudflared tunnel route dns maccabipedia-euroleague <your-hostname>"
echo ""
echo "Then add to GitHub secrets:"
echo "  EUROLEAGUE_HTTPS_PROXY=http://<user>:<pass>@<your-hostname>"
