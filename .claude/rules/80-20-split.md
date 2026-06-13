---
description: The contract that defines what AI does (80 percent) and what humans do (20 percent) on Salone Explorer. Loaded for every session.
---

# Rule: the 80 / 20 split

This rule encodes the AI-led operating model. It applies repo-wide.

## What AI does (the 80 percent)

- Read SPEC.md, the GitHub issue, and any linked artefacts.
- Produce the context pack (`/orchestrate`).
- Write the implementation plan and wait for approval (`plan-then-code`).
- Implement the plan: code, data, content, tests, docs - respecting the
  three-layer separation.
- Run the verification loop: lint, typecheck, unit tests, a11y smoke,
  secret scan, build.
- Spawn `code-reviewer` and `security-reviewer` for first-pass review.
- Update README, in-code headers, ADRs as required.
- Open the draft PR with a complete description (`/handoff`).

## What humans do (the 20 percent)

- Approve the plan before implementation begins.
- Sign off on architecture decisions (ADRs) and any SPEC deviation.
- Review the draft PR and apply judgement.
- Resolve ambiguous requirements.
- Final security and business-logic sign-off.
- Click merge. (Claude is denied this action by `settings.json`.)

## Hard boundaries (enforced by hooks and settings)

- Claude must not run `gh pr merge`.
- Claude must not `git push --force` or `git reset --hard`.
- Claude must not bypass hooks (`--no-verify`).
- Claude must not introduce secrets; the secret scanner blocks the
  commit.
- Claude must not deviate from SPEC.md section 5, 6.1, 6.3, 8, 10, or 12
  without stopping to ask.

## What this rule is NOT

This is not a model of what Claude is *capable* of - Claude can do the
20 percent. It is a *responsibility* model: the human is the accountable
party for those steps. Routing them through a human is what makes the
program AI-Led, not AI-only.
