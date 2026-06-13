---
description: Branch model and lifecycle for Salone Explorer. Simple two-branch model - feature branches from dev, promote dev to main behind the four CI gates. Hotfix from main. Loaded every session.
---

# Rule: branch conventions

## The two long-lived branches

| Branch | Purpose                                                            | Protection                                   |
| ------ | ----------------------------------------------------------------- | -------------------------------------------- |
| `dev`  | Integration trunk. All feature work merges here first.            | CI must be green                             |
| `main` | Production. Deployed to Vercel. Tagged for release.               | `ci.yml`, `codeql.yml`, `security.yml`, `a11y.yml` all green + 1 human approval |

Promotion is one-directional: `dev -> main`. Feature work never targets
`main` directly. Hotfix is the only exception.

## Branch types

| Type      | Naming                          | Source | Target            |
| --------- | ------------------------------- | ------ | ----------------- |
| Feature   | `issue-<num>-<slug>`            | `dev`  | `dev`             |
| Bugfix    | `fix-<num>-<slug>`              | `dev`  | `dev`             |
| Chore     | `chore-<slug>`                  | `dev`  | `dev`             |
| Promotion | `promote-dev-to-main-<date>`    | `dev`  | `main`            |
| Hotfix    | `hotfix-<num>-<slug>`           | `main` | `main` (then back-merge to dev) |

`<slug>` is lowercase-kebab-case, derived from the issue/phase title,
max 40 chars. For phase work without an issue, use a descriptive slug:
`phase-3-accessibility`, `phase-5-supabase-schema`.

## Feature lifecycle

```
1. git fetch origin
2. git checkout -b issue-<num>-<slug> origin/dev          (always from dev)
3. Commit small, push often. /code-push enforces conventions.
4. verification-loop green; /handoff opens a draft PR -> dev
5. CI green + 1 human approval
6. Squash-merge to dev (human action)
7. Delete the branch on merge
```

## Promotion lifecycle (dev -> main)

Promotions move accumulated dev work to production.

```
git fetch origin
git checkout -b promote-dev-to-main-2026-06-05 origin/dev
/handoff      # opens the promotion PR dev -> main
```

The promotion PR must have all four CI workflows green before merge:

- `ci.yml`        - lint, typecheck, unit tests, build
- `codeql.yml`    - static analysis
- `security.yml`  - SAST / secret scan
- `a11y.yml`      - Playwright + axe on `/`, `/attractions/tiwai-island`,
                    `/about`, `/signin`, `/signup`; fails on serious or
                    critical violations

After merge to main, Vercel deploys automatically. Tag main `vN.N.N`.

## Hotfix lifecycle

The only path that bypasses dev. Use only when production has a defect
that cannot wait.

```
1. git fetch origin
2. git checkout -b hotfix-<num>-<slug> origin/main
3. Smallest viable diff. No drive-by changes.
4. /code-push, /handoff opens the hotfix PR -> main.
5. CI green + 1 human approval.
6. Merge to main; tag vN.N.N+1.
7. Back-merge to dev so history stays aligned.
8. Open a follow-up issue to add a regression test if not already added.
```

Hotfix work references a `docs/incidents/<id>.md` entry (spec-first rule
still applies; incidents count as a source).

## What is forbidden

- Branching from a stale source. Always `git fetch` first.
- Branching from another feature branch.
- Reusing a branch name across issues.
- Working on `dev` or `main` directly.
- Force-pushing `dev` or `main` (denied by hook and branch protection).
- Creating a feature branch from `main` (hotfix is the only exception).
- Merging a hotfix without back-merging to dev.

## Cross-references

- `commit-conventions.md` - message format + required trailers
- `spec-first.md` - every change traces to SPEC.md
- `CLAUDE.md` - the four CI workflows required to merge to main
