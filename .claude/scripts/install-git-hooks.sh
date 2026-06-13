#!/usr/bin/env bash
# install-git-hooks.sh - point this clone at the versioned .githooks/ dir.
# One-time, per-clone setup. Activates the tool-agnostic enforcement floor
# (commit-msg + pre-commit) so commits from Claude Code, Codex, Gemini, or
# a bare terminal all pass through the same gate. Reversible with:
#   git config --unset core.hooksPath
# See docs/dev-guide/multi-tool-enforcement.md.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
HOOKS_DIR="$REPO_ROOT/.githooks"

if [ ! -d "$HOOKS_DIR" ]; then
  >&2 echo "error: $HOOKS_DIR does not exist; run from inside the repo."
  exit 1
fi

chmod +x "$HOOKS_DIR"/* 2>/dev/null || true
git -C "$REPO_ROOT" config core.hooksPath .githooks

echo "git hooks installed: core.hooksPath = .githooks"
echo "active hooks:"
for h in "$HOOKS_DIR"/*; do
  [ -f "$h" ] && echo "  - $(basename "$h")"
done
