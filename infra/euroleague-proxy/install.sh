#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

apt-get install -y tinyproxy

if ! command -v tailscale >/dev/null 2>&1; then
    echo "Installing Tailscale..."
    curl -fsSL https://tailscale.com/install.sh | sh
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

cp "$SCRIPT_DIR/maccabipedia.filter" /etc/tinyproxy/maccabipedia.filter
cp "$SCRIPT_DIR/notify-failure@.service" /etc/systemd/system/

mkdir -p /etc/systemd/system/tinyproxy.service.d
echo '[Unit]' > /etc/systemd/system/tinyproxy.service.d/notify.conf
echo 'OnFailure=notify-failure@%n.service' >> /etc/systemd/system/tinyproxy.service.d/notify.conf

mkdir -p /etc/systemd/system/tailscaled.service.d
echo '[Unit]' > /etc/systemd/system/tailscaled.service.d/notify.conf
echo 'OnFailure=notify-failure@%n.service' >> /etc/systemd/system/tailscaled.service.d/notify.conf

systemctl daemon-reload
systemctl enable --now tinyproxy tailscaled

echo ""
echo "=== Done ==="
echo "Next: run 'tailscale up' to authenticate (one-time, browser will open)."
echo "Then get your stable Tailscale IP: tailscale ip -4"
echo "Set GitHub secrets:"
echo "  TAILSCALE_AUTHKEY — create at https://login.tailscale.com/admin/settings/keys (ephemeral, reusable)"
echo "  EUROLEAGUE_HTTPS_PROXY — http://<proxy-user>:<proxy-pass>@<tailscale-ip>:8787"
