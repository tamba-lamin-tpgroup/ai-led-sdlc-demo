---

name: e2e-testing
description: Drive a real browser through the running Salone Explorer app with Playwright. Slow, flaky-prone, expensive; reserve for the user journeys whose breakage is most visible. Needs a running dev or preview server.
triggers:
  - "end-to-end"
  - "e2e"
  - "playwright"
  - "browser test"
  - "user journey"
  - "full stack test"
  - "smoke e2e"
context: fork
allowed-tools:
  - Bash
  - Read
argument-hint: "[<route> | <spec-path>]"
---
# Skill: e2e-testing

The most-realistic, most-expensive test type. Spend it carefully.
Runner: Playwright (`@playwright/test`).

## When to use

- Critical user journeys end to end through the rendered app.
- Multi-page flows and primary CTAs.
- Auth-gated flows once Phase 2 (auth + account) lands.

## When NOT to use

- Single-unit behaviour (use `skills/unit-testing`).
- WCAG/axe rendering checks (use `skills/accessibility-testing`).
- Repository or validation logic (use `skills/unit-testing`).

## User journeys to cover

Phase 1 (public, no auth):

- Browse attractions: open `/`, navigate the attractions list.
- View an attraction detail page, e.g. `/attractions/tiwai-island`.
- Reach `/about` and confirm the disclaimer is present.

Phase 2 (auth + account; SPEC.md Phase 6):

- Sign in via `/signin`; sign up via `/signup`.
- Bookmark an attraction; favorite an attraction.
- Schedule a tour (tour booking flow).
- View My Account and see saved/booked items.

## RLS and auth-state notes (Phase 2)

- Tests run with real auth state. Persist a signed-in session via a
  Playwright storage-state fixture in `tests/fixtures/`; do not log in
  through the UI in every spec.
- Cover the RLS boundary at the journey layer: a signed-in user sees
  only their own bookmarks / favorites / bookings; a second user never
  sees the first user's records, and a signed-out visitor cannot reach
  account-scoped routes.
- Never embed real credentials or the Supabase service-role key in a
  spec or fixture. Use seeded test users via env, scanned by
  `skills/secret-scanning`.

## Layout

```
tests/
  e2e/
    browse-attractions.spec.ts
    attraction-detail.spec.ts
    sign-in.spec.ts          # Phase 2
    bookmark-favorite.spec.ts # Phase 2
    schedule-tour.spec.ts     # Phase 2
  fixtures/
    users.ts
    storage-state.json        # Phase 2 signed-in session
```

## Run commands

E2E needs a running dev or preview server. Build then `npm run preview`,
or `npm run dev`, before running:

```
npx playwright test
npx playwright test tests/e2e/browse-attractions.spec.ts -g "name"
npx playwright test --headed --debug      # local debugging only
```

## Anti-patterns

- E2E tests that exercise validation logic. Move to unit tests.
- Hardcoded sleeps. Use Playwright's `waitFor*` / web-first assertions.
- Tests that depend on run order. Each spec is independent.
- Tests that hit a production deployment. Always local or a preview env.
