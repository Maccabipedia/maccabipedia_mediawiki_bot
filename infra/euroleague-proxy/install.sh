#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

apt-get install -y tinyproxy

if ! command -v cloudflared >/dev/null 2>&1; then
    echo "Installing cloudflared..."
    curl -fsSL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 \
        -o /tmp/cloudflared
    install -m755 /tmp/cloudflared /usr/local/bin/cloudflared
fi

if ! command -v gh >/dev/null 2>&1; then
    echo "gh CLI not found — install it and run 'gh auth login' before continuing"
    exit 1
fi

if [ ! -f /etc/tinyproxy/maccabipedia.conf ]; then
    read -rp "Enter proxy username: " proxy_user
    read -rsp "Enter proxy password: " proxy_pass
    echo ""
    cat "$SCRIPT_DIR/tinyproxy.conf" > /etc/tinyproxy/maccabipedia.conf
    echo "BasicAuth $proxy_user $proxy_pass" >> /etc/tinyproxy/maccabipedia.conf
    chmod 600 /etc/tinyproxy/maccabipedia.conf
fi


mkdir -p /opt/euroleague-proxy
cp "$SCRIPT_DIR/maccabipedia.filter" /etc/tinyproxy/maccabipedia.filter
cp "$SCRIPT_DIR/start-tunnel.sh" /opt/euroleague-proxy/start-tunnel.sh
chmod +x /opt/euroleague-proxy/start-tunnel.sh
cp "$SCRIPT_DIR/cloudflared.service" /etc/systemd/system/
cp "$SCRIPT_DIR/notify-failure@.service" /etc/systemd/system/

systemctl daemon-reload
systemctl enable --now tinyproxy cloudflared

echo ""
echo "=== Done ==="
echo "On each reboot, the Cloudflare Quick Tunnel URL is captured and"
echo "EUROLEAGUE_HTTPS_PROXY in GitHub secrets is updated automatically."
echo "Check tunnel status: journalctl -u cloudflared -f"
