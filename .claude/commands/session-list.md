---
description: List every session ever recorded in this project. Highlights the active one, sorts most-recent first, shows the one-line outcome of each.
allowed-tools: Bash, Read, Grep
---

# /session-list

Catalogue of persistent memory. Use to find a session to resume or to
refresh memory on prior work in a layer.

## Procedure

1. List every `.claude/sessions/*.md` file (exclude hidden files and
   `.current-session`).
2. For each, parse the frontmatter to extract:
   - `id`, `layer`, `issue`, `started`, `ended`, `actor`
3. From the body, extract the first line of the `## Overview` section
   (the one-line "what we set out to do") and, if `ended` is not
   `in-progress`, the first line of the `## Outcomes` section.
4. Read `.claude/sessions/.current-session` to identify the active one.
5. Sort by `started` descending (newest first). The active session — the
   one whose id matches the pointer — is highlighted with `*`.
6. Print as a table:

   ```
   active  | started            | layer        | issue   | overview                                  | outcome
   --------|--------------------|--------------|---------|-------------------------------------------|-----------
   *       | 2026-06-05 17:00   | code         | #42     | Build hero component for landing page     | (in progress)
           | 2026-06-04 14:05   | content      | #41     | Move CTA strings into content layer       | Completed; PR #88 opened
           | 2026-06-03 09:30   | data         | #40     | Add Tiwai Island attraction record        | Done; record + region lookup added
   ```

   For sessions whose `ended` is `in-progress` but which are not the
   active session, show `(in progress)` in the outcome column.

7. Below the table, print three quick-action lines:
   - `/session-resume <id>` to reactivate any closed session
   - `/session-current` to expand the active session
   - filter hint: `/session-list <layer>` to filter (TODO if not yet
     supported)
