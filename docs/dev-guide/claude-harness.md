# Claude Code harness (`.claude/`)

This project ships an AI-led SDLC harness: custom subagents, governance
hooks, rules, skills, and slash commands that let Claude Code build
Salone Explorer fast and autonomously while staying inside the project's
architectural guardrails. It was adapted from a reference enterprise
setup and tuned to this stack (React + Vite + TypeScript + Supabase +
Tailwind + Playwright, single repo, Vercel deploy).

`SPEC.md` remains the single source of truth; this harness enforces it.

## One-time activation

Two files cannot be auto-written by Claude (they configure Claude's own
permissions). Activate them yourself:

```bash
# 1. Install the harness settings (review first, then move into place).
mv .claude/settings.json.proposed .claude/settings.json

# 2. Create your local, gitignored overrides + GitHub token for the MCP.
cp .claude/settings.local.json.template .claude/settings.local.json
#   then edit settings.local.json and set GITHUB_PERSONAL_ACCESS_TOKEN.

# 3. Restart Claude Code so it loads settings.json, hooks, and .mcp.json.
```

After this, the status line, hooks, output style, and MCP servers are
live.

## What's in the box

### Subagents (`.claude/agents/`)

| Agent               | Model  | Use when                                                        |
| ------------------- | ------ | --------------------------------------------------------------- |
| `architect`         | opus   | Cross-layer change, new dependency, contract/schema change. Produces an ADR; never codes. |
| `orchestrator`      | opus   | Entry point for a GitHub issue. Runs the spec-first pre-flight, writes a context pack, dispatches work. |
| `product-analyst`   | sonnet | A vague issue needs a concrete spec + acceptance criteria before coding. |
| `code-reviewer`     | sonnet | First-pass review of a diff. Catches three-layer leaks, silent fallbacks, missing tests. |
| `security-reviewer` | sonnet | Diffs touching auth, secrets, Supabase/RLS, env vars, rendering. Blocks handoff on High findings. |
| `qa-engineer`       | sonnet | Author the test plan from acceptance criteria and run the verification loop. |
| `docs-writer`       | sonnet | A diff changes behaviour/APIs/commands. Updates README, headers, ADRs, PR body. |

### Slash commands (`.claude/commands/`)

- Session lifecycle: `/session-start`, `/session-update`, `/session-end`,
  `/session-current`, `/session-resume`, `/session-list`, `/session-help`,
  `/session-autonomous-coding`.
- Workflow: `/orchestrate`, `/issue-start`, `/dev-start`, `/code-push`,
  `/quality`, `/handoff`, `/status`.

### Skills (`.claude/skills/`)

`plan-then-code`, `verification-loop`, `tdd-workflow`,
`accessibility-testing`, `secret-scanning`, `unit-testing`, `e2e-testing`,
and `sierra-leone-tourist-expert` (SME content fact-checker - verifies
attraction data and copy against the five approved sources; run it before
`/handoff` on any `src/data/` or `src/content/` change).

### Rules (`.claude/rules/`, loaded every session)

`three-layer-separation` (keystone), `engineering-principles`,
`spec-first`, `commit-conventions`, `branch-conventions`,
`test-conventions`, `api-conventions`, `80-20-split`.

### Hooks (`.claude/hooks/`, wired in `settings.json`)

| Event            | Hook                  | Enforces                                                       |
| ---------------- | --------------------- | ------------------------------------------------------------- |
| SessionStart     | `session-start.sh`    | Loads active-session memory / recent sessions into context.   |
| UserPromptSubmit | `user-prompt-submit.sh` | Blocks code-producing prompts with no SPEC/issue reference.  |
| PreToolUse(Bash) | `pre-tool-bash.sh`    | Blocks force-push, `reset --hard`, `--no-verify`, `gh pr merge`; secret-scans + requires a commit trailer. |
| PreToolUse(Edit) | `pre-tool-edit.sh`    | Blocks new source files missing a one-line purpose header.    |
| PostToolUse(Edit)| `post-tool-edit.sh`   | Auto-runs ESLint `--fix` + Prettier on the edited file.       |
| Stop             | `stop-session.sh`     | Nags if a session is left open; snapshots the transcript.     |

### Scripts (`.claude/scripts/`)

`statusline.sh`, `scan-secrets.sh` (+ allowlist), `log-tool-call.sh`,
`resume-context.py`, `copilot-review.sh` (Copilot reviewer loop driven
by `/handoff` — see `docs/dev-guide/copilot-review.md`).

### MCP servers (`.mcp.json`)

`github`, `filesystem`, `context7` (live library docs),
`code-review-graph` (graph-powered code navigation).

## The daily loop

```
/session-start 14          # or: /session-start phase-3-accessibility
/orchestrate <issue-url>   # optional: pre-flight + context pack
# ... plan-then-code, implement, /session-update as you go ...
/quality                   # full gate
/code-push "feat: ..."     # conventional commit + trailer + push
/handoff                   # verification + reviews + draft PR
/session-end               # write outcomes for the next session
```

For long autonomous runs: `/session-autonomous-coding <issue#>` (launch
Claude with `--dangerously-skip-permissions`).

## Governance model (enforced, per your setup choice)

- Every code-producing prompt must reference a SPEC phase/section, a
  GitHub issue, or run inside an issue-linked session.
- Every commit needs a `Requirement:` / `Phase:` / `Incident:` trailer.
- Every new source file needs a one-line header.
- Secrets, force-push, `reset --hard`, `--no-verify`, and `gh pr merge`
  are hard-blocked.
- Merging stays human-only (the 80/20 split).
