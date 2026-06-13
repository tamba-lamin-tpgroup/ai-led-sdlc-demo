---

name: tdd-workflow
description: Use when the change is well-specified and behaviour-driven. Authors failing Vitest tests for each acceptance criterion first, confirms they fail for the expected reason, then writes the minimum production code to pass them, then refactors.
triggers:
  - "TDD"
  - "test-driven development"
  - "red-green-refactor"
  - "failing test first"
  - "write test first"
context: fork
allowed-tools:
  - Bash
  - Read
  - Write
argument-hint: "<feature-description or AC reference>"
---
# Skill: tdd-workflow

Red -> green -> refactor with Vitest for Salone Explorer.

## Procedure

1. **Read** the acceptance criteria from the SPEC.md phase/section or the
   GitHub issue this work traces to.
2. **List** the tests you will write (one per AC, plus edge cases).
   Behaviour-named; see `.claude/rules/test-conventions.md`.
3. **Red - author failing tests first.** Run them. Confirm each fails
   with a message that names the missing behaviour, not a syntax or
   import error.
4. **Green - implement** the minimum code to pass exactly those tests.
   Hold the three-layer boundary: strings to `src/content/*.json`, facts
   to `src/data/*.json`, logic to the code layer; data access through the
   `src/lib/content/index.ts` barrel.
5. **Run** the full file/module suite. Confirm green.
6. **Refactor** for clarity only. Do not add behaviour. Re-run tests.
7. **Commit** with a message that names the AC / SPEC reference and the
   test file (see `.claude/rules/commit-conventions.md`).

## Test location and naming

Per `.claude/rules/test-conventions.md`:

- Unit tests live in `tests/unit/` (or co-located per the Phase 1
  scaffold choice - pick one convention and keep it).
- File mirrors the unit under test, e.g.
  `src/lib/content/file-attraction-repository.ts`
  -> `tests/unit/lib/content/file-attraction-repository.test.ts`.
- Names describe behaviour in plain English:
  good: `it("returns an empty list when no attractions match the region")`;
  bad:  `it("calls filterByRegion")`.

## Commands

```
# Run a single test by name
npx vitest run tests/unit/lib/content/file-attraction-repository.test.ts \
  -t "returns an empty list when no attractions match the region"

# Watch a file while implementing
npx vitest tests/unit/lib/content/file-attraction-repository.test.ts

# Whole unit suite (after Phase 1 scaffolds package.json)
npm run test:unit
```

Note: `npm run test:unit` exists only after Phase 1 scaffolds
`package.json`; before then invoke `npx vitest run` directly.

## In-scope test phases (always include the last two)

When building a suite from acceptance criteria, cover in order: happy
path, negative, boundary, state/flow, integration (Phase 2 real local
Supabase), regression. Then, mandatory regardless of the AC:

- **Accessibility (Phase 7):** at least one a11y assertion per new route
  or interactive component. The deep WCAG smoke runs under
  `skills/accessibility-testing`; here, at minimum assert labels/roles
  on rendered markup.
- **Security (Phase 8):** at least one - XSS probe in user input, RLS
  enforcement (Phase 2+), and confirm no Supabase service-role key or
  other secret is referenced in client code.

## Rules

- Never edit a test to make a failing test pass.
- Never add a `skip` / `xit` without a tracking issue and a TODO linking
  it.
- Never default a test to "passed"; the assertion must observe a positive
  signal. Re-run with the bug in place to confirm the test catches it.
- If a behaviour cannot be tested, that is a design smell. Surface it.
