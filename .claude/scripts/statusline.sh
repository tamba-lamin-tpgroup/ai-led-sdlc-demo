#!/usr/bin/env bash
# statusline.sh - one-line workspace state for the Claude Code status bar
# format:  [branch] issue:<id|none>  session:<id|none>  +a -d  time:<elapsed> cost:$<usd>
set -euo pipefail

cd "${CLAUDE_PROJECT_DIR:-.}"

# Claude Code pipes a JSON status payload on stdin; live session duration and
# cost live there (authoritative figures it computes, not derived here). Read
# only when stdin is not a TTY so manual/direct runs do not block on input.
payload=""
if [ ! -t 0 ]; then
  payload="$(cat)"
fi

branch="$(git symbolic-ref --short HEAD 2>/dev/null || git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'no-branch')"
branch="${branch//$'\n'/ }"

# Issue id from branch name pattern issue-<n>-... / fix-<n>-... / hotfix-<n>-...
issue="$(echo "$branch" | grep -oE '^(issue|fix|hotfix)-[0-9]+' | grep -oE '[0-9]+' || echo 'none')"

# Active session id (the persistent-memory anchor)
session="none"
pointer=".claude/sessions/.current-session"
if [ -f "$pointer" ]; then
  raw="$(tr -d '[:space:]' < "$pointer" 2>/dev/null || true)"
  [ -n "$raw" ] && session="${raw%.md}"
fi

# Diff stats vs HEAD
stats="$(git diff --shortstat 2>/dev/null | sed -E 's/.*([0-9]+) insertions?\(\+\),?\s*([0-9]+)?.*/+\1 -\2/' || echo '')"

# Live session time + cost from the stdin payload. Degrades to empty if the
# payload, the fields, or jq are absent - the statusline never errors on it.
live=""
if [ -n "$payload" ] && command -v jq >/dev/null 2>&1; then
  dur_ms="$(printf '%s' "$payload" | jq -r '.cost.total_duration_ms // empty' 2>/dev/null || true)"
  cost_usd="$(printf '%s' "$payload" | jq -r '.cost.total_cost_usd // empty' 2>/dev/null || true)"
  dur_ms="${dur_ms%%.*}"  # integer ms only; drop any fractional part
  parts=""
  if [ -n "$dur_ms" ] && [ "$dur_ms" -ge 0 ] 2>/dev/null; then
    secs=$(( dur_ms / 1000 ))
    h=$(( secs / 3600 )); m=$(( (secs % 3600) / 60 )); s=$(( secs % 60 ))
    if [ "$h" -gt 0 ]; then elapsed="${h}h ${m}m"
    elif [ "$m" -gt 0 ]; then elapsed="${m}m"
    else elapsed="${s}s"; fi
    parts="time:${elapsed}"
  fi
  if [ -n "$cost_usd" ]; then
    cost_fmt="$(printf '%.2f' "$cost_usd" 2>/dev/null || echo "$cost_usd")"
    parts="${parts:+$parts }cost:\$${cost_fmt}"
  fi
  [ -n "$parts" ] && live="  $parts"
fi

printf "[%s] issue:%s  session:%s  %s%s" "$branch" "$issue" "$session" "$stats" "$live"
