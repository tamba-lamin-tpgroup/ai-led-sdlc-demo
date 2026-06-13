# Automated Copilot review in `/handoff`

GitHub Copilot is the third reviewer in the handoff loop, added after the
two local review agents (`code-reviewer`, `security-reviewer`). The flow
is automatic on every `/handoff`: once the draft PR is open, Claude
requests a Copilot review, watches for it in the background, resolves the
safe comments, and hands back to a human for final review and merge.

Claude never merges — Copilot is a reviewer, not a gate Claude clears.

## The loop

```
/handoff
  -> verification-loop, code-reviewer, security-reviewer   (unchanged)
  -> open draft PR, comment URL on issue                   (unchanged)
  -> copilot-review.sh request <pr>                        (add Copilot reviewer)
  -> copilot-review.sh watch <pr> &  (background)          (poll until review)
  -- harness re-invokes Claude when the watcher exits --
  -> classify each Copilot thread:
       safe   -> fix + verification-loop + /code-push + resolve-thread
       flag   -> reply with assessment, leave unresolved for the human
  -> ping the owner: summary + human checklist
```

The watcher runs as a backgrounded Bash process so the handoff turn
completes. Polling does not consume model turns; the harness re-invokes
Claude with the watcher's output when Copilot responds (or on timeout).

## The script: `.claude/scripts/copilot-review.sh`

One source of truth for the GitHub mechanics. `set -euo pipefail`, fails
loudly with context (no silent fallbacks).

| Subcommand                 | Does                                                              |
| -------------------------- | ---------------------------------------------------------------- |
| `request <pr>`             | Best-effort add of `Copilot` as a reviewer, then verify. GitHub answers 201 but silently drops the bot unless Copilot code review is enabled for the repo, so the script checks `requested_reviewers` and exits `3` (not a false success) when it could not add it. Exit `0` when Copilot is requested (added now or already was). |
| `watch <pr>`               | Poll `pulls/<pr>/reviews` for a Copilot review, then emit its threads as JSON to stdout and `.claude/sessions/copilot-review-<pr>.json`. |
| `resolve-thread <node-id>` | GraphQL `resolveReviewThread` — used only after a comment is actually fixed. |

### Environment

| Var                     | Default | Meaning                          |
| ----------------------- | ------- | -------------------------------- |
| `COPILOT_POLL_INTERVAL` | `20`    | Seconds between polls.           |
| `COPILOT_POLL_TIMEOUT`  | `1200`  | Seconds before the watch gives up. |

### Watch output shape

```json
{
  "threads": [
    {
      "id": "<thread-node-id>",
      "isResolved": false,
      "isOutdated": false,
      "path": "salone-explorer/src/...",
      "line": 42,
      "url": "https://github.com/.../#discussion_r...",
      "body": "Copilot's comment text"
    }
  ]
}
```

Empty `threads` means Copilot reviewed with no inline comments — report
"Copilot: no issues" and skip to the owner ping.

## Resolution policy

Conservative by design; the 80/20 split and `plan-then-code` stay intact
for anything material.

- **Safe-to-autofix** — typos, lint-level nits, obvious null/guard
  additions, doc or comment wording. Fix it, re-run `verification-loop`,
  `/code-push` (so the secret scan, three-layer grep, new-file-header,
  and trailer gates all run), reply on the thread, then `resolve-thread`.
- **Flag-for-human** — anything touching logic, behaviour, the
  three-layer separation, data/content facts, auth/RLS, dependencies, or
  architecture. Reply with an assessment (valid / won't-fix /
  needs-human) and leave the thread **unresolved**. Never auto-fix these,
  never resolve a thread without addressing it, never edit to silence a
  comment.

## Failure modes

- **Watch timeout** — Copilot did not review within
  `COPILOT_POLL_TIMEOUT`. The script exits non-zero with a clear message;
  `/handoff` reports it and tells the owner to confirm Copilot review is
  enabled and assigned, then proceeds to the owner ping.
- **`gh pr view --json reviewRequests` shows no bot** — expected. That
  field omits bot reviewers. Verify the request with
  `gh api repos/<owner>/<repo>/pulls/<pr>/requested_reviewers`.
- **Permission denied requesting a reviewer or resolving a thread** —
  the `gh` token needs push access on the repo. The script fails loudly
  rather than continuing as if the request succeeded.

## Triggering the review (important)

The API will not add the Copilot bot to `requested_reviewers` unless
Copilot code review is enabled for the repository. With that disabled,
the POST returns 201 but the bot is dropped (`request` then exits `3`).
The GraphQL `requestReviews` mutation cannot substitute — it takes
`userIds`, and Copilot is a Bot, not a User. So one of the following must
hold for the trigger to be automatic:

- **Repo-level auto-request** (recommended): an admin enables
  Settings -> Code review -> Automatically request Copilot code review.
  Every new PR then gets Copilot without any API call; the watcher and
  resolve steps run unchanged. (Requires admin; a `repo`-scope token
  without admin cannot set this.)
- **Manual click**: a human uses the PR's Reviewers menu to request
  Copilot. The watcher picks it up from there.

The `request` subcommand stays in the loop as a best-effort attempt plus
a clear instruction when it cannot add the bot. The durable automation is
the watch -> classify -> resolve -> ping half, which works however the
review was triggered.

## Preconditions

- Copilot code review enabled for the repository (repo-level auto-request
  or a manual reviewer request). Without it, `request` exits `3`.
- `gh` authenticated with `repo` scope (push).
