---
description: Test file conventions. Path-scoped - applies when editing test files. Stack is Vitest (unit) + Playwright with axe-core (e2e/a11y).
paths:
  - "**/tests/**"
  - "**/*.test.ts"
  - "**/*.test.tsx"
  - "**/*.spec.ts"
  - "**/*.spec.tsx"
---

# Rule: test conventions

## Location

- Unit (Vitest):       `tests/unit/` or co-located `*.test.ts(x)` per the
  scaffold convention chosen in Phase 1 - pick one and keep it.
- E2E + a11y (Playwright): `tests/a11y/` and `tests/e2e/`.

Tests never sit beside production code unless the Phase 1 scaffold
explicitly adopts co-location. Default to `tests/`.

## Naming

- File mirrors the unit under test:
  - `src/lib/content/file-attraction-repository.ts`
    -> `tests/unit/lib/content/file-attraction-repository.test.ts`
- Test name describes behaviour in plain English:
  - good: `it("returns an empty list when no attractions match the region")`
  - bad:  `it("calls filterByRegion")`

## Authoring rules

- One behaviour per test. If you need many assertions, that is multiple
  tests.
- No mocks for systems running locally. A Phase 2 integration test hits
  the real local Supabase instance.
- No `skip` / `xit` / `test.skip` without a tracking issue and a TODO
  with the issue link.
- Test data lives in `tests/fixtures/`, not inline.
- Snapshot tests are a last resort. Prefer assertion on shape.

## Forbidden

- Editing a test to make a failing test pass.
- Weakening an assertion to make CI green.
- `eslint-disable`-ing a `jsx-a11y` rule in a component to dodge an a11y
  test.
- Removing a test because it is "flaky" without filing an issue first.

## Accessibility tests are not optional

The a11y CI gate (`a11y.yml`) runs Playwright + `@axe-core/playwright`
across five routes: `/`, `/attractions/tiwai-island`, `/about`,
`/signin`, `/signup`. It fails on serious or critical violations. Every
new route or interactive component adds or extends an a11y smoke test.

## Test generation structure (phases)

When authoring a suite from acceptance criteria, cover these in order:

| Phase | Type          | Notes                                                     |
| ----- | ------------- | --------------------------------------------------------- |
| 1     | Happy path    | Nominal success; one per acceptance criterion             |
| 2     | Negative      | Wrong input, missing required field, unauthenticated      |
| 3     | Boundary      | Empty list, min/max length, missing optional fields       |
| 4     | State / flow  | Repository source toggle, auth state transitions          |
| 5     | Integration   | Real Supabase (Phase 2+); RLS denies cross-user reads     |
| 6     | Regression    | Guards an existing behaviour touched by the change        |
| 7     | Accessibility | WCAG 2.2 AA: keyboard, focus, contrast, labels (axe)      |
| 8     | Security      | XSS probe in user input, RLS enforcement, no exposed keys |

### Rules

- Never default a test result to "passed". The assertion must observe a
  positive signal.
- Phase 7 (a11y) and Phase 8 (security) are mandatory - at least one
  each per feature, even if the acceptance criteria do not name them.
- Phase 5 (integration) hits real dependencies in the test environment;
  mocks are not accepted there.
