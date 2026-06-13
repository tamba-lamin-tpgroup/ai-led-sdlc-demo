---
description: Stage, commit, and push the current change. Enforces the Salone Explorer commit conventions (no AI signature, no --no-verify, conventional type, required traceability trailer), runs the secret scanner via the pre-tool-bash hook, and updates the active session.
argument-hint: "<type>: <imperative summary>"
allowed-tools: Bash, Read, Edit
---

# /code-push

Move a finished, verified change from the working tree to the remote.
Conventions live in `.claude/rules/commit-conventions.md` — read it if
the message is rejected.

## Procedure

1. **Sanity gates**:
   - `verification-loop` must have run since the last commit and exited 0
     (`npm run lint`, `npm run typecheck`, `npm run build`, secret scan —
     available only after Phase 1 scaffolds `package.json`).
   - `git status --porcelain` must show only the files listed in the
     active session's most recent `### Update` block (no surprise files).
   - Active session is open (`/session-current` shows it). If not, abort
     with a pointer to `/session-start`.
   - Branch must be a feature/fix/chore/promotion/hotfix branch, not
     `dev` or `main` directly (per `.claude/rules/branch-conventions.md`).

2. **Validate `$ARGUMENTS`** against
   `^(feat|fix|chore|docs|test|refactor|perf|build|ci): .{1,72}$`.
   This is the no-scope `type: summary` form mandated by
   `commit-conventions.md`. If it doesn't match, print the regex and the
   rule file path, then stop.

3. **Stage the changes**:
   - Prefer named-file `git add` over `git add -A` (per global guidance).
   - List the files about to be staged; ask the user to confirm if any
     look unexpected.

4. **Commit** (via heredoc) with the required trailers:
   - Append exactly one traceability trailer:
     `Requirement: <ref>` or `Phase: <n>` (or, for a hotfix,
     `Incident: <id>`). Pull the value from the active session's
     frontmatter (`issue:`, the linked SPEC phase/section); if it cannot
     be inferred, ask the user.
   - If an issue exists, also append `Refs: #<num>` (in-progress) or
     `Closes: #<num>` (only on the commit that finishes the issue). Pull
     the number from the session's `issue:` frontmatter.
   - The pre-tool-bash hook enforces the trailer, scans for secrets, and
     blocks `--no-verify`.

   Example:

   ```
   feat: add file-based attractions repository

   Requirement: SPEC section 5.2 - file-based repository
   Refs: #12
   ```

5. **Push**:
   - `git push -u origin <current-branch>`.
   - The PreToolUse hook blocks force-push and `--no-verify`.

6. **Update the session**:
   - Run `/session-update "code-push: <commit hash> <subject>"`.

7. **Print** the commit hash, branch, and the next suggested command
   (`/handoff` if the work is finished, or continue coding).

## What you must NOT do

- Do not pass `--no-verify` (denied by hook anyway).
- Do not amend a commit that has been pushed.
- Do not include AI co-author signatures or emoji.
- Do not commit without a traceability trailer.
- Do not skip the verification-loop "just this once".
