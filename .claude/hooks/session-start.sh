#!/usr/bin/env bash
# session-start.sh - workspace state + persistent session memory at the top of every session
# fires on Claude Code SessionStart event
set -euo pipefail

ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"
cd "$ROOT"

SESS_DIR=".claude/sessions"
POINTER="$SESS_DIR/.current-session"

echo "==== salone-explorer session ===="
echo "workspace: $ROOT"
echo "branch:    $(git symbolic-ref --short HEAD 2>/dev/null || echo 'no-branch')"
dirty="$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
echo "changed:   $dirty file(s)"

# ---------- persistent memory ----------
# Convention: pointer file contains the bare session id (without .md).
# Hook tolerates either form (with or without .md) for robustness.
mkdir -p "$SESS_DIR"
active_raw=""
[ -f "$POINTER" ] && active_raw="$(tr -d '[:space:]' < "$POINTER")"
active_file=""
if [ -n "$active_raw" ]; then
  case "$active_raw" in
    *.md) active_file="$SESS_DIR/$active_raw" ;;
    *)    active_file="$SESS_DIR/${active_raw}.md" ;;
  esac
fi

if [ -n "$active_file" ] && [ -f "$active_file" ]; then
  file="$active_file"
  id=$(basename "${file%.md}")
  echo
  echo "ACTIVE SESSION: $id"
  echo "  goals:"
  awk '/^## Goals/{flag=1;next} /^## /{flag=0} flag && /^- /{print "    "$0}' "$file" | head -20
  echo "  last 3 updates:"
  awk '/^### Update -/{c++; print "    "$0; flag=1; next}
       /^### /{flag=0}
       flag && c<=3 && /^[A-Za-z]/{print "      "$0}' "$file" \
    | tail -40
  echo
  python3 "$ROOT/.claude/scripts/resume-context.py" "$id" 2>/dev/null || true
  echo
  echo "  resume:  /session-current   (full view)"
  echo "  finish:  /session-end       (write outcomes, clear pointer)"
else
  recent=$(ls -t "$SESS_DIR"/*.md 2>/dev/null | head -3 || true)
  if [ -n "$recent" ]; then
    echo
    echo "NO ACTIVE SESSION. Three most-recent sessions:"
    while IFS= read -r f; do
      [ -z "$f" ] && continue
      id=$(awk -F': ' '/^id:/{print $2; exit}' "$f")
      layer=$(awk -F': ' '/^layer:/{print $2; exit}' "$f")
      ended=$(awk -F': ' '/^ended:/{print $2; exit}' "$f")
      [ "$ended" = "in-progress" ] && status="(orphaned, no /session-end was called)" || status="ended $ended"
      outcome=$(awk '/^## Outcomes/{flag=1; next} /^## /{flag=0} flag && /^[A-Za-z]/{print; exit}' "$f")
      next=$(awk '/^Concrete next steps:/{flag=1; next} /^[A-Z]/{flag=0} flag && /^  *[0-9]/{print; exit}' "$f")
      printf "  %s  layer=%s  %s\n      outcome: %s\n      next:    %s\n" \
        "$id" "$layer" "$status" "${outcome:-<none>}" "${next:-<none>}"
    done <<< "$recent"
    echo
    echo "  Resume any with:  /session-resume <id>"
    echo "  Or start fresh:   /session-start <name|issue#>"
  else
    echo
    echo "NO SESSIONS YET. Start one with:  /session-start <name|issue#>"
  fi
fi

# ---------- active context packs ----------
packs=$(find .claude/context-packs -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
if [ "$packs" -gt 0 ]; then
  echo
  echo "context packs: $packs active"
  for d in .claude/context-packs/*/; do
    [ -f "$d/state.md" ] && echo "  - $(basename "$d")"
  done
fi

echo "========================================"
