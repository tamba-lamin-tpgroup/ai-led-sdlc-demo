# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository state

This directory currently contains only specification artefacts — no application code has been scaffolded yet:

- `SPEC.md` — the single source of truth. Read it before generating any code. It is authoritative over this file when they disagree.
- `README.md` — the public-facing project front door. Mirrors `SPEC.md` at a higher level.
- `STUDENT_GUIDE.md` — teaching narrative documenting how `SPEC.md` was authored. Not a build artefact; do not generate code from it.

The project target is **Salone Explorer**, a Sierra Leone tour-guide SPA published by TpGroup (SL) Limited under the **FambulTik** brand. Target GitHub remote: `git@github.com:click2tman/ai-led-sdlc-demo.git`. Target deploy: Vercel (Vite preset).

When scaffolding, follow `SPEC.md` §19 (Delivery Workflow) phase by phase, and commit at the end of each phase.

## Non-negotiable architectural rules

These are the rules most likely to be violated by an AI agent and cause the most damage. They come from `SPEC.md` §5 and §22.

### Three-layer separation: code, data, content

Every file belongs to exactly one layer. The layer dictates where it lives:

| Layer   | Path                                        | Holds                                                            |
| ------- | ------------------------------------------- | ---------------------------------------------------------------- |
| Code    | `src/components/`, `src/pages/`, `src/lib/` | React components, route handlers, business logic. No strings. No facts. |
| Data    | `src/data/*.json`                           | Attraction records, region lookups, taxonomies.                  |
| Content | `src/content/*.json`                        | All user-facing strings, page copy, microcopy, disclaimer.       |

**Hard rule — no exceptions:** if you are about to type an English string (`"Schedule a Tour"`) or an attraction fact (`"Tiwai Island"`, `8.4831`, opening hours) inside a `.tsx` or `.ts` file, stop. The string goes in `src/content/strings.en.json` and is read via `t("namespace.key")`. The fact goes in `src/data/attractions.json` and is read through the `attractions` repository. Tests and `src/data/`/`src/content/` themselves are the only places literals are allowed.

Verification: a grep for hard-coded English strings or known attraction names anywhere under `src/components/`, `src/pages/`, or `src/lib/` (excluding `src/lib/content/`) must return zero matches.

### Repository pattern for all data access

Components and pages must never import `attractions.json` directly. They consume `attractions` from the barrel module `src/lib/content/index.ts`. The barrel picks the implementation based on `VITE_ATTRACTIONS_SOURCE`:

- `file` (default, Phase 1) — `fileAttractionRepository` reads JSON.
- `supabase` (Phase 2.5) — `supabaseAttractionRepository` reads Postgres.
- `payload` (Phase 8, future) — to be added.

When adding any new domain type, define the interface first, add the file-based implementation, then optionally the Supabase one. Never bypass the repository to "just read the JSON."

### Strings indirection

`src/lib/content/strings.ts` exports `t(key)`. All copy flows through it. Strings never contain HTML — compose rich text in components from multiple keys.

### Other guardrails (see `SPEC.md` §22)

- Do not invent attraction facts. Paraphrase from the five sources listed in `SPEC.md` §4. When a fact is unconfirmed, set `hours.notes: "Hours vary — confirm locally"`.
- Do not add libraries beyond `SPEC.md` §3 without justification in a code comment.
- Do not store secrets in client code. Only `VITE_`-prefixed env vars are exposed to the browser.
- Do not disable RLS, weaken CI, or `eslint-disable` `jsx-a11y` rules to make builds pass.
- Do not ship without the disclaimer in three places: Home alert, footer, `/about`.
- Stop and ask before deviating from §5 (architecture), §6.1 (`Attraction` type), §6.3 (Supabase schema), §8 (brand), §10 (a11y), or §12 (project structure).

## Commands (post-scaffold)

These commands are defined in `SPEC.md` §18 and will be wired in `package.json` once Phase 1 scaffolding is complete. They do not work until then.

| Command                       | Purpose                                                              |
| ----------------------------- | -------------------------------------------------------------------- |
| `npm run dev`                 | Vite dev server at `http://localhost:5173`.                          |
| `npm run build`               | `tsc --noEmit` + bundle + `generate-sitemap` + `vite-plugin-prerender`. |
| `npm run preview`             | Serve `dist/`.                                                       |
| `npm run lint`                | ESLint including `jsx-a11y` recommended. Errors fail the build.      |
| `npm run typecheck`           | `tsc --noEmit` standalone.                                           |
| `npm run test:a11y`           | Playwright + `@axe-core/playwright` smoke across five routes.        |
| `npm run migrate:attractions` | Phase 2.5: upsert `src/data/attractions.json` into Supabase.         |

Run a single Playwright spec with `npx playwright test tests/a11y/smoke.spec.ts -g "name of test"`.

Node 20+ required.

## Branching and CI

Merges to `main` require four workflows green: `ci.yml`, `codeql.yml`, `security.yml`, `a11y.yml`. The a11y workflow fails on serious or critical axe violations on `/`, `/attractions/tiwai-island`, `/about`, `/signin`, `/signup`.

## Phase 2 (Supabase) preconditions

Before touching auth or any user-scoped feature, Supabase must be provisioned and `supabase/schema.sql` (from `SPEC.md` §6.3) applied. Every user-scoped table — `profiles`, `saved_attractions`, `tour_bookings` — has RLS enabled with `auth.uid() = user_id` policies. Never add a new user-scoped table without an RLS policy in the same migration.

## Branding constants

- Publisher: TpGroup (SL) Limited.
- Brand: FambulTik (Krio: *family stick*).
- Design system: [design.tpgroupsl.com](https://design.tpgroupsl.com/). All component visuals derive from tokens in `src/styles/tokens.css` (see `SPEC.md` §8.4 for the full token table). Tailwind reads them as CSS variables.
- Logo assets live in `src/assets/brand/fambultik/`.
