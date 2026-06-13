---
description: Lower-level than /orchestrate. Cuts the feature branch for a specific issue from origin/dev and guides into /session-start, but does not spawn engineer agents.
argument-hint: "<issue-num>"
allowed-tools: Bash, Read, Write, Grep
---

# /issue-start

Use this when you want to start work on an issue manually rather than
through full orchestration. Single git repo.

## Procedure

1. **Parse `$ARGUMENTS`** -> `<num>`. If empty, ask for the issue number.

2. **Read the issue title** (`gh issue view <num>`) and slugify it
   (lowercase, hyphens, max 40 chars) to produce `<slug>`.

3. **Cut the feature branch from a fresh `origin/dev`** (per
   `.claude/rules/branch-conventions.md`):
   ```
   git fetch origin
   git checkout -b issue-<num>-<slug> origin/dev
   ```
   Always branch from `dev`, never from `main` (hotfix is the only
   exception) and never from another feature branch.

4. **Print** the new branch name and the SPEC phase/section the issue
   traces to (required by `spec-first.md` before any code).

5. **Guide to `/session-start`**: suggest
   `/session-start <num>` to open the persistent-memory session for this
   work, then either `/orchestrate #<num>` to dispatch agents or start
   manually with `plan-then-code`.

## Anti-patterns

- Branching from a stale `origin/dev`. Always `git fetch` first.
- Reusing an existing branch name. Branches map 1:1 to issues.
- Starting code before the SPEC trace is identified.
