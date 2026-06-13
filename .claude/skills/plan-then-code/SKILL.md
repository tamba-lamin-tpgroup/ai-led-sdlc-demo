---

name: plan-then-code
description: Use for any change beyond a one-line edit. Forces an explicit explore -> plan -> approve -> code -> verify -> commit cycle. The plan is approved by a human (or by the orchestrator on simple work) before any production file is edited.
triggers:
  - "plan"
  - "design approach"
  - "architecture decision"
  - "plan before coding"
  - "implementation plan"
  - "explore plan"
context: fork
allowed-tools:
  - Read
  - Bash
  - Write
argument-hint: "<issue-url, SPEC phase/section, or brief description>"
---
# Skill: plan-then-code

Implements the explore -> plan -> approve -> code -> verify -> commit
cycle for Salone Explorer. SPEC.md is the single source of truth; read
the relevant phase/section before planning. See `.claude/rules/spec-first.md`.

## Steps

### 1. Explore (no edits)

- Read the SPEC.md phase/section (or GitHub issue) this work traces to.
- Read every file the diff is likely to touch (use Glob + Read).
- Note which LAYER each file lives in: code (`src/components/`,
  `src/pages/`, `src/lib/`), data (`src/data/*.json`), or content
  (`src/content/*.json`). See `.claude/rules/three-layer-separation.md`.
- Output: a short list of "files I will touch" and "files I will read but
  not touch".

### 2. Plan

Produce a plan in this format:

```
## Plan

### Requirement
<SPEC.md phase (section 19) or section reference, or GitHub issue.
e.g. "SPEC Phase 3 - accessibility" or "SPEC section 6.1 - Attraction
type" or "#42". This must be a traceable source per spec-first.md.>

### Approach
<2-4 sentences. State the approach AND the alternative you rejected.>

### Pre-flight (re-confirm the four spec-first checks)
- Traceable source: <SPEC phase/section or issue - confirmed present>
- Phase preconditions met: <e.g. Phase 6 auth requires Phase 5 Supabase
  provisioned + supabase/schema.sql applied with RLS; or "none">
- Dependencies satisfied: <prior phase/issue done, or "none">
- Edge cases enumerated and correct phase sequence: <list>

### Files to change (by layer)
- src/lib/foo.ts [CODE]: <what changes - no strings, no facts>
- src/data/attractions.json [DATA]: <what facts change>
- src/content/strings.en.json [CONTENT]: <what copy changes>
- ...

### Files to add (by layer)
- src/lib/content/new-repository.ts [CODE]: <purpose>
- ...

WARNING: any English UI string belongs in CONTENT (src/content/*.json,
read via t()); any attraction fact belongs in DATA (src/data/*.json,
read via the attractions repository). Never inline either in the CODE
layer. Components/pages must import from the barrel
src/lib/content/index.ts, never src/data/*.json directly.

### Tests
- AC-N -> <unit | a11y | e2e> -> tests/<path>
- AC-N -> <unit | a11y | e2e> -> tests/<path>

### Risks
- <each risk + mitigation>

### Out of scope
- <what this PR will NOT do>
```

Stop. Wait for explicit approval before step 3.

### 3. Code

- Implement exactly what the plan said. If you discover the plan is
  wrong, stop and update the plan first.
- Smallest viable diff. No drive-by refactors.
- File header on every new file: `// <filename> - <one-line purpose>`.
- Hold the layer boundary: strings to content, facts to data, logic to
  code. Data access through the repository barrel only.

### 4. Verify

Run `skills/verification-loop`. Do not proceed past failures.

### 5. Commit

- Conventional message, imperative mood, max 72 chars first line. See
  `.claude/rules/commit-conventions.md`.
- Required traceability trailer: `Requirement: SPEC Phase <n> - <topic>`
  or `Phase: <n>` or `Requirement: <id>`.
- Issue trailer when one exists: `Refs: #<num>` or `Closes: #<num>`.
- No `Co-Authored-By` AI signatures. No `--no-verify`.

## Anti-patterns

- "Let me just quickly try something" without a plan.
- Editing more than the plan said. The plan is the contract.
- Skipping step 4 because "it's obviously fine".
- Inlining a UI string or attraction fact in the code layer "for now".
