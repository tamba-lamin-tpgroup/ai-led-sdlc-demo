#!/usr/bin/env bash
# post-tool-edit.sh - run the file-local linter/formatter for the edited file
# fires on PostToolUse(Edit|Write). Best-effort; never blocks the session.
set -euo pipefail

payload="$(cat || true)"

# Log the post-tool snapshot (file path + outcome).
HOOKS_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPTS_DIR="$HOOKS_DIR/../scripts"
printf '%s' "$payload" | "$SCRIPTS_DIR/log-tool-call.sh" post Edit ok >/dev/null 2>&1 || true

path="$(echo "$payload" | jq -r '.tool_input.file_path // empty' 2>/dev/null || true)"
[ -z "$path" ] && exit 0
[ ! -f "$path" ] && exit 0

# Resolve the project root: nearest ancestor with package.json.
ws_root="$path"
while [ "$ws_root" != "/" ] && [ "$ws_root" != "${CLAUDE_PROJECT_DIR:-/}" ]; do
  ws_root="$(dirname "$ws_root")"
  [ -f "$ws_root/package.json" ] && break
done
[ -f "$ws_root/package.json" ] || ws_root="${CLAUDE_PROJECT_DIR:-$(pwd)}"

case "$path" in
  *.ts|*.tsx|*.js|*.jsx)
    if [ -f "$ws_root/package.json" ] && command -v npx >/dev/null 2>&1; then
      ( cd "$ws_root" && npx --no-install eslint --fix "$path" 2>/dev/null ) || true
      ( cd "$ws_root" && npx --no-install prettier --write "$path" 2>/dev/null ) || true
    fi
    ;;
  *.css|*.json|*.md)
    if [ -f "$ws_root/package.json" ] && command -v npx >/dev/null 2>&1; then
      ( cd "$ws_root" && npx --no-install prettier --write "$path" 2>/dev/null ) || true
    fi
    ;;
esac
exit 0
