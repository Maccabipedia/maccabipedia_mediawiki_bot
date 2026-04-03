#!/usr/bin/env bash
# WorktreeCreate hook — creates worktree at sibling directory with config and venv
#
# Receives JSON on stdin with: cwd, worktree_path, session_id
# Must output the actual worktree path to stdout

set -euo pipefail

INPUT=$(cat)
REPO_ROOT=$(echo "$INPUT" | jq -r '.cwd')
WORKTREE_NAME=$(echo "$INPUT" | jq -r '.name')

REPO_NAME=$(basename "$REPO_ROOT")
WT_ROOT="$(dirname "$REPO_ROOT")/${REPO_NAME}-wt"
WT_DIR="${WT_ROOT}/${WORKTREE_NAME}"

if [ -d "$WT_DIR" ]; then
    echo "$WT_DIR"
    exit 0
fi

mkdir -p "$WT_ROOT"

# Create worktree with new branch from HEAD
git -C "$REPO_ROOT" worktree add -b "$WORKTREE_NAME" "$WT_DIR" HEAD >&2

# Copy gitignored .claude config
SRC="${REPO_ROOT}/.claude/settings.local.json"
if [ -f "$SRC" ]; then
    mkdir -p "${WT_DIR}/.claude"
    cp "$SRC" "${WT_DIR}/.claude/settings.local.json"
    echo "  copied settings.local.json" >&2
fi

# Symlink .venv
if [ -d "${REPO_ROOT}/.venv" ] && [ ! -e "${WT_DIR}/.venv" ]; then
    ln -s "${REPO_ROOT}/.venv" "${WT_DIR}/.venv"
    echo "  linked .venv" >&2
fi

# Output the worktree path (required by Claude Code)
echo "$WT_DIR"
