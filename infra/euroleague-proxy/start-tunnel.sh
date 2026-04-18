#!/usr/bin/env bash
set -euo pipefail

PROXY_USER="$(grep ^BasicAuth /etc/tinyproxy/maccabipedia.conf | awk '{print $2}')"
PROXY_PASS="$(grep ^BasicAuth /etc/tinyproxy/maccabipedia.conf | awk '{print $3}')"

cloudflared tunnel --url http://localhost:8787 --no-autoupdate 2>&1 | while IFS= read -r line; do
    echo "$line"
    if [[ "$line" =~ https://[a-z0-9-]+\.trycloudflare\.com ]]; then
        url="${BASH_REMATCH[0]}"
        host="${url#https://}"
        secret="http://${PROXY_USER}:${PROXY_PASS}@${host}"
        gh secret set EUROLEAGUE_HTTPS_PROXY \
            --body "$secret" \
            --repo Maccabipedia/maccabipedia_mediawiki_bot
        echo "GitHub secret EUROLEAGUE_HTTPS_PROXY updated to $host"
    fi
done
