#!/usr/bin/env bash
# remove-worktree.sh — Remove a git worktree and optionally delete its branch
#
# Usage: bash .claude/scripts/remove-worktree.sh <branch-name> [--keep-branch]
#   branch-name   — the worktree/branch to remove
#   --keep-branch — keep the branch after removing the worktree (default: delete it)
#
# Removes worktree from: ../maccabipedia_mediawikibot-wt/<branch-name>

set -euo pipefail

if [ $# -lt 1 ]; then
    echo "Usage: bash .claude/scripts/remove-worktree.sh <branch-name> [--keep-branch]"
    echo ""
    echo "Active worktrees:"
    git worktree list
    exit 1
fi

BRANCH="$1"
KEEP_BRANCH=false
if [ "${2:-}" = "--keep-branch" ]; then
    KEEP_BRANCH=true
fi

# Resolve paths
REPO_ROOT="$(git rev-parse --show-toplevel)"
REPO_NAME="$(basename "$REPO_ROOT")"
WT_ROOT="$(dirname "$REPO_ROOT")/${REPO_NAME}-wt"
WT_DIR="${WT_ROOT}/${BRANCH}"

# Check worktree exists
if [ ! -d "$WT_DIR" ]; then
    echo "ERROR: Worktree not found: $WT_DIR"
    echo ""
    echo "Active worktrees:"
    git worktree list
    exit 1
fi

# Remove the worktree
echo "Removing worktree: $WT_DIR"
git worktree remove "$WT_DIR" --force

# Delete branch unless --keep-branch
if [ "$KEEP_BRANCH" = false ]; then
    echo "Deleting branch: $BRANCH"
    git branch -D "$BRANCH" 2>/dev/null || echo "  branch already gone or not local"
fi

# Clean up empty worktrees root
if [ -d "$WT_ROOT" ] && [ -z "$(ls -A "$WT_ROOT")" ]; then
    rmdir "$WT_ROOT"
    echo "Removed empty worktrees directory"
fi

echo "Done."
