---
description: Package the current branch into a draft PR ready for human review. Confirms a clean tree, runs verification-loop, spawns code-reviewer and security-reviewer, writes the PR body, opens a draft PR, comments the URL on the issue, then requests a Copilot review and resolves its comments in the background before handing back. Claude never merges.
allowed-tools: Bash, Read, Write, Edit, Grep, Agent
---

# /handoff

The end of the AI's 80 percent: a draft PR a human reviews and merges.
Claude never runs `gh pr merge` (denied by hook).

## Procedure

1. **Confirm a clean working tree** (`git status --porcelain` empty). If
   dirty, stop and tell the user to `/code-push` first.

2. **Run `verification-loop`** (`npm run lint`, `npm run typecheck`,
   `npm run build`, secret scan — available after Phase 1). Stop on any
   failure.

3. **Spawn the `code-reviewer` agent.** Apply non-controversial fixes,
   then re-run verification-loop. Re-commit via `/code-push` if anything
   changed.

4. **Spawn the `security-reviewer` agent.** Block on any High finding —
   do not open the PR until it is resolved or explicitly waived by the
   user. Surface Medium findings in the PR body.

5. **Spawn the `docs-writer` agent** to produce the PR body. It must
   reference the SPEC phase/section and the issue (per `spec-first.md`),
   summarise the change, and list the verification results.

6. **Choose the PR base** (per `branch-conventions.md`):
   - Feature/fix/chore branch (`issue-<num>-<slug>`) -> base `dev`.
   - Promotion branch (`promote-dev-to-main-<date>`) -> base `main`.
   - Hotfix branch (`hotfix-<num>-<slug>`) -> base `main`.

7. **Push and open the draft PR**:
   ```
   git push -u origin <branch>
   gh pr create --draft --base <dev|main> --title "<type: summary>" --body-file <body>
   ```
   The four CI gates (`ci.yml`, `codeql.yml`, `security.yml`, `a11y.yml`)
   run on the PR; all must be green before a human merges.

8. **Comment the PR URL on the originating issue** (`gh issue comment`).

9. **Run** `/session-update "handoff: draft PR <url> opened against <base>"`.

10. **Request a Copilot review** (the third reviewer, after the two local
    agents):
    ```
    .claude/scripts/copilot-review.sh request <pr>
    ```
    Automatic on every `/handoff`. Best-effort: GitHub will not add the
    Copilot bot through the API unless Copilot code review is enabled for
    the repo (an admin setting), so the script verifies and exits `3` if
    it could not add it. On exit `3`, surface its message to the owner
    (enable repo-level auto-request, or click Request Copilot review on
    the PR) and **still start the watcher** — the review may arrive via
    the repo auto-rule or a manual click. Note: `gh pr view --json
    reviewRequests` omits bot reviewers; confirm with
    `gh api repos/<owner>/<repo>/pulls/<pr>/requested_reviewers`.

11. **Start the background watcher** so this turn completes and the harness
    re-invokes you when the watcher exits with Copilot's comments (or a
    timeout). Run it backgrounded — with the Bash tool's background mode
    (`run_in_background: true`), or a trailing `&` when run by hand:
    ```
    .claude/scripts/copilot-review.sh watch <pr> &
    ```

12. **Resolve on watcher completion** — apply the Copilot resolution
    policy below, then `/session-update` with the fixed/flagged counts.

13. **Ping the owner** for final review and merge: print the PR URL, the
    Copilot summary (fixed vs flagged, links to any unresolved threads),
    and the human-reviewer checklist — review the diff, confirm the four
    CI gates pass, confirm SPEC trace in the body, then squash-merge.

## Copilot resolution policy

When the watcher returns (its JSON is also at
`.claude/sessions/copilot-review-<pr>.json`), classify each Copilot
thread before touching anything:

- **Safe-to-autofix** — typos, lint-level nits, obvious null/guard
  additions, doc or comment wording. Apply the fix, re-run
  `verification-loop`, then `/code-push` (so the secret scan, three-layer
  grep, new-file-header, and trailer gates all still run — never bypass
  them). Reply on the thread noting the fix, then
  `.claude/scripts/copilot-review.sh resolve-thread <thread-id>`.
- **Flag-for-human** — anything touching logic, behaviour, the
  three-layer separation, data/content facts, auth/RLS, dependencies, or
  architecture (the surfaces `engineering-principles` and
  `three-layer-separation` protect). Reply with a short assessment
  (valid / won't-fix / needs-human) and leave the thread **unresolved**
  for the human. Do not auto-fix these.

If Copilot posts no inline comments, report "Copilot: no issues" and skip
straight to step 13. If the watcher times out, report it plainly and tell
the owner to confirm Copilot review is enabled and assigned, then proceed
to step 13.

## Hard rules

- Never `gh pr merge` — Claude opens the PR; a human merges it.
- Never open a non-draft PR.
- Never open a PR with verification-loop red or an unresolved High
  security finding.
- Copilot is an additional reviewer, not a gate Claude clears by editing.
  Only safe items are auto-fixed; substantive comments are flagged and
  left unresolved for the human. Auto-fixing to silence a comment, or
  resolving a thread without addressing it, is forbidden.
- Fixes go through `/code-push`; never commit Copilot fixes with
  `--no-verify` or any gate bypassed.
