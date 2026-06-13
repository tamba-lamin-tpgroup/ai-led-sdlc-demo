---
description: Open a persistent session. Required at the top of every AI or human development session. Creates a session file in .claude/sessions/ that captures goals, updates, and outcomes so the next session can pick up where this one left off.
argument-hint: "[issue-num | short-name]"
allowed-tools: Bash, Read, Write, Grep
---

# /session-start

Mandatory first command for any development work on Salone Explorer.
Creates the persistent-memory file the rest of the session writes to and
the next session reads from.

## Procedure

1. **Refuse to start a second session.** If
   `.claude/sessions/.current-session` is non-empty, print the active
   session's path and last update, then stop. Tell the user to
   `/session-end` first or `/session-resume` to keep going.

2. **Resolve the slug**:
   - If `$ARGUMENTS` looks like a number, treat it as a GitHub issue
     number. Read the title from the issue (`gh issue view <num>`) and
     slugify it (lowercase, hyphens, max 40 chars).
   - Else, slugify `$ARGUMENTS` directly.
   - If `$ARGUMENTS` is empty, ask the user for a short name.

3. **Detect the layer** from the changed paths, the active branch, or
   CWD. One of:
   - `code` — `src/components/`, `src/pages/`, `src/lib/`
   - `data` — `src/data/*.json`
   - `content` — `src/content/*.json`
   - `infra` — CI workflows, Vercel config, `supabase/`, tooling
   - `cross-layer` — work spanning two or more of the above

4. **Create the session file** at
   `.claude/sessions/YYYY-MM-DD-HHMM-<layer>-<slug>.md` with this exact
   frontmatter and section structure. The structure is parsed
   mechanically by the SessionStart hook, `/session-list`, and
   `resume-context.py`, so do not rename headings or reorder the
   frontmatter fields.

   ```
   ---
   id: YYYY-MM-DD-HHMM-<layer>-<slug>
   layer: <code | data | content | infra | cross-layer>
   issue: #<num> | none
   context_pack: .claude/context-packs/<issue-num>/ | none
   started: YYYY-MM-DD HH:MM ZZZ
   ended: in-progress
   author: <git config user.name>
   actor: human | claude | claude-autonomous
   branch: <current branch>
   ---

   # Session: <slug>

   ## Overview
   <One paragraph: what we are setting out to do and why. Cite the SPEC
   phase/section per spec-first.>

   ## Goals
   - [ ] goal 1
   - [ ] goal 2

   ## Plan
   <Link to the plan-then-code plan file or paste the plan here.>

   ## Updates
   <Empty. Each /session-update appends here.>

   ## Findings
   <Empty. Notable discoveries appended during the session.>

   ## Open questions
   <Empty. Unresolved questions appended here.>

   ## Outcomes
   <Empty. /session-end fills this with the summary.>

   ## Next session
   <Empty. /session-end fills this with what to pick up next.>
   ```

5. **Update the pointer**: write the bare session id (no path, no `.md`
   extension) to `.claude/sessions/.current-session`. Example contents:
   `2026-06-05-1700-code-attractions-repository`.

6. **Confirm** to the user: print the session id, the path, and the
   three commands they will use next:
   - `/session-update "<note>"` to append progress
   - `/session-end` to finalise and clear the pointer
   - `/session-current` to view current state

## Why this is mandatory

Every prior failure mode in long-running AI work traces back to the same
cause: the next session had no idea what the previous one was doing. The
session file is the single durable artefact between sessions. Without
`/session-start`, that artefact does not exist.

## Anti-patterns

- Starting work without `/session-start` and "remembering to do it later".
- Renaming or omitting any of the section headings.
- Using `workstream:` instead of `layer:` in the frontmatter.
- Using a slug that already exists — re-use `/session-resume` instead.
