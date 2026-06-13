---
description: Finalise the active session with a comprehensive summary and clear the pointer. Mandatory at the end of every development session.
allowed-tools: Bash, Read, Edit
---

# /session-end

Close the active session. Write the durable summary the next session
reads from. Clear the active-session pointer.

## Procedure

1. **Locate the active session.**
   - Read `.claude/sessions/.current-session`.
   - If empty or missing, tell the user there is no active session and
     stop.

2. **Compute summary inputs**:
   - Duration: `started` (from frontmatter) -> now.
   - Commits made during the session:
     `git log --since="<started>" --pretty='%h %s' -- .`
   - Files changed during the session: aggregate from updates.
   - Final `verification-loop` status (re-run if not run since the last
     commit; do not skip). The loop covers `npm run lint`,
     `npm run typecheck`, `npm run build`, and the secret scan — these
     exist only after Phase 1 has scaffolded `package.json`.
   - PRs opened (search session updates and `gh pr list`).
   - Token usage for the session window. Derive the start date from the
     `started` frontmatter (the `YYYY-MM-DD` part) and run:

     ```
     python3 "$CLAUDE_PROJECT_DIR/.claude/scripts/token-report.py" \
       --since <started-date> --summary
     ```

     This is approximate (filtered by date, not exact session boundary);
     label it as such. Token counts are exact; cost reads `n/a` unless
     rates are set in `.claude/config/model-pricing.json`.

3. **Update the frontmatter** of the active session file:
   - `ended:` -> now (`YYYY-MM-DD HH:MM ZZZ`)
   - keep all other frontmatter fields (id, layer, issue, context_pack,
     started, author, actor, branch) unchanged

4. **Fill the `## Outcomes` section** with this exact structure:

   ```
   Duration: <h:mm>
   Commits: <count>   PRs opened: <count>   Files changed: <count>
   Token usage (this session, approx): <token-report --summary output>

   Goals reached:
     - [x] goal 1 (cite update timestamp)
     - [ ] goal 2 (not done; reason)

   Key accomplishments:
     - <bullet>
     - <bullet>

   Code changes:
     <one line per significant module touched>

   Decisions made:
     <bullet, with link to ADR if produced>

   Findings worth carrying:
     <bullet, copied from ## Findings, deduplicated>

   Verification status (final):
     <copy/paste of the verification-loop report>
   ```

5. **Fill the `## Next session` section** with the actionable handoff:

   ```
   Pick up by reading:
     - This session file
     - Context pack at <path>
     - Open questions below

   Concrete next steps:
     1. <imperative step>
     2. <imperative step>

   Unresolved blockers:
     - <bullet, copied from ## Open questions, deduplicated>

   Recommended starting command:
     /session-resume <this-id>     OR
     /orchestrate <next-issue-url>
   ```

6. **Clear the pointer**: write an empty file to
   `.claude/sessions/.current-session` (do not delete the file — the
   hook checks for emptiness).

7. **Confirm** to the user: print the duration, the goals-reached count,
   and the next-session starting command.

## Why this is the most important command

The Outcomes and Next-session sections are exactly what the SessionStart
hook surfaces in the next session. If they are missing or thin, the next
session loses memory and re-derives everything from scratch. That is the
failure mode every session lifecycle exists to prevent.

## Anti-patterns

- Skipping `/session-end` because "I'll just close the terminal". The
  pointer stays stuck on a stale session and the SessionStart hook shows
  the wrong context next time.
- Filling Outcomes with a one-liner. The next session needs the
  decisions and findings, not just "done".
- Leaving Next-session empty. If there is genuinely nothing next, write
  "session goal completely satisfied; no follow-up required" — explicit.
