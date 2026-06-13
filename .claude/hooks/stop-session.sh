#!/usr/bin/env bash
# stop-session.sh - persist a one-line session trail; nag if a session is open without /session-end
# fires on Stop. Writes to .claude/sessions/<date>.log; prints reminder if pointer is non-empty.
set -euo pipefail

ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"
SESS_DIR="$ROOT/.claude/sessions"
mkdir -p "$SESS_DIR"

log_file="$SESS_DIR/$(date -u +%Y-%m-%d).log"
branch="$(git -C "$ROOT" symbolic-ref --short HEAD 2>/dev/null || echo '-')"
diff_stats="$(git -C "$ROOT" diff --shortstat HEAD 2>/dev/null || echo '')"

# Stop event payload contains transcript_path - snapshot it so we can read
# the full prompt + reasoning + output trail of this session later.
payload="$(cat 2>/dev/null || true)"
transcript=""
if command -v jq >/dev/null 2>&1; then
  transcript="$(echo "$payload" | jq -r '.transcript_path // empty' 2>/dev/null || true)"
fi

printf '%s  branch=%s  %s\n' \
  "$(date -u +%H:%M:%SZ)" "$branch" "$diff_stats" \
  >> "$log_file"

# Snapshot the transcript path into the active session's observability dir.
pointer_file="$SESS_DIR/.current-session"
if [ -n "$transcript" ] && [ -f "$pointer_file" ]; then
  active_raw="$(tr -d '[:space:]' < "$pointer_file" || true)"
  if [ -n "$active_raw" ]; then
    obs_dir="$ROOT/.claude/observability/transcripts/$active_raw"
    mkdir -p "$obs_dir"
    {
      echo "transcript_path: $transcript"
      echo "stopped_at:      $(date -u +%Y-%m-%dT%H:%M:%SZ)"
      echo "branch:          $branch"
    } > "$obs_dir/transcript-pointer.txt"
  fi
fi

# Nag if a session is still active.
pointer="$SESS_DIR/.current-session"
if [ -f "$pointer" ]; then
  active_raw="$(tr -d '[:space:]' < "$pointer" || true)"
  active_file=""
  if [ -n "$active_raw" ]; then
    case "$active_raw" in
      *.md) active_file="$SESS_DIR/$active_raw" ;;
      *)    active_file="$SESS_DIR/${active_raw}.md" ;;
    esac
  fi
  if [ -n "$active_file" ] && [ -f "$active_file" ]; then
    id=$(basename "${active_file%.md}")
    started="$(awk -F': ' '/^started:/{print $2; exit}' "$active_file" 2>/dev/null || echo '?')"
    last_update="$(grep -c '^### Update' "$active_file" 2>/dev/null || echo 0)"
    >&2 cat <<NAG

[reminder] Session $id is still open.
           started:        $started
           updates so far: $last_update
           Run /session-end to finalise outcomes and clear the pointer
           BEFORE closing the terminal. Otherwise the next session will
           load this one as if it were still in flight.
NAG
  fi
fi
exit 0
