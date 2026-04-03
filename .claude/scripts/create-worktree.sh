#!/usr/bin/env bash
# create-worktree.sh — Create a git worktree with .claude config and venv
#
# Usage: bash .claude/scripts/create-worktree.sh <branch-name> [base-branch]
#   branch-name  — name for the new branch and worktree directory
#   base-branch  — branch to base off (default: master)
#
# Creates worktree at: ../maccabipedia_mediawikibot-wt/<branch-name>
# Copies .claude/ config (settings.local.json, etc.) and symlinks .venv

set -euo pipefail

if [ $# -lt 1 ]; then
    echo "Usage: bash .claude/scripts/create-worktree.sh <branch-name> [base-branch]"
    exit 1
fi

BRANCH="$1"
BASE="${2:-master}"

# Resolve paths
REPO_ROOT="$(git rev-parse --show-toplevel)"
REPO_NAME="$(basename "$REPO_ROOT")"
WT_ROOT="$(dirname "$REPO_ROOT")/${REPO_NAME}-wt"
WT_DIR="${WT_ROOT}/${BRANCH}"

# Validate
if [ -d "$WT_DIR" ]; then
    echo "ERROR: Worktree directory already exists: $WT_DIR"
    exit 1
fi

# Create worktrees root if needed
mkdir -p "$WT_ROOT"

# Create the worktree with a new branch
echo "Creating worktree: $WT_DIR (branch: $BRANCH from $BASE)"
git worktree add -b "$BRANCH" "$WT_DIR" "$BASE"

# Copy .claude/ gitignored files (settings.local.json, scratch/, research/)
echo "Copying .claude/ config..."
for item in settings.local.json scratch research; do
    src="${REPO_ROOT}/.claude/${item}"
    dst="${WT_DIR}/.claude/${item}"
    if [ -e "$src" ]; then
        if [ -d "$src" ]; then
            mkdir -p "$dst"
            cp -r "$src/." "$dst/" 2>/dev/null || true
        else
            cp "$src" "$dst"
        fi
        echo "  copied .claude/${item}"
    fi
done

# Symlink .venv from main repo
if [ -d "${REPO_ROOT}/.venv" ]; then
    echo "Symlinking .venv..."
    ln -s "${REPO_ROOT}/.venv" "${WT_DIR}/.venv"
    echo "  linked .venv -> ${REPO_ROOT}/.venv"
fi

echo ""
echo "Worktree ready: $WT_DIR"
echo "Branch: $BRANCH (based on $BASE)"
echo ""
echo "To use:  cd $WT_DIR"
echo "To remove: git worktree remove $WT_DIR"
