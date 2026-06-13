---
description: One-shot summary of work in progress. Active session, current branch and recent commits, working-tree state, active context packs, and open PRs.
allowed-tools: Bash, Read, Grep, Glob
---

# /status

Project heartbeat. Run any time you want a single screen of the state.
Single git repo — no submodule loop.

## Procedure

0. **Active session block** (if any):
   - `cat .claude/sessions/.current-session`
   - If non-empty, read that session file's frontmatter (id, started,
     layer, issue) and the last `### Update` block. Print verbatim.
   - If empty, print "no active session — run /session-start" and the
     three most-recent closed sessions (id, ended, `## Outcomes` first
     line).

1. **Repo meta**:
   ```
   git config --get remote.origin.url
   git rev-parse --abbrev-ref HEAD
   ```

2. **Recent history and working tree**:
   ```
   git log --oneline -5
   git status --porcelain
   ```

3. **Active context packs**: `ls .claude/context-packs/*/state.md`; for
   each, `cat` it and label by issue number.

4. **Open PRs**:
   ```
   gh pr list --state open --json number,title,url,isDraft,baseRefName
   ```
   Note the base of each (PRs to `dev` are feature work; PRs to `main`
   are promotions or hotfixes).

5. **Output** as a single markdown summary: session -> branch + commits
   + tree -> context packs -> open PRs.
