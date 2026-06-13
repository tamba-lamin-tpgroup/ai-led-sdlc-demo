---
description: Contract conventions for Salone Explorer. Path-scoped - applies when editing the repository barrel, domain types, content keys, or the Supabase schema. A contract is anything another layer or module depends on.
paths:
  - "**/src/lib/content/**"
  - "**/src/data/**"
  - "**/src/content/**"
  - "**/supabase/**"
  - "**/*.schema.json"
  - "**/schema.sql"
---

# Rule: contract conventions

A contract is anything another layer or module depends on: the
`Attraction` type, the repository interface, the content string keys, the
Supabase schema. Treat changes here with care - they ripple.

## The repository contract

- Components and pages consume `attractions` from the barrel
  `src/lib/content/index.ts`. They never import `src/data/*.json`.
- The barrel selects the implementation from `VITE_ATTRACTIONS_SOURCE`:
  `file` (default), `supabase` (Phase 2.5), `payload` (Phase 8).
- Adding a new domain type: **define the interface first**, then the
  file-based implementation, then optionally Supabase. Never bypass the
  repository.
- The `Attraction` type in `src/lib/content/types.ts` is canonical and
  matches `SPEC.md` section 6.1. Do not diverge from it without an ADR.

## The content contract

- All user-facing copy lives in `src/content/strings.en.json` and is
  read via `t("namespace.key")` from `src/lib/content/strings.ts`.
- Keys are dot-namespaced: `home.hero.heading`, `cta.scheduleTour`.
- Strings never contain HTML. Compose rich text from multiple keys in
  the component.
- Renaming a key: add the new key, migrate all read sites in the same
  PR, then remove the old. Never rename in place and leave dangling
  `t()` calls.

## The data contract

- `src/data/attractions.json` records match the `Attraction` type
  exactly. Schema-validated.
- Do not invent facts. Paraphrase from the five sources in SPEC.md
  section 4. Unconfirmed hours -> `hours.notes: "Hours vary - confirm
  locally"`.

## The Supabase contract (Phase 2+)

- `supabase/schema.sql` is canonical and matches `SPEC.md` section 6.3.
- Every user-scoped table (`profiles`, `saved_attractions`,
  `tour_bookings`) has RLS enabled with `auth.uid() = user_id` policies.
- **Never add a user-scoped table without an RLS policy in the same
  migration.** Never disable RLS.
- Schema changes require an ADR and a migration; they do not edit data
  in place.

## Routes

- Route paths are kebab-case nouns: `/attractions`,
  `/attractions/:slug`, `/about`, `/signin`, `/signup`, `/account`.
- No verbs in route paths.

## Forbidden

- Importing `src/data/*.json` directly from a component or page.
- Inlining a user-facing string instead of using `t()`.
- Renaming a type field or content key in place without migrating all
  consumers in the same PR.
- Adding a user-scoped Supabase table without an RLS policy.
- Diverging the `Attraction` type or Supabase schema from SPEC.md
  without an ADR.
