#!/usr/bin/env bash
# user-prompt-submit.sh - spec-first gate on all prompts.
# Every prompt that produces code/files must satisfy ONE of the allow
# conditions below. Exit 0 = proceed. Exit 1 = warning (Claude must not
# write code/files).
#
# Salone Explorer is spec-driven: SPEC.md is the single source of truth and
# its §19 delivery workflow defines the phases. Work must trace to a SPEC
# phase/section, a tracked GitHub issue, or an approved requirement.
set -euo pipefail

payload="$(cat || true)"
prompt_text="$(echo "$payload" | jq -r '.tool_input.prompt // empty' 2>/dev/null || true)"
[ -z "$prompt_text" ] && prompt_text="$payload"

# 1. Slash commands pass unconditionally.
if echo "$prompt_text" | grep -qE '^\s*/[a-z]'; then
  exit 0
fi

# 2. Explicit SPEC phase / section, requirement, or issue reference.
#    Phase N, SPEC §N, SPEC section N, #NNN, GitHub issue URL,
#    STORY-/FR-/NFR-/TASK-/EPIC- ids.
if echo "$prompt_text" | grep -qiE \
  '(github\.com/[^ ]+/issues/[0-9]+|#[0-9]+|issue[- ]?[0-9]+|phase[ -]?[0-9]+(\.[0-9]+)?|spec[ ]*(§|section|sec\.?)[ ]*[0-9]+|STORY-[0-9]+|FR-[0-9]+|NFR-[0-9]+|TASK-[0-9]+|EPIC-[0-9]+)'; then
  exit 0
fi

# 3. Active session is linked to a GitHub issue.
_session_has_issue() {
  local dir="$1"
  local pointer="$dir/.claude/sessions/.current-session"
  [ -f "$pointer" ] || return 1
  local session_id; session_id="$(tr -d '[:space:]' < "$pointer")"
  [ -n "$session_id" ] || return 1
  local session_file
  case "$session_id" in
    *.md) session_file="$dir/.claude/sessions/$session_id" ;;
    *)    session_file="$dir/.claude/sessions/${session_id}.md" ;;
  esac
  [ -f "$session_file" ] || return 1
  local issue; issue="$(awk -F': ' '/^issue:/{gsub(/[[:space:]]/, "", $2); print $2; exit}' \
    "$session_file" 2>/dev/null || echo '')"
  [ -n "$issue" ] && [ "$issue" != "none" ]
}

_ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"
if _session_has_issue "$_ROOT"; then
  exit 0
fi

# 4. Explicit intent to CREATE a requirement, issue, or SPEC entry.
if echo "$prompt_text" | grep -qiE \
  '\b(create|draft|write|file|start|open|define|author)\s+(a\s+|new\s+|the\s+)?(requirement|story|issue|FR|NFR|epic|task|user.?story|acceptance.?criteria|feature.?request|spec|phase)\b'; then
  exit 0
fi

# 5. Pure informational query (a question with no implementation verb).
_has_impl_verb() {
  echo "$1" | grep -qiE \
    '\b(implement|build|fix|add|migrate|refactor|update|modify|change|delete|remove|generate|scaffold|provision|develop|deploy|configure|set.?up|extend|enhance|improve|integrate|connect|wire|patch|debug|resolve|address|handle|process|extract|transform|load|install|upgrade|bump|create|write|code|edit|make|convert|rewrite|reformat|style|render)\b'
}

if echo "$prompt_text" | grep -qiE \
  '^\s*(what|how|why|when|where|which|who|is\s+there|are\s+there|does|do|did|should|would|could|explain|describe|show\s+me|tell\s+me|list|summarize|summarise|review|check|analyse|analyze|read|look\s+at|examine|inspect|can\s+you\s+(explain|describe|show|list|summarize|summarise|review|check|analyse|analyze))'; then
  if ! _has_impl_verb "$prompt_text"; then
    exit 0
  fi
fi

# BLOCK.
>&2 cat <<'WARN'
[spec-first] No SPEC phase, requirement, or issue reference in this prompt.

  Project policy: every prompt that produces code, tests, or file
  changes MUST trace to SPEC.md (the single source of truth), a tracked
  GitHub issue, or an approved requirement.

  HOW TO PROCEED - pick one:

  A. Link your session to a GitHub issue (best for all dev work):
       /session-start <issue-number>
     Every subsequent prompt in the session is automatically covered.

  B. Reference the SPEC phase or section directly in your prompt:
       "Scaffold the Vite app per SPEC Phase 1"
       "Implement the attractions repository per SPEC section 5.2"
       "Add the WCAG disclaimer alert for Phase 3"

  C. Reference a GitHub issue directly:
       "Implement the sign-in form per #14"

  D. Create the requirement/issue first:
       "Create an issue for the tour-booking calendar"
     Then run /orchestrate <issue-url> before coding begins.

  YOU MUST NOT write, edit, or generate production code, tests, or
  documentation in response to this prompt.
WARN
exit 1
