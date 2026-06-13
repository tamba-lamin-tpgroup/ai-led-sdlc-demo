---
description: Start an autonomous-mode session for long-running, low-supervision work. Wraps a normal session with explicit autonomous-mode policies (auto-fix retries, escalation rules, mandatory verification gates).
argument-hint: "[issue-num | short-name]"
allowed-tools: Bash, Read, Write, Edit, Agent
---

# /session-autonomous-coding

For multi-hour, single-feature, single-developer-supervised runs.
Operates the same lifecycle as `/session-start` plus stricter rails.

## Prerequisites

- Claude Code launched with autonomous mode enabled:

  ```
  claude --dangerously-skip-permissions
  ```

  If the current session was not launched with that flag, exit and
  relaunch before invoking this command.

- A GitHub issue exists for the work and a context pack has been produced
  (`/orchestrate` or `/issue-start`).

## Procedure

1. **Verify autonomous-mode prerequisites** (above). If missing, stop.
2. **Verify branch**: must NOT be on `dev` or `main`. Feature work runs
   on `issue-<num>-<slug>`. If you are on a protected branch, run
   `/issue-start` first.
3. **Run /session-start** with `actor: claude-autonomous` in the
   frontmatter and `$ARGUMENTS` as the slug. Detect the layer (code |
   data | content | infra | cross-layer) as in `/session-start`.
4. **Initialise the autonomous policy block** in `## Plan`:

   ```
   Autonomous policy:
     - Auto-fix lint/typecheck/test failures up to 3 attempts per failure
     - Auto-commit at every green verification-loop
     - Auto-/session-update after every commit
     - Auto-spawn code-reviewer + security-reviewer before /handoff
     - Escalate to human on:
         * architectural decision required (invoke architect, then stop)
         * ambiguous requirement or missing SPEC trace
         * security finding (Medium or High)
         * breaking change to a public contract (the Attraction type,
           the attractions repository interface, the Supabase schema,
           an env var)
         * 3 consecutive failed auto-fix attempts on the same step
   ```

5. **Run the engineer agent** (the default claude agent) with the context
   pack and the autonomous policy. Do not pause between iterations unless
   an escalation condition is hit.

6. **At every commit**, auto-run `/session-update` with the commit hash
   and a one-line summary. The Updates section becomes the audit trail.

7. **At session end** (work complete or escalation hit), auto-run
   `/session-end`. The Outcomes section is the report the human reviewer
   reads.

## Hard rules

- Never bypass `verification-loop` (lint, typecheck, build, secret scan).
  Auto-fix failures up to the budget; escalate beyond it.
- Never skip the secret scanner.
- Never `git push --force` (denied by hook regardless).
- Never `gh pr merge` (denied by hook regardless).
- Never `--no-verify` (denied by hook regardless).
- Never weaken CI, disable RLS, or `eslint-disable` a `jsx-a11y` rule to
  make a build pass.
- Auto-commit at green only — never auto-commit a failing state.

## When to escalate by hand

Even within budget, escalate manually if:

- The change feels larger than the issue described.
- A new external dependency would be introduced (libraries beyond
  SPEC.md section 3 need justification).
- A test you cannot fix should be deleted (almost never the right move).
- The change would touch SPEC.md section 5, 6.1, 6.3, 8, 10, or 12 —
  stop and ask per CLAUDE.md.
