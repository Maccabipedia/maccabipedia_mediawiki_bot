#!/usr/bin/env bash
# open-in-browser.sh — Open a URL or file in the default Windows browser/app
#
# Usage: bash .claude/scripts/open-in-browser.sh <url-or-file-path>

if [ $# -lt 1 ]; then
    echo "Usage: bash .claude/scripts/open-in-browser.sh <url-or-file-path>"
    exit 1
fi

wslview "$1"
