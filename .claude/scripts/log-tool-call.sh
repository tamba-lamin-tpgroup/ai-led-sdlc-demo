#!/usr/bin/env bash
# log-tool-call.sh - append a structured JSONL line per tool invocation
# usage: log-tool-call.sh <phase> <tool_name> <gate_decision>
#   phase:           pre | post
#   tool_name:       Bash | Edit | Write | Agent | ...
#   gate_decision:   allow | block | warn | (empty)
# Reads the tool payload from stdin (Claude Code hook contract).
# Writes to .claude/observability/tool-calls/<UTC-date>.jsonl
set -euo pipefail

ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"
OBS_DIR="$ROOT/.claude/observability/tool-calls"
mkdir -p "$OBS_DIR"
out_file="$OBS_DIR/$(date -u +%Y-%m-%d).jsonl"

phase="${1:-pre}"
tool="${2:-unknown}"
gate="${3:-}"

# Active session id (the persistent-memory anchor for this entry)
session_id=""
pointer="$ROOT/.claude/sessions/.current-session"
[ -f "$pointer" ] && session_id="$(tr -d '[:space:]' < "$pointer" || true)"

# Read payload from stdin (the hook gives us the tool's JSON input)
payload="$(cat 2>/dev/null || true)"

# Build the JSONL line. jq guarantees valid JSON encoding for the payload string.
ts="$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ 2>/dev/null || date -u +%Y-%m-%dT%H:%M:%SZ)"
branch="$(git -C "$ROOT" symbolic-ref --short HEAD 2>/dev/null || echo '-')"

if command -v jq >/dev/null 2>&1; then
  jq -n -c \
    --arg ts        "$ts" \
    --arg phase     "$phase" \
    --arg tool      "$tool" \
    --arg gate      "$gate" \
    --arg session   "$session_id" \
    --arg branch    "$branch" \
    --arg payload   "$payload" \
    '{ts:$ts, phase:$phase, tool:$tool, gate:$gate, session:$session, branch:$branch, payload:(try ($payload|fromjson) catch $payload)}' \
    >> "$out_file"
else
  # Fallback: minimal escape; loses payload structure but keeps the line valid
  esc=$(printf '%s' "$payload" | tr '\n' ' ' | sed 's/"/\\"/g')
  printf '{"ts":"%s","phase":"%s","tool":"%s","gate":"%s","session":"%s","branch":"%s","payload":"%s"}\n' \
    "$ts" "$phase" "$tool" "$gate" "$session_id" "$branch" "$esc" >> "$out_file"
fi
