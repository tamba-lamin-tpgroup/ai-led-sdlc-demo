#!/usr/bin/env bash
# pre-tool-bash.sh - guard rails for Bash tool invocations
# fires on PreToolUse(Bash). Reads the proposed command from stdin (JSON).
# Exit 0 = allow. Exit 1 = warn-only. Exit 2 = block.
set -euo pipefail

payload="$(cat || true)"

# Log the call first so we capture even if we then block.
HOOKS_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPTS_DIR="$HOOKS_DIR/../scripts"
printf '%s' "$payload" | "$SCRIPTS_DIR/log-tool-call.sh" pre Bash allow >/dev/null 2>&1 || true

cmd="$(echo "$payload" | jq -r '.tool_input.command // empty' 2>/dev/null || true)"
if [ -z "$cmd" ]; then exit 0; fi

# Block destructive git ops always (defence in depth alongside settings deny list).
case "$cmd" in
  *"git push --force"*|*"git push -f"*)
    >&2 echo "[blocked] force push is forbidden by project policy"
    exit 2 ;;
  *"git reset --hard"*)
    >&2 echo "[blocked] reset --hard is forbidden by project policy"
    exit 2 ;;
  *"git commit "*"--no-verify"*)
    >&2 echo "[blocked] commits must respect hooks; --no-verify is forbidden"
    exit 2 ;;
  *"gh pr merge"*)
    >&2 echo "[blocked] PR merges are human-only"
    exit 2 ;;
esac

# On commits: secret scan + Requirement:/Phase:/Incident: trailer check.
if echo "$cmd" | grep -qE '^[[:space:]]*git commit\b'; then
  staged="$(git -C "${CLAUDE_PROJECT_DIR:-.}" diff --name-only --cached 2>/dev/null || true)"
  if [ -n "$staged" ]; then
    if ! "$SCRIPTS_DIR/scan-secrets.sh" --staged 2>&1; then
      >&2 echo "[blocked] secret scanner found a finding in the staged change"
      exit 2
    fi
  fi

  # Require a traceability trailer in every commit message. Amend / reuse
  # commits are exempt (they carry the original, already-checked message).
  if echo "$cmd" | grep -qE '\--(amend|reuse-message|-C)'; then
    : # exempt
  elif ! echo "$cmd" | grep -qiE '(Requirement|Phase|Incident):[[:space:]]+\S'; then
    >&2 echo "[blocked] commit message is missing a traceability trailer"
    >&2 echo "          every commit must trace to SPEC.md, a requirement, or an incident."
    >&2 echo "          spec work:   Requirement: SPEC Phase 3 - accessibility  (or:  Phase: 3)"
    >&2 echo "          requirement: Requirement: STORY-0042-<slug>"
    >&2 echo "          hotfix:      Incident: <incident-id>"
    >&2 echo "          see: .claude/rules/spec-first.md and commit-conventions.md"
    exit 2
  fi
fi

exit 0
