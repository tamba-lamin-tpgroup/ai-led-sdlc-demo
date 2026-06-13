---
id: 2026-06-13-1243-infra-create-phase-issues
layer: infra
issue: none
context_pack: none
started: 2026-06-13 12:43 EDT
ended: 2026-06-13 14:00 EDT
author: Tamba Lamin
actor: claude
branch: main
---

# Session: create-phase-issues

## Overview
Read SPEC.md and turn the delivery workflow (§19) into GitHub issues
grouped by phase, then wire those issues into the repo project board
(https://github.com/users/tamba-lamin-tpgroup/projects/1) so that issue
status moves are reflected on the board. Source of truth: SPEC.md §2
(scope) and §19 (delivery workflow), Phases 1–11 plus 2.5.

## Goals
- [x] Decide issue granularity (one per phase vs one per spec step) — one per phase
- [x] Create GitHub issues covering the SPEC phases — #1–#12 created
- [ ] Add issues to project #1 and set their Status so the board reflects them
- [ ] Confirm board automation moves cards on status change

## Plan
Read SPEC §19 phase by phase, create one issue per phase (default),
labelled by phase, body cites the SPEC §19 steps and acceptance
criteria. Add each to project #1 via gh project item-add, set the
Status field. Blocker: gh token lacks read:project/project scopes.

## Updates
- 2026-06-13 12:43 EDT — Session opened. Read SPEC §2 and §19. Found gh
  token missing read:project/project scopes; board wiring blocked until
  refreshed. Existing issues: none.
- 2026-06-13 12:50 EDT — Decisions: one issue per phase, all SPEC phases.
  Created 12 phase labels and 12 issues (#1 Phase 1 … #12 Phase 11; #8
  Phase 2.5, #9 Phase 8). Board wiring blocked on gh project scope —
  awaiting `gh auth refresh -s project` from the user.

## Findings
- gh token scopes: gist, read:org, repo, workflow. Missing read:project
  and project (write) — required to list/add project items.

## Open questions
- Issue granularity: one issue per phase, or one per SPEC §19 step?

## Outcomes
Created 12 phase labels and 12 GitHub issues (#1–#12) covering all SPEC phases (1–11, 2.5, 8). Board wiring to project #1 is blocked — requires `gh auth refresh -s project` to add the project OAuth scope. Core deliverable (issues created) is done.

## Next session
Run `gh auth refresh -s project` and then `gh project item-add 1 --url <issue-url>` for each issue to wire the board. Or skip the board wiring and proceed to Phase 1 implementation.
