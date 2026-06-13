---

name: verification-loop
description: The single quality gate before /handoff and at any natural pause point in a long session. Runs secret scan, lint, typecheck, unit tests, build, a11y smoke, and the three-layer grep checks. Returns a pass/fail report; do not proceed past failures.
triggers:
  - "verify"
  - "lint"
  - "typecheck"
  - "build check"
  - "quality gate"
  - "pre-handoff check"
  - "verification"
  - "run checks"
context: fork
allowed-tools:
  - Bash
  - Read
argument-hint: ""
---
# Skill: verification-loop

The hard gate before any diff can leave the working tree. Single git repo;
SPEC.md is the source of truth.

## Important: scaffold dependency

The `npm run *` scripts below exist only AFTER Phase 1 scaffolds
`package.json` (SPEC.md section 18). Before Phase 1, run only the
secret scan and the three-layer grep checks; mark the npm steps as
N/A (no package.json yet) rather than failing them.

## Canonical command sequence

Run in this order. Stop at the first failing step; do not run the rest.

```
# 0. Secret scan runs from the repo root (covers harness + app).
.claude/scripts/scan-secrets.sh --staged        # or explicit <paths...>

# All app steps (lint..a11y) and the three-layer greps run from the app
# subdirectory. The app lives in salone-explorer/ (SPEC §12); cd in once.
cd salone-explorer

# 2. Lint (eslint incl. jsx-a11y)         [needs package.json]
npm run lint

# 3. Typecheck (tsc --noEmit)             [needs package.json]
npm run typecheck

# 4. Unit tests (vitest), if defined      [needs package.json]
npm run test:unit

# 5. Build                                [needs package.json]
npm run build

# 6. A11y smoke (Playwright + axe)        [needs a preview/dev server]
npm run test:a11y

# 7. Three-layer grep checks (see below)  - ALWAYS
```

The a11y step (`npm run test:a11y`) requires a running preview or dev
server (e.g. `npm run preview` on the built `dist/`, or `npm run dev`).
Start it first, or skip with an explicit note if no server is available.

## Three-layer grep checks (always run; both must return zero matches)

These enforce `.claude/rules/three-layer-separation.md`. Run them from the
app subdirectory (`cd salone-explorer` per the sequence above) so the
`src/...` targets resolve; from the repo root, prefix paths with
`salone-explorer/`. A grep that finds nothing because it pointed at the
wrong directory is a silent pass — never accept a zero-match result
without confirming the path exists.

```
# (a) No hard-coded English UI strings or known attraction names in the
#     CODE layer. Search src/components, src/pages, src/lib but EXCLUDE
#     src/lib/content. A non-empty result is a FAIL.
grep -rnE '"[A-Z][a-z]+( [A-Za-z]+){1,}"' \
  src/components src/pages src/lib \
  --include='*.ts' --include='*.tsx' \
  | grep -v 'src/lib/content/'
# Also grep for known attraction names (e.g. Tiwai Island, Bunce Island,
# River No. 2, Freetown) in the same scope - must be zero.

# (b) No component/page imports src/data/*.json directly. Data access
#     must go through the barrel src/lib/content/index.ts. Non-empty = FAIL.
grep -rnE "from ['\"].*src/data/.*\.json['\"]|import .*['\"].*/data/.*\.json['\"]" \
  src/components src/pages src/lib \
  --include='*.ts' --include='*.tsx' \
  | grep -v 'src/lib/content/'
```

Tests and the `src/data/` / `src/content/` files themselves are the only
places literals are permitted; the greps above already exclude the code
layer's content barrel.

## Report format

Output a PASS/FAIL table. Overall result is FAIL if any step fails.

| Step          | Command                       | Exit | Result | Notes |
| ------------- | ----------------------------- | ---- | ------ | ----- |
| secret scan   | scan-secrets.sh --staged      | 0    | PASS   |       |
| lint          | npm run lint                  | 0    | PASS   |       |
| typecheck     | npm run typecheck             | 1    | FAIL   | foo.ts:14 |
| unit tests    | npm run test:unit             | -    | SKIP   | typecheck failed |
| build         | npm run build                 | -    | SKIP   |       |
| a11y smoke    | npm run test:a11y             | -    | SKIP   |       |
| 3-layer (a)   | grep code-layer strings       | -    | SKIP   |       |
| 3-layer (b)   | grep direct json imports      | -    | SKIP   |       |

End with a single line: `OVERALL: PASS` or `OVERALL: FAIL (<step>)`.

## Hard rules

- Do not proceed past any FAIL. Fix it, re-run from step 1.
- Never silence a check (eslint-disable jsx-a11y, weaken a grep, skip the
  scan) to make the gate green.
