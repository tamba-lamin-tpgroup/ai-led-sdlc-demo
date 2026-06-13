---
description: Show the session-management cheat sheet. Explains the lifecycle, the file format, and how persistent memory flows between sessions.
allowed-tools: Read
---

# /session-help

## What sessions are

The session file is the project's persistent memory. Every AI or human
development session on Salone Explorer must be wrapped in:

```
/session-start <name>
... do work ...
/session-update "..."   (repeat as you progress)
/session-end
```

Without these, the next session starts with no memory of what was tried,
decided, or left in flight — the single largest source of wasted work in
long-running AI-led work.

## Commands

- `/session-start [name|issue#]` — open a new session, refuses if one is
  already active
- `/session-update [notes]` — append a structured update to the active
  session
- `/session-end` — finalise with a summary, fill Next-session, clear the
  pointer
- `/session-list` — all sessions, most-recent first, active highlighted
- `/session-current` — the active session at a glance
- `/session-resume <id>` — re-open a closed session
- `/session-autonomous-coding [name]` — start an autonomous-mode session
  (requires `claude --dangerously-skip-permissions`)

## File layout

```
.claude/sessions/
  .current-session                              pointer to active session (one bare id, or empty)
  YYYY-MM-DD-HHMM-<layer>-<slug>.md             one file per session
  <date>.log                                    per-day stop hook trail (separate, low-level)
```

`<layer>` is one of: `code`, `data`, `content`, `infra`, `cross-layer`.

## File format

Each session file has YAML frontmatter and a fixed set of sections.
Frontmatter fields, in order:

```
id, layer, issue, context_pack, started, ended, author, actor, branch
```

Sections (do not rename — mechanically parsed):

```
# Session: <slug>
## Overview
## Goals
## Plan
## Updates                  (appended by /session-update)
## Findings
## Open questions
## Outcomes                 (filled by /session-end)
## Next session             (filled by /session-end)
```

The headings are parsed by the SessionStart hook, `/session-list`, and
`.claude/scripts/resume-context.py`. Do not rename them. The field is
`layer:`, not `workstream:`.

## How memory carries forward

- The SessionStart hook reads `.current-session`. If non-empty, it prints
  the active session's goals + last 3 updates so a returning session
  resumes without context loss.
- If no session is active, the hook prints the most recent closed
  sessions with their `Outcomes` first line and `Next session > Concrete
  next steps` first line — so the operator instantly sees the pickup
  candidates.
- `resume-context.py <session-id>` produces the compact briefing block
  used by `/session-resume` and by the orchestrator when dispatching a
  subagent to continue work.

## Best practice

- Start a session for any unit of work that will take longer than 15
  minutes.
- Update at every state change (plan -> code -> verify -> commit ->
  push). Cheap and structured beats sparse and free-form.
- End every session, even short ones. Five seconds of finalisation saves
  an hour of next-session re-derivation.
- Resume rather than start when you are continuing the same logical work
  after a break.
