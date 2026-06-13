---

name: unit-testing
description: Author and run unit tests with Vitest. Pure functions and small units, no network, no real DB beyond local fixtures. Use as the lowest-cost behaviour gate; one test per branch of the unit under test. Behaviour-named.
triggers:
  - "unit test"
  - "vitest"
  - "pure function test"
  - "mock"
  - "test coverage"
  - "unit spec"
context: fork
allowed-tools:
  - Bash
  - Read
argument-hint: "[<module> | <test-path>]"
---
# Skill: unit-testing

Smallest test type for Salone Explorer. Fast feedback. Runner: Vitest.

## Location and naming

Per `.claude/rules/test-conventions.md`:

- Tests live in `tests/unit/` (or co-located `*.test.ts(x)` per the
  Phase 1 scaffold choice - pick one convention and keep it).
- File mirrors the unit under test:
  `src/lib/content/strings.ts`
  -> `tests/unit/lib/content/strings.test.ts`.
- Names describe behaviour in plain English:
  good: `it("returns the key itself when the string id is missing")`;
  bad:  `it("calls resolve")`.

```
describe("t() string resolver", () => {
  it("returns the resolved copy for a known key", () => { ... });
  it("throws when the key namespace does not exist", () => { ... });
});
```

## High-value units to cover

- **Repository pattern** (`src/lib/content/`): the `file` implementation
  (`fileAttractionRepository` reading `src/data/attractions.json`) and,
  from Phase 2.5, the `supabase` implementation. Cover the barrel
  selecting the right one from `VITE_ATTRACTIONS_SOURCE`, plus list,
  get-by-slug, filter-by-region, and the empty/not-found paths.
- **The `t()` string resolver** (`src/lib/content/strings.ts`): known
  key resolves; missing key fails fast (no silent fallback); keys never
  return HTML.
- **Data validation**: attraction records parse against the `Attraction`
  type (SPEC.md section 6.1); malformed coordinates, missing required
  fields, and the `hours.notes: "Hours vary - confirm locally"` fallback.

## What belongs in a unit test

- Pure functions: input -> output, no side effects.
- Per-branch coverage: every `if`, every switch arm, every error path.
- Boundary conditions: empty, single, many, null, undefined, max, min.

## What does NOT belong here

- HTTP calls and real Supabase reads -> integration tests (Phase 2+,
  against a real local Supabase instance; no mocks for running systems).
- Browser interaction -> `skills/e2e-testing`.
- WCAG rendering checks -> `skills/accessibility-testing`.

## Run commands

```
# Single test by name
npx vitest run tests/unit/lib/content/strings.test.ts \
  -t "returns the resolved copy for a known key"

# Whole unit suite (after Phase 1 scaffolds package.json)
npm run test:unit
# or directly:
npx vitest run
```

## Anti-patterns

- Mocking the unit under test. Test the real thing.
- Mocking a system that is actually running locally.
- Snapshot tests as the only assertion. Snapshots are a last resort.
- Tests that pass when behaviour is wrong. Re-run with the bug in place
  to confirm the test catches it.
- Defaulting a result to "passed"; the assertion must observe a signal.
