#!/usr/bin/env bash
# WorktreeRemove hook — cleans up sibling worktree directory
#
# Receives JSON on stdin with: cwd, worktree_path
# Non-blocking — cannot prevent removal

set -euo pipefail

INPUT=$(cat)
WORKTREE_PATH=$(echo "$INPUT" | jq -r '.worktree_path')

if [ -d "$WORKTREE_PATH" ]; then
    git worktree remove "$WORKTREE_PATH" --force 2>/dev/null || true
fi
