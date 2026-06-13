---
description: Reactivate a previously-ended session. Use when continuing work that was paused (overnight, across phases, after a code freeze) without losing the prior context, decisions, and findings.
argument-hint: "<session-id-or-filename>"
allowed-tools: Bash, Read, Edit, Write
---

# /session-resume

Re-open a closed session. Preserves the original frontmatter and body;
adds a `### Resume` marker to `## Updates`.

## Procedure

1. **Refuse if a session is already active.** Read
   `.claude/sessions/.current-session`. If non-empty, tell the user to
   `/session-end` first.

2. **Locate the target file**:
   - Accept either the bare id (`2026-06-05-1700-code-...`) or the full
     filename. Look it up in `.claude/sessions/`.
   - If not found, print the closest matches via `ls`.

3. **Update the frontmatter**:
   - Set `ended:` -> `in-progress`
   - Append a `resumed:` field with the timestamp (preserve the original
     `started:` and all other fields, including `layer:`).

4. **Append a Resume marker** to `## Updates`:

   ```
   ### Resume - YYYY-MM-DD HH:MM ZZZ

   Resumed by: <git config user.name>
   Branch: <current branch>
   Reason: <ask the user; one sentence>

   Carrying forward:
     - <copy the bullets from the original "## Next session > Concrete next steps">
   ```

5. **Set the pointer**: write the bare session id (no `.md`) to
   `.claude/sessions/.current-session`.

6. **Print the compact briefing**:

   ```bash
   python3 .claude/scripts/resume-context.py <session-id>
   ```

   This emits the session id, layer, branch, condensed Goals, the last 3
   Update summaries, and any open questions — enough context for the
   resumer (human or subagent) to pick up without reading the full
   session file.

   Paste the briefing output into the first message of the resumed
   session so it lands in the conversation context.

## Orchestrator use (subagent continuity)

When the orchestrator dispatches a subagent to continue interrupted
work, prepend the briefing to the subagent's prompt:

```python
briefing = subprocess.check_output(
    ["python3", ".claude/scripts/resume-context.py", session_id],
    text=True,
)
agent_prompt = f"{briefing}\n\n{task_prompt}"
```

This gives the subagent the same context the human resumer sees, without
requiring it to read the full session file.

## Why a Resume marker, not a new session

The session file is the unit of memory for one logical chunk of work.
Resuming preserves the chain of decisions and findings without
splintering them across N session files for what is conceptually one
piece of work.

## When to start a new session instead

- The work has changed direction enough that the old goals no longer
  apply.
- The original session was for a different layer than the new intent.
- Different developer / actor with no overlap in context.
