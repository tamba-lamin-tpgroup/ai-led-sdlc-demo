# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository state

This directory currently contains only specification artefacts — no application code has been scaffolded yet:

- `SPEC.md` — the single source of truth. Read it before generating any code. It is authoritative over this file when they disagree.
- `README.md` — the public-facing project front door. Mirrors `SPEC.md` at a higher level.
- `STUDENT_GUIDE.md` — teaching narrative documenting how `SPEC.md` was authored. Not a build artefact; do not generate code from it.

The project target is **Salone Explorer**, a Sierra Leone tour-guide SPA published by TpGroup (SL) Limited under the **FambulTik** brand. Target GitHub remote: `git@github.com:tamba-lamin-tpgroup/ai-led-sdlc-demo.git`. Target deploy: Vercel (Vite preset).

**Live-demo scope:** this repository is the **live, in-class demonstration** and delivers **Phase 1 — Static foundation only**. `SPEC.md` documents the full roadmap (Phases 1–11) for context, but do not build beyond Phase 1 here unless explicitly asked. The `salone-explorer/` app is scaffolded live during the demo — it is intentionally absent at the start.

When scaffolding, follow `SPEC.md` §19 (Delivery Workflow) phase by phase, and commit at the end of each phase.

## Repository layout: app vs harness (binding)

The shippable application and the AI-led SDLC harness live in **separate
trees** so the production artefact never contains the tooling:

```
ai-led-sdlc-demo/          <- repo root: harness + docs + spec only
├── .claude/               <- AI harness (NOT deployed)
├── docs/                  <- documentation (NOT deployed)
├── SPEC.md  README.md     <- spec + front door
└── salone-explorer/       <- the Vite app — the ONLY thing Vercel builds
    ├── package.json  vite.config.ts  tsconfig.json
    └── src/{components,pages,lib,data,content,...}
```

- The app is scaffolded into `salone-explorer/` (a repo subdirectory),
  not the repo root. `npm create vite@latest salone-explorer` (SPEC §19
  Phase 1) already produces this folder.
- **Vercel Root Directory = `salone-explorer`.** Vercel clones the repo
  but builds only from there, so `.claude/`, `docs/`, and other
  repo-root files are excluded from the deployment by construction.
- **Run app commands from inside the app dir:** `cd salone-explorer`
  before `npm run ...`. CI workflows set `working-directory: salone-explorer`.
- **Path convention:** `src/...` paths in this file and the rules are
  relative to `salone-explorer/`. Harness checks that run from the repo
  root (e.g. the three-layer grep in `verification-loop`) `cd salone-explorer`
  first, or target `salone-explorer/src/...`.

## AI harness (`.claude/`)

This repo ships an AI-led SDLC harness: subagents, governance hooks,
rules, skills, and slash commands. Full reference: `docs/dev-guide/claude-harness.md`.

- **Rules** in `.claude/rules/` are loaded every session and are binding:
  `three-layer-separation` (keystone), `engineering-principles`,
  `spec-first`, `commit-conventions`, `branch-conventions`,
  `test-conventions`, `api-conventions`, `80-20-split`.
- **Sessions are mandatory** for development work: `/session-start` →
  `/session-update` → `/session-end`. The session file is the durable
  memory between sessions.
- **Governance is enforced by hooks**: code-producing prompts must
  reference a SPEC phase/section or a GitHub issue; commits need a
  `Requirement:`/`Phase:`/`Incident:` trailer; new source files need a
  one-line header; secrets, force-push, `reset --hard`, `--no-verify`,
  and `gh pr merge` are hard-blocked.
- **Tool-agnostic floor** (`.githooks/`): a `commit-msg` trailer gate and
  a `pre-commit` secret-scan / new-file-header / three-layer grep run on
  every commit regardless of which AI authored it. Install per clone with
  `.claude/scripts/install-git-hooks.sh`. See
  `docs/dev-guide/multi-tool-enforcement.md`.
- **Activation** (one-time, human-only): move `.claude/settings.json.proposed`
  to `.claude/settings.json` and copy `settings.local.json.template` to
  `settings.local.json`, then restart Claude Code. Run
  `.claude/scripts/install-git-hooks.sh` to wire the git-hook floor.

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

These commands are defined in `SPEC.md` §18 and will be wired in `package.json` once Phase 1 scaffolding is complete. They do not work until then. Run them from the app directory: `cd salone-explorer` first.

| Command                       | Purpose                                                              |
| ----------------------------- | -------------------------------------------------------------------- |
| `npm run dev`                 | Vite dev server at `http://localhost:5173`.                          |
| `npm run build`               | `tsc --noEmit` + bundle + `generate-sitemap` + `vite-plugin-prerender`. |
| `npm run preview`             | Serve `dist/`.                                                       |
| `npm run lint`                | ESLint including `jsx-a11y` recommended. Errors fail the build.      |
| `npm run typecheck`           | `tsc --noEmit` standalone.                                           |
| `npm run test:a11y`           | Playwright + `@axe-core/playwright` smoke across five routes.        |
| `npm run migrate:attractions` | Phase 2.5: upsert `src/data/attractions.json` into Supabase.         |

Run a single Playwright spec with `npx playwright test tests/a11y/smoke.spec.ts -g "name of test"` (from `salone-explorer/`).

Node 20+ required.

## Branching and CI

Merges to `main` require four workflows green: `ci.yml`, `codeql.yml`, `security.yml`, `a11y.yml`. The a11y workflow fails on serious or critical axe violations on `/`, `/attractions/tiwai-island`, `/about`, `/signin`, `/signup`. All four run with `working-directory: salone-explorer` (the app subdirectory).

## Phase 2 (Supabase) preconditions

Before touching auth or any user-scoped feature, Supabase must be provisioned and `salone-explorer/supabase/schema.sql` (from `SPEC.md` §6.3) applied. Every user-scoped table — `profiles`, `saved_attractions`, `tour_bookings` — has RLS enabled with `auth.uid() = user_id` policies. Never add a new user-scoped table without an RLS policy in the same migration.

## Branding constants

- Publisher: TpGroup (SL) Limited.
- Brand: FambulTik (Krio: *family stick*).
- Design system: [design.tpgroupsl.com](https://design.tpgroupsl.com/). All component visuals derive from tokens in `src/styles/tokens.css` (see `SPEC.md` §8.4 for the full token table). Tailwind reads them as CSS variables.
- Logo assets live in `src/assets/brand/fambultik/`.
