---
description: Show the full state of the active session. Run any time you need to remind yourself of goals, recent updates, blockers, or where to pick up.
allowed-tools: Bash, Read
---

# /session-current

The single screen for "what am I doing right now".

## Procedure

1. Read `.claude/sessions/.current-session`.
2. If empty, print "no active session — run /session-start <name>" and
   stop.
3. Otherwise read the session file and print:

   ```
   id:           <id>
   started:      <started>  (duration: <h:mm>)
   layer:        <layer>
   branch:       <branch>
   issue:        <issue>
   actor:        <actor>

   Goals:
     <copy ## Goals checklist verbatim>

   Last 3 updates:
     <Show the three most recent ### Update blocks, full verbatim>

   Open questions:
     <copy ## Open questions verbatim, or "none">

   Verification (last known): <pass | fail | not-run-since-last-commit>

   Suggested next: /session-update "<one-line note>"  or  /session-end
   ```

## When to call

- Returning to the terminal after a break.
- Starting a fresh Claude Code conversation in the same session.
- Trying to remember what the open question was.
- Before `/session-end` — sanity-check that you have everything needed
  to write a useful Outcomes section.
