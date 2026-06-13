---
description: Append a structured update to the active session. Run after every meaningful step (plan approved, code committed, test passing, blocker hit, decision made). The session file is the only record the next session has.
argument-hint: "[short summary of what just happened]"
allowed-tools: Bash, Read, Edit
---

# /session-update

Append progress to the active session. Cheap, frequent, structured.

## Procedure

1. **Locate the active session.**
   - Read `.claude/sessions/.current-session`.
   - If empty or missing, tell the user to `/session-start` and stop.

2. **Compose the update block** with this exact shape (do not deviate;
   `/session-list`, the SessionStart hook, and `resume-context.py` parse
   these):

   ```
   ### Update - YYYY-MM-DD HH:MM ZZZ

   Summary: <$ARGUMENTS or, if empty, a one-sentence summary of what just happened>

   Git:
     branch: <current branch>
     last-commit: <short hash> <subject>
     staged: <count>   modified: <count>   untracked: <count>
     files-touched-since-last-update:
       - <path1>
       - <path2>

   Tasks (TaskList):
     completed: <n>   in-progress: <n>   pending: <n>
     just-completed:
       - <task subject>

   Verification:
     last-run: <timestamp or "not run since last commit">
     status: <pass | fail | skipped>

   Notes:
     <Free-form bullets. Decisions, blockers, surprises.>
   ```

   Pull the git block from `git status --porcelain` and
   `git log -1 --pretty='%h %s'`.

3. **Append** the block to the `## Updates` section of the active
   session file. Do not touch other sections except to add findings to
   `## Findings` if `$ARGUMENTS` clearly contains one (a discovery,
   gotcha, or non-obvious behaviour worth carrying forward).

4. **If a blocker is reported**, also append a one-line entry under
   `## Open questions` with the verbatim blocker text and the date.

5. **Confirm** to the user: print the update block back, in case they
   want to amend it.

## When to call

- After `/orchestrate` writes the context pack
- After the engineer's plan is approved
- After every commit (paired with `/code-push` is a good cadence)
- When `verification-loop` flips state (pass -> fail or fail -> pass)
- When you change direction (plan B replaces plan A)
- When you hit a blocker
- When a stakeholder answers an open question

## Anti-patterns

- One mega-update at the end of the session. Too much to summarise; too
  little for the next session to act on.
- Updates without git context. The git block is the cheapest way to
  reconstruct what changed.
- Free-form prose only. The structured fields are what tooling reads.
