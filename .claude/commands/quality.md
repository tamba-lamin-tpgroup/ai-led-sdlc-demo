---
description: Full quality gate — runs verification-loop, unit tests (Vitest), accessibility audit (Playwright + axe), and secret scan, with an optional E2E step. Use before any PR or promotion. Prints a PASS/FAIL matrix.
argument-hint: "[--skip-e2e]"
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, Agent
---

# /quality

The comprehensive quality gate. Chains the quality skills in the correct
order. Exits on the first blocker — fix it, then re-run.

All `npm run` commands below exist only after Phase 1 has scaffolded
`package.json` (SPEC.md section 18). Before that, the gate reports each
step as `SKIP (no package.json)`.

## Arguments

| Argument     | Default | Description                                              |
|--------------|---------|----------------------------------------------------------|
| `--skip-e2e` | false   | Skip the optional E2E step — use for the fast inner loop  |

Parse `$ARGUMENTS`.

## Procedure

### Step 1 — Verification loop (mandatory gate)
Run the `verification-loop` skill: `npm run lint` (ESLint incl.
`jsx-a11y`), `npm run typecheck` (`tsc --noEmit`), `npm run build`, the
secret scan, and dead-code check. Stop on any failure. Do not proceed.

### Step 2 — Unit tests (Vitest)
Run the `unit-testing` skill (`vitest run`). Stop on any test failure.

### Step 3 — Accessibility audit (Playwright + axe)
Run the `accessibility-testing` skill: `npm run test:a11y` (Playwright +
`@axe-core/playwright`) across the five gated routes — `/`,
`/attractions/tiwai-island`, `/about`, `/signin`, `/signup`. Fail on any
serious or critical axe violation (matches the `a11y.yml` gate).

### Step 4 — Secret scan (final check)
Run the `secret-scanning` skill on all staged and unstaged changes
(`.claude/scripts/scan-secrets.sh`). Block on any finding.

### Step 5 — E2E (optional; skipped with --skip-e2e)
Run the `e2e-testing` skill (Playwright) only if a preview server is
available (`npm run preview` serving `dist/`). If no server is up, report
`SKIP (no preview server)`; do not start one implicitly.

### Output
Print a pass/fail matrix:

```
[PASS] verification-loop
[PASS] unit-testing (vitest)
[FAIL] accessibility-testing  — 2 serious violations on /signup (see <path>)
[PASS] secret-scanning
[SKIP] e2e-testing (no preview server)
```

If all gates pass: print "Quality gate passed. Run /handoff to open the PR."
If any gate fails: print the failing output and stop.
