#!/usr/bin/env bash
# gen-agent-memory.sh - generate AGENTS.md (Codex) and GEMINI.md (Gemini)
# from a per-tool preamble plus the shared CLAUDE.md and .claude/rules/*.md.
# Codex CLI reads AGENTS.md; Gemini CLI reads GEMINI.md. The governance is
# identical across assistants; only the enforcement mechanics differ, so
# each file opens with a tool-specific preamble that (1) names what is
# mechanically enforced for that tool (the git-hook floor), (2) names the
# Claude Code-native mechanisms that DO NOT apply, then includes the shared
# rules and CLAUDE.md as reference.
#
# usage:
#   gen-agent-memory.sh           regenerate AGENTS.md and GEMINI.md
#   gen-agent-memory.sh --check   exit 1 if either file is out of date
#
# See docs/dev-guide/multi-tool-enforcement.md.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
RULES_DIR="$REPO_ROOT/.claude/rules"
CLAUDE_MD="$REPO_ROOT/CLAUDE.md"

# preamble <memfile> <tool-name>
# Emits the tool-specific operating agreement that precedes the shared
# governance content.
preamble() {
  local memfile="$1" tool="$2"
  cat <<EOF
<!--
  GENERATED FILE - do not edit by hand.
  Source: per-tool preamble + CLAUDE.md + .claude/rules/*.md
  Regenerate: .claude/scripts/gen-agent-memory.sh
-->

# ${memfile} - ${tool} working agreement for Salone Explorer

You are ${tool}. This file is your project memory: the ${tool} counterpart
of CLAUDE.md. The governance in this repo is identical for every assistant
that touches it; only the *enforcement mechanics* differ by tool. Read this
preamble first - it tells you which parts of the Claude Code-oriented
content below actually apply to you.

## What is mechanically enforced for you

Commits you author pass through versioned git hooks (\`.githooks/\`,
activated via \`core.hooksPath\`). They run for any tool and block on
failure:

- \`commit-msg\` - every commit message needs a
  \`Requirement:\`/\`Phase:\`/\`Incident:\` traceability trailer.
- \`pre-commit\` - secret scan on staged files, a one-line purpose header on
  each new source file, and the three-layer separation grep over
  \`salone-explorer/src\`.

Activate them once per clone:

    .claude/scripts/install-git-hooks.sh

## What does NOT apply to you

The \`.claude/\` harness is Claude Code-native. Its slash commands
(\`/session-start\`, \`/orchestrate\`, \`/handoff\`, ...), \`settings.json\`
hooks, skills, subagents, output styles, and statusline DO NOT run under
${tool}. Where the rules and CLAUDE.md below reference those mechanisms,
treat them as background and use the manual equivalent:

- No \`/session-start\` automation: if you do long-running work, record
  intent and outcomes in \`.claude/sessions/\` by hand following the
  existing file format.
- No prompt-level spec-first gate: satisfy spec-first at commit time via
  the trailer (enforced by \`commit-msg\` above) - reference a SPEC phase /
  section, a GitHub issue, or an incident.
- No automated \`reset --hard\` / \`push --force\` block: the git hooks
  cannot stop these, so the discipline is on you. Do not run them; do not
  bypass the hooks.
- No automated reviewer agents: request human review before merge. ${tool}
  never merges to \`main\`.

## Binding rules

The rules below (from \`.claude/rules/\`) are binding and tool-neutral.

EOF
}

# rules_block - concatenate every rule file with a source marker.
rules_block() {
  local rule
  for rule in "$RULES_DIR"/*.md; do
    [ -f "$rule" ] || continue
    echo "<!-- source: .claude/rules/$(basename "$rule") -->"
    echo
    cat "$rule"
    echo
    echo "---"
    echo
  done
}

# reference_block - CLAUDE.md, framed as shared reference.
reference_block() {
  cat <<'EOF'
## Project reference (shared with Claude Code)

The full project guide follows. It is written for Claude Code, but the
architecture, the three-layer rule, the repository pattern, the branding
constants, and the post-scaffold commands apply to you unchanged. Only the
"AI harness (.claude/)" and activation sections are Claude Code-only - see
"What does NOT apply to you" above.

EOF
  cat "$CLAUDE_MD"
}

build() {
  preamble "$1" "$2"
  rules_block
  reference_block
}

write_or_check() {
  local target="$1" memfile="$2" tool="$3"
  local generated; generated="$(build "$memfile" "$tool")"
  if [ "${MODE:-write}" = "check" ]; then
    if [ ! -f "$target" ] || ! diff -q <(printf '%s\n' "$generated") "$target" >/dev/null 2>&1; then
      >&2 echo "[stale] $target is out of date; run .claude/scripts/gen-agent-memory.sh"
      return 1
    fi
    return 0
  fi
  printf '%s\n' "$generated" > "$target"
  echo "wrote $target"
}

MODE=write
[ "${1:-}" = "--check" ] && MODE=check

rc=0
write_or_check "$REPO_ROOT/AGENTS.md" "AGENTS.md" "Codex CLI" || rc=1
write_or_check "$REPO_ROOT/GEMINI.md" "GEMINI.md" "Gemini CLI" || rc=1
exit "$rc"
