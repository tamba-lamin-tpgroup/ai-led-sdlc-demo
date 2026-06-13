#!/usr/bin/env bash
# pre-tool-edit.sh - enforce file-header convention on new source files
# fires on PreToolUse(Edit|Write). Only blocks Write to a *new* source file
# with no one-line purpose header.
set -euo pipefail

payload="$(cat || true)"
tool="$(echo "$payload" | jq -r '.tool_name // "Edit"' 2>/dev/null || echo Edit)"

# Log first so we capture even if we then block.
HOOKS_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPTS_DIR="$HOOKS_DIR/../scripts"
printf '%s' "$payload" | "$SCRIPTS_DIR/log-tool-call.sh" pre "$tool" allow >/dev/null 2>&1 || true

path="$(echo "$payload" | jq -r '.tool_input.file_path // empty' 2>/dev/null || true)"
content="$(echo "$payload" | jq -r '.tool_input.content // empty' 2>/dev/null || true)"

[ -z "$path" ] && exit 0
[ "$tool" = "Edit" ] && exit 0   # Edits to existing files do not require a new header

# Only enforce on source files. Data (src/data/*.json) and content
# (src/content/*.json) are pure JSON by the three-layer rule and carry no
# header. Docs and config are exempt too.
case "$path" in
  *.md|*.txt|*.json|*.yml|*.yaml|*.toml|*.lock|*.gitignore|*.gitmodules|*.template|*.example|*.css|*.svg|*.html) exit 0 ;;
esac

# Skip if file already exists (Write would overwrite; treat as the user's call).
[ -f "$path" ] && exit 0

# Header is the first non-empty line. Accept # ... or // ... or /* ... or """ ...
first_line="$(echo "$content" | awk 'NF{print; exit}')"
case "$first_line" in
  '#'*|'//'*|'/*'*|'"""'*) exit 0 ;;
esac

>&2 echo "[blocked] new source files must begin with a one-line file-purpose comment"
>&2 echo "          path: $path"
>&2 echo "          example: '// $(basename "$path") - <one-line purpose>'"
exit 2
