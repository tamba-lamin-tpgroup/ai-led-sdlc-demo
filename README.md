# Salone Explorer

> Discover Sierra Leone, one attraction at a time.

A mobile-first, **WCAG 2.2 Level AA**, SEO-, AEO-, and GEO-optimised tour-guide web app for Sierra Leone. Published by **TpGroup (SL) Limited** under the **FambulTik** brand and built on the [TpGroup Design System](https://design.tpgroupsl.com/). Architected around a strict **separation of code, data, and content** so editorial work never blocks engineering — and so the codebase is ready to migrate to **Payload CMS** without touching UI code.

[![CI](https://github.com/tamba-lamin-tpgroup/ai-led-sdlc-demo/actions/workflows/ci.yml/badge.svg)](https://github.com/tamba-lamin-tpgroup/ai-led-sdlc-demo/actions/workflows/ci.yml)
[![CodeQL](https://github.com/tamba-lamin-tpgroup/ai-led-sdlc-demo/actions/workflows/codeql.yml/badge.svg)](https://github.com/tamba-lamin-tpgroup/ai-led-sdlc-demo/actions/workflows/codeql.yml)
[![Security](https://github.com/tamba-lamin-tpgroup/ai-led-sdlc-demo/actions/workflows/security.yml/badge.svg)](https://github.com/tamba-lamin-tpgroup/ai-led-sdlc-demo/actions/workflows/security.yml)
[![A11y](https://github.com/tamba-lamin-tpgroup/ai-led-sdlc-demo/actions/workflows/a11y.yml/badge.svg)](https://github.com/tamba-lamin-tpgroup/ai-led-sdlc-demo/actions/workflows/a11y.yml)
[![WCAG 2.2 AA](https://img.shields.io/badge/WCAG-2.2%20AA-15803D)](https://www.w3.org/TR/WCAG22/)
[![Built with Claude Code](https://img.shields.io/badge/built%20with-Claude%20Code-7C3AED)](https://docs.claude.com/claude-code)

**Live demo:** [slint-ai-sldc-demo.tpgroupsl.com](https://slint-ai-sldc-demo.tpgroupsl.com) _(production domain; live after first deploy)_
**Vercel project:** [`slint-ai-led-sdlc-s-projects/slint-ai-led-sdlc-demo`](https://vercel.com/slint-ai-led-sdlc-s-projects/slint-ai-led-sdlc-demo) &middot; **Supabase project:** `slint-ai-led-sdlc-demo`

> **⚠️ Live-demo scope.** This repository hosts the **live, in-class demonstration**, which delivers **Phase 1 — Static foundation only**. The spec and docs describe the full roadmap (Phases 1–11) for context, but only Phase 1 is built here. The `salone-explorer/` app is scaffolded **live during the demo** and is intentionally absent from this repo at the start — the root holds only the spec, docs, CI config, and the `.claude/` harness.

---

## ⚠️ Disclaimer

> *Salone Explorer is built by TpGroup (SL) Limited under the **FambulTik** brand for **demonstration and educational purposes only**. It is not an official tourism service and does not represent any government body. Attraction details, opening hours, and ratings are curated from public sources and may be inaccurate or out of date. Always verify directly with the operator before travelling. No payments or real bookings are processed by this application.*

> **Phase 11 caveat.** The "no payments" statement above holds for the in-class build (Phases 1–7). The optional Stripe payments phase (Phase 11) requires this disclaimer to be revised before enabling live payments. See `SPEC.md` §17.

---

## Table of Contents

1. [Architecture — Code, Data, Content](#architecture--code-data-content)
2. [Brand & Design System](#brand--design-system)
3. [Features](#features)
4. [Tech Stack](#tech-stack)
5. [Getting Started](#getting-started)
6. [Environment Variables](#environment-variables)
7. [Project Structure](#project-structure)
8. [Data & Content Files](#data--content-files)
9. [Data Sources](#data-sources)
10. [Accessibility — WCAG 2.2 AA](#accessibility--wcag-22-aa)
11. [SEO, AEO & GEO](#seo-aeo--geo)
12. [Structured Data (JSON-LD)](#structured-data-json-ld)
13. [Mobile & Responsive Standards](#mobile--responsive-standards)
14. [Security & SAST](#security--sast)
15. [Supabase Backend (Phase 2)](#supabase-backend-phase-2)
16. [Migrating to Payload CMS (Future)](#migrating-to-payload-cms-future)
17. [Deployment](#deployment)
18. [Scripts](#scripts)
19. [Acceptance Criteria](#acceptance-criteria)
20. [Roadmap](#roadmap)
21. [Contributing](#contributing)
22. [License & Credits](#license--credits)

---

## Architecture — Code, Data, Content

Salone Explorer enforces a **three-layer separation**. This is the most important rule in the project.

| Layer       | Lives in            | Examples                                                       | Eventual home                    |
| ----------- | ------------------- | -------------------------------------------------------------- | -------------------------------- |
| **Code**    | `src/components/`, `src/pages/`, `src/lib/` | React components, route handlers, business logic. | Source repo.                     |
| **Data**    | `src/data/*.json`   | Attractions, regions, taxonomies.                              | Supabase (Phase 2.5) → Payload (Phase 8). |
| **Content** | `src/content/*.json`| UI strings, button labels, page copy, disclaimer.              | Payload CMS (Phase 8).           |

**Hard rule:** no component, page, or library file contains a user-facing string or an attraction fact. If you ever feel tempted to write `"Schedule a Tour"` or `"Tiwai Island"` inside a `.tsx` file — stop. The string belongs in `src/content/strings.en.json` (referenced via `t("schedule.button")`); the fact belongs in `src/data/attractions.json` (loaded through the repository).

### The repository pattern

All data access goes through a typed `AttractionRepository` interface with swappable implementations:

```ts
// Components only ever see this
import { attractions } from "@/lib/content";

const list = await attractions.getAll();
```

The implementation is chosen at build time by an env var:

| `VITE_ATTRACTIONS_SOURCE` | Implementation                                | When                              |
| ------------------------- | --------------------------------------------- | --------------------------------- |
| `file` (default)          | `fileAttractionRepository` reads JSON         | Phase 1                           |
| `supabase`                | `supabaseAttractionRepository` reads Postgres | Phase 2.5 (optional migration)    |
| `payload` *(future)*      | `payloadAttractionRepository` reads CMS API   | Phase 8                           |

UI never knows which backend served the data. Same pattern for the strings module — today it reads `strings.en.json`; tomorrow it reads Payload Globals.

### Why this matters

Hard-coding strings and data into components produces three failure modes every senior engineer has seen: editorial bottleneck (a button-label change needs a developer), no path to i18n, and content drift (the same term written three different ways in three components). Externalising data and content from day one fixes all three — and graduates cleanly to a CMS without a rewrite.

See `SPEC.md` §5 for the full architectural specification.

---

## Brand & Design System

Salone Explorer ships under **FambulTik**, TpGroup's heritage-and-diaspora brand. *Fambul Tik* is Krio for *family stick* — a symbol of diaspora-to-homeland connection.

| Asset                   | Source                                                                                             |
| ----------------------- | -------------------------------------------------------------------------------------------------- |
| Design system           | [design.tpgroupsl.com](https://design.tpgroupsl.com/)                                              |
| Logo usage              | [design.tpgroupsl.com/foundations/logo-usage](https://design.tpgroupsl.com/foundations/logo-usage) |
| FambulTik brand home    | [design.tpgroupsl.com/templates/fambultik-home](https://design.tpgroupsl.com/templates/fambultik-home) |
| Colour tokens           | [design.tpgroupsl.com/foundations/colors](https://design.tpgroupsl.com/foundations/colors)         |
| Typography              | [design.tpgroupsl.com/foundations/typography](https://design.tpgroupsl.com/foundations/typography) |
| Accessibility foundation| [design.tpgroupsl.com/foundations/accessibility](https://design.tpgroupsl.com/foundations/accessibility) |

Design tokens are wired into Tailwind via CSS variables in `src/styles/tokens.css`. See `SPEC.md` §8.4 for the token table.

---

## Features

### Phase 1 — Public site
- Browse 8 curated Sierra Leone attractions with photos, video, ratings.
- Per-attraction detail page with description, hours, FAQ, *Get Directions*.
- FambulTik-branded UI driven by TpGroup Design System tokens.
- All copy externalised to `src/content/strings.en.json`.
- All attraction data externalised to `src/data/attractions.json`, accessed via a repository.
- Mobile-first; verified at 320 / 375 / 414 / 768 / 1024 / 1440 px.
- Pre-rendered HTML for crawlers and LLM ingestion.
- Schema.org JSON-LD entity graph; SEO, AEO, and GEO optimisation.
- Persistent demo-disclaimer alert.

### Phase 2 — Authenticated experience
- Email / password auth via Supabase.
- **Social login** — Google, Facebook, LinkedIn (Supabase OAuth).
- **Bookmarks** and **Favorites** toggles.
- **Schedule a Tour** dialog.
- **My Account** page; cancel support.
- RLS on every user-scoped table.

### Phase 2.5 — Optional database migration
Flip `VITE_ATTRACTIONS_SOURCE=supabase` to load attractions from the database instead of JSON. No UI changes required.

### Phases 9–11 — Production extensions (post-class)
Beyond the in-class build; each adds real non-functional weight (server compute, secrets, moderation, legal). Specified in `SPEC.md` §2 and §19.
- **Phase 9 — Real-time reviews.** Authenticated reviews with live updates (Supabase Realtime), moderation, and `aggregateRating` feeding the JSON-LD graph.
- **Phase 10 — Email notifications.** Transactional email for booking/review events via Supabase Edge Functions + an email provider.
- **Phase 11 — Payments (Stripe).** Tour-deposit checkout processed server-side in Edge Functions with webhook verification. Requires the §17 disclaimer revision.

### Phase 8 — Future
Migrate to Payload CMS. See [Migrating to Payload CMS](#migrating-to-payload-cms-future).

---

## Tech Stack

| Layer            | Choice                                                                |
| ---------------- | --------------------------------------------------------------------- |
| Build tool       | Vite 5                                                                |
| Framework        | React 18 + TypeScript (strict)                                        |
| Routing          | react-router-dom v6                                                   |
| Styling          | Tailwind CSS v3 + FambulTik tokens                                    |
| Components       | Radix UI primitives + `cva`, styled to TpGroup DS                     |
| Icons            | `lucide-react`                                                        |
| Document head    | `react-helmet-async`                                                  |
| Pre-rendering    | `vite-plugin-prerender`                                               |
| Data layer       | Repository pattern over JSON (P1) → Supabase (P2.5) → Payload (P8)    |
| Content layer    | `src/content/*.json` + `t()` helper                                   |
| Backend (P2)     | Supabase (Postgres + Auth + RLS)                                      |
| Client SDK       | `@supabase/supabase-js` v2                                            |
| Auth providers (P6) | Supabase Auth: email/password + Google, Facebook, LinkedIn OAuth   |
| Realtime (P9)    | Supabase Realtime (live review updates)                               |
| Server compute (P10, P11) | Supabase Edge Functions (Deno) — holds Stripe/email secrets  |
| Email (P10)      | Transactional provider (e.g. Resend) via Edge Function               |
| Payments (P11)   | Stripe (`@stripe/stripe-js` client + Stripe SDK server-side)         |
| Maps             | Google Maps deep links (no API key)                                   |
| A11y testing     | `@axe-core/playwright`, `eslint-plugin-jsx-a11y`, Lighthouse          |
| Hosting          | Vercel                                                                |
| CI / SAST        | GitHub Actions — CodeQL, Semgrep, `npm audit`, axe-core               |
| Dep updates      | Dependabot                                                            |

---

## Getting Started

### Prerequisites
- Node.js **20+**
- npm 10+
- Access to `tamba-lamin-tpgroup/ai-led-sdlc-demo`
- _(Phase 2)_ A Supabase project + a Vercel account

### Clone & install

```bash
git clone git@github.com:tamba-lamin-tpgroup/ai-led-sdlc-demo.git
cd ai-led-sdlc-demo
```

The Vite app is scaffolded into the `salone-explorer/` subdirectory during
Phase 1 (see `SPEC.md` §19); until then that directory does not exist. Once
it has been scaffolded, install from inside it:

```bash
cd salone-explorer
npm install
```

All commands in the steps below run from the `salone-explorer/` app
directory (see [Project structure](#project-structure)); the repo root
holds only the spec, docs, and the `.claude/` harness.

### Configure environment

```bash
cp .env.example .env.local
```

### Run locally

```bash
npm run dev
# → http://localhost:5173
```

### Production build

```bash
npm run build      # type-check + bundle + pre-render + sitemap
npm run preview
```

---

## Environment Variables

Vite only exposes variables prefixed with `VITE_` to client code.

| Variable                    | Required for       | Description                                                       |
| --------------------------- | ------------------ | ----------------------------------------------------------------- |
| `VITE_SITE_URL`             | Both phases        | Absolute base URL for canonicals, sitemap, JSON-LD `@id`.         |
| `VITE_ATTRACTIONS_SOURCE`   | Both phases        | `file` (default) or `supabase`. Picks the active repository.      |
| `VITE_SUPABASE_URL`         | Phase 2            | Supabase project URL.                                             |
| `VITE_SUPABASE_ANON_KEY`    | Phase 2            | Supabase anon (public) key.                                       |
| `VITE_STRIPE_PUBLISHABLE_KEY` | Phase 11         | Stripe publishable (client) key.                                  |

**Server-side secrets are never `VITE_`-exposed.** Social-login OAuth client IDs/secrets (Google, Facebook, LinkedIn) are configured in the Supabase dashboard. Stripe and email secrets live as Supabase Edge Function secrets: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` (Phase 11), `EMAIL_PROVIDER_API_KEY` (Phase 10).

`.env.example`:

```env
# Production custom domain. Vercel preview deploys use their *.vercel.app URL.
VITE_SITE_URL=https://slint-ai-sldc-demo.tpgroupsl.com
VITE_ATTRACTIONS_SOURCE=file
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=
# Phase 11 (client publishable key only):
VITE_STRIPE_PUBLISHABLE_KEY=
```

---

## Project Structure

The shippable app and the AI-led SDLC tooling live in **separate trees**. The repo root holds the spec, docs, CI config, and the `.claude/` harness; the app is scaffolded into `salone-explorer/`. **Vercel's Root Directory is `salone-explorer`**, so the deployment is built only from that folder and never contains the harness or docs (see [ADR 0001](docs/adr/0001-app-subdirectory-separation.md)).

```
ai-led-sdlc-demo/                # repo root — NOT deployed
├── .github/
│   ├── workflows/{ci,codeql,security,a11y}.yml   # run working-directory: salone-explorer
│   └── dependabot.yml
├── .claude/                     # AI-led SDLC harness
├── docs/                        # documentation + adr/
├── SPEC.md  README.md
└── salone-explorer/             # ── THE APP — Vercel Root Directory ──
    ├── index.html  vercel.json  vite.config.ts
    ├── tailwind.config.js  tsconfig.json  package.json
    ├── public/{robots.txt, sitemap.xml, llms.txt, favicon.svg}
    ├── scripts/{generate-sitemap.ts, migrate-attractions-to-supabase.ts}
    ├── supabase/schema.sql
    ├── tests/a11y/smoke.spec.ts
    └── src/
        ├── main.tsx  App.tsx  index.css
        ├── assets/brand/fambultik/   styles/tokens.css
        ├── data/                 # ── DATA LAYER ─────────────────
        │   ├── types.ts  attractions.json  regions.json
        ├── content/              # ── CONTENT LAYER ──────────────
        │   ├── strings.en.json  pages/{home,about}.json
        ├── lib/                  # ── CODE LAYER ─────────────────
        │   ├── supabase.ts
        │   ├── content/
        │   │   ├── attractions.ts          # interface
        │   │   ├── attractions.file.ts     # JSON impl
        │   │   ├── attractions.supabase.ts # DB impl (P2.5)
        │   │   ├── strings.ts              # t() helper
        │   │   └── index.ts                # barrel; picks impl
        │   ├── bookmarks.ts  bookings.ts
        ├── seo/                  # SeoHead, JsonLd, graph builders
        ├── auth/                 # AuthProvider, ProtectedRoute
        ├── components/           # DS-aligned UI
        └── pages/                # route components
```

---

## Data & Content Files

### `src/data/attractions.json`
Array of `Attraction` objects (type in `src/data/types.ts`). Each entry has nested arrays (`images`, `tags`, `sources`, `faqs`) — JSON is used (not CSV) because of the nesting. The file is the only place attraction facts live. Components reach it through `attractions.getAll()` / `attractions.getById(id)`, never via direct import.

### `src/data/regions.json`
Flat lookup of Sierra Leone districts to provinces. Drives the region badge.

### `src/content/strings.en.json`
Flat key→string map of every user-facing string in the app. Keys use dot notation (`nav.home`, `home.hero.cta`, `disclaimer.full`). Components call `t("namespace.key")`. Adding a string means adding a key — no exceptions.

### `src/content/pages/{home,about}.json`
Longer-form copy (multiple paragraphs) for individual pages, kept out of the flat strings file for readability.

### How to edit content
- New button label → add a key to `strings.en.json`, reference it via `t()`.
- New attraction → add an entry to `attractions.json`, cite a §4 source.
- New paragraph on About → add to `content/pages/about.json`.
- Never edit a `.tsx` file just to change a word.

### Switching to the database (Phase 2.5)
Run `npm run migrate:attractions` to upsert every record from JSON into the Supabase `public.attractions` table. Then set `VITE_ATTRACTIONS_SOURCE=supabase` in Vercel and redeploy. The UI does not change.

---

## Data Sources

All attraction content is paraphrased from these authoritative sources. Each entry's `sources[]` cites at least one.

- [Sierra Leone National Tourist Board](https://ntb.gov.sl/)
- [Sierra Leone Tourism (Official)](https://tourismsierraleone.com/)
- [Visit Sierra Leone (VSL Travel)](https://www.visitsierraleone.org/)
- [Sierra Leone Heritage — National Museum](https://www.sierraleoneheritage.org/museum)
- [sierra-leone.org](https://sierra-leone.org/)

**Sourcing rules.** Paraphrase. No more than one short sentence verbatim. If a fact is not confirmed, `hours.notes: "Hours vary — confirm locally"`. Images from Wikimedia Commons or official-site public media; Unsplash with attribution otherwise.

---

## Accessibility — WCAG 2.2 AA

The TpGroup Design System is WCAG 2.2 AA — using its tokens and components is the cheapest path to conformance. Application code is verified independently:

- `eslint-plugin-jsx-a11y` (`recommended`) — violations fail `npm run lint`.
- `@axe-core/playwright` smoke tests on five routes — fail on serious or critical.
- Lighthouse Accessibility ≥ 95 on Home and Detail.
- One keyboard-only and one screen-reader pass (VoiceOver / NVDA) before each release.

Highlights: 4.5 : 1 contrast, single-column reflow at 320 CSS px, ≥ 3 : 1 non-text contrast, focus visible + ≥ 3 : 1 focus appearance ring (new in 2.2), focus not obscured (new in 2.2), 44 × 44 px targets (exceeds new 2.5.8 minimum), dragging alternatives (new in 2.2), consistent help (new in 2.2), redundant entry (new in 2.2), accessible authentication (new in 2.2).

Full success-criterion-by-success-criterion checklist in `SPEC.md` §10.

---

## SEO, AEO & GEO

**SEO.** Semantic HTML5; one `<h1>` per page; per-page `<title>` ≤ 60, description ≤ 160; OG + Twitter; canonical URLs; `robots.txt`; build-time `sitemap.xml` generated from the active attractions repository; pre-rendered HTML.

**AEO (Answer Engine Optimization).** Optimised for answer engines and assistants (Google AI Overviews, Perplexity, ChatGPT, Copilot, voice): question-shaped headings with extractable first-sentence answers, `SpeakableSpecification` JSON-LD over each attraction's lead and key facts, self-contained `FAQPage` answers, and citable fact blocks high on detail pages. Builds on GEO + JSON-LD with no new client dependency. See `SPEC.md` §13.3.

**GEO.** Definitional lead sentences in `longDescription`; inline source attributions; per-attraction FAQ → `FAQPage` JSON-LD; `llms.txt` generated from the repository; visible "Last reviewed" date → `dateModified`.

---

## Structured Data (JSON-LD)

Each page emits a Schema.org `@graph`:

- `Organization` — TpGroup (SL) Limited.
- `TouristInformationCenter` — FambulTik / Salone Explorer.
- `WebSite`, `WebPage`, `BreadcrumbList` per route.
- `TouristAttraction` per attraction with `address`, `geo`, `aggregateRating`, `openingHoursSpecification`, `image`, `video`, `containedInPlace`.
- `FAQPage` per attraction.
- `Review` per published review (Phase 9), aggregated into `aggregateRating`.
- `SpeakableSpecification` on the attraction lead + key facts (AEO).

Validate at [validator.schema.org](https://validator.schema.org/) and Google's [Rich Results Test](https://search.google.com/test/rich-results).

---

## Mobile & Responsive Standards

| Breakpoint | Min width | Layout                              |
| ---------- | --------- | ----------------------------------- |
| (base)     | 0         | Single column.                      |
| `sm`       | 640 px    | Two-column grids start.             |
| `md`       | 768 px    | Tablet nav, larger gutters.         |
| `lg`       | 1024 px   | Three-column attraction grid.       |
| `xl`       | 1280 px   | Capped max-width container.         |

Touch targets ≥ 44 × 44 px. Body 16 px, line-height 1.5. Verified at 320 / 375 / 414 / 768 / 1024 / 1440 px.

---

## Security & SAST

Merges to `main` require all four workflows green:

| Workflow      | Tools                                                                  |
| ------------- | ---------------------------------------------------------------------- |
| `ci.yml`      | `npm ci`, ESLint (incl. `jsx-a11y`), `tsc --noEmit`, `npm run build`   |
| `codeql.yml`  | GitHub CodeQL (`security-and-quality`)                                 |
| `security.yml`| Semgrep (OWASP, JS, TS, React, secrets) + `npm audit --audit-level=high` |
| `a11y.yml`    | `@axe-core/playwright` on five routes                                  |

App-level: no secrets in client code; RLS on every user-scoped table; `rel="noopener noreferrer"` on outbound links; security headers in `vercel.json`. For the production extensions: OAuth redirect URLs allow-listed in Supabase (no open redirect, P6); review bodies sanitised, length-bounded, rate-limited, and moderation-gated (P9); Stripe and email secrets held only as Edge Function secrets (P10/P11); Stripe webhooks signature-verified before any DB write, with payment status written only by the Edge Function service role (P11).

---

## Supabase Backend (Phase 2)

1. Provision Supabase via the Vercel integration or directly at supabase.com.
2. Copy URL + anon key into Vercel env vars (with `VITE_` prefix) and `.env.local`.
3. Run `supabase/schema.sql` in the SQL Editor.
4. Auth → Email enabled ("Confirm email" disabled for the class); enable the Google, Facebook, and LinkedIn OAuth providers (Phase 6) with their client IDs/secrets and allow-listed redirect URLs.

Tables: `profiles`, `saved_attractions` (bookmarks + favorites via `kind` enum), `tour_bookings`. RLS on all three, scoped `auth.uid() = user_id`. The production extensions add `reviews` (Phase 9) and `payments` (Phase 11), each with RLS — see the draft schema in `SPEC.md` §6.6.

### Phase 2.5 — Migrate attractions to Supabase (optional)

```sql
create table public.attractions ( ... );  -- see SPEC.md §5.3
create policy "public read attractions" on public.attractions for select using (true);
```

```bash
npm run migrate:attractions    # JSON → public.attractions
```

Set `VITE_ATTRACTIONS_SOURCE=supabase` on Vercel; redeploy. UI is unchanged.

---

## Migrating to Payload CMS (Future)

The endpoint architecture is **Payload CMS** managing all content. The repository pattern means this migration is a service swap, not a rewrite.

| Today                                | Phase 8                                                            |
| ------------------------------------ | ------------------------------------------------------------------ |
| `src/data/attractions.json`          | Payload `attractions` collection                                   |
| `src/content/strings.en.json`        | Payload `strings` collection (key/value, localised)                |
| `src/content/pages/*.json`           | Payload `pages` collection with rich-text blocks                   |
| Disclaimer hard-coded in strings.json| Payload `siteSettings` global                                      |
| `fileAttractionRepository`           | `payloadAttractionRepository` (fetches REST/GraphQL)               |
| `t(key)` reads JSON                  | `t(key)` reads Payload-driven strings via React Query              |

Supabase remains in the architecture for user-generated data (bookmarks, bookings, profiles). Payload owns *editorial* data. This is the production-grade split: CMS for content editors, database for transactional records.

See `SPEC.md` §5.4 for the architectural sketch.

---

## Deployment

### Vercel
Project: [`slint-ai-led-sdlc-s-projects/slint-ai-led-sdlc-demo`](https://vercel.com/slint-ai-led-sdlc-s-projects/slint-ai-led-sdlc-demo). Use the existing project — do not create a new one.
1. Connect the repo to the existing project. **Root Directory: `salone-explorer`** (excludes `.claude/` and `docs/` from the build). Framework Preset: **Vite**. Build Command: `npm run build`. Output Directory: `dist`.
2. Set env vars: `VITE_SITE_URL=https://slint-ai-sldc-demo.tpgroupsl.com`, `VITE_ATTRACTIONS_SOURCE=file`, and (Phase 2) `VITE_SUPABASE_*`.
3. Map the `slint-ai-sldc-demo.tpgroupsl.com` domain. Deploy. Auto-deploys on every push to `main`.

### Post-deploy verification
- `/robots.txt`, `/sitemap.xml`, `/llms.txt` resolve.
- Lighthouse (mobile): A11y ≥ 95, SEO ≥ 90, BP ≥ 90, Perf ≥ 80.
- Schema.org Validator passes on a detail URL.
- View-source on a detail page shows long description text in HTML (pre-rendering worked).
- Keyboard-only walkthrough completes without trapped focus.

---

## Scripts

| Script                      | Purpose                                                  |
| --------------------------- | -------------------------------------------------------- |
| `npm run dev`               | Vite dev server.                                         |
| `npm run build`             | Type-check, bundle, generate sitemap, pre-render routes. |
| `npm run preview`           | Serve `dist/`.                                           |
| `npm run lint`              | ESLint (incl. `jsx-a11y`).                               |
| `npm run typecheck`         | `tsc --noEmit`.                                          |
| `npm run test:a11y`         | Playwright + axe-core locally.                           |
| `npm run migrate:attractions` | Upsert JSON attractions into Supabase (Phase 2.5).     |

---

## Acceptance Criteria

### Phase 1
- [ ] `npm run build`, `tsc --noEmit`, ESLint clean.
- [ ] **No English literals in any `.tsx`/`.ts` source file outside `src/data/`, `src/content/`, or tests.** Verified by grep.
- [ ] **No attraction facts outside `src/data/attractions.json` and its repository module.**
- [ ] Home renders the attractions returned by `attractions.getAll()`.
- [ ] FambulTik logo present in NavBar and footer; tokens applied.
- [ ] Disclaimer alert on Home; full disclaimer in footer and `/about`.
- [ ] Usable at 320 / 375 / 414 / 768 / 1024 / 1440 px; touch targets ≥ 44 × 44 px.
- [ ] axe-core CI reports zero serious/critical violations on five routes.
- [ ] Lighthouse: A11y ≥ 95, SEO ≥ 90, BP ≥ 90, Perf ≥ 80.
- [ ] JSON-LD validates with zero errors.
- [ ] `/robots.txt`, `/sitemap.xml`, `/llms.txt` resolve.
- [ ] CI, CodeQL, Security, A11y workflows green on `main`.

### Phase 2
- [ ] Sign-up, sign-in, sign-out work.
- [ ] Bookmark / Favorite persist across reloads.
- [ ] Scheduling creates a row visible on `/account`.
- [ ] Cancelling sets `status='cancelled'`.
- [ ] `/account` redirects to `/signin` while signed out.
- [ ] RLS verified across two accounts.
- [ ] WCAG 2.2 AA still met.

### Phase 2.5 (optional)
- [ ] `VITE_ATTRACTIONS_SOURCE=supabase` produces identical pages.
- [ ] No component diff between modes.

### Phases 6, 9–11 (production extensions)
- [ ] Phase 6: Google, Facebook, LinkedIn sign-in each complete and create a `profiles` row; no provider secret in the client bundle.
- [ ] Phase 9: one review per user per attraction, list updates live, only published reviews are public (RLS verified), `aggregateRating` reflects them.
- [ ] Phase 10: booking create/cancel triggers an email; provider key only an Edge Function secret.
- [ ] Phase 11: deposit checkout succeeds in Stripe test mode, booking marked paid only via verified webhook, no Stripe secret in the client, disclaimer revised before live mode.

Full criteria in `SPEC.md` §20.

---

## Roadmap

- Tag-filter chips on Home (driven by content).
- Client-side search.
- Dark mode (still 2.2 AA in dark).
- Editable `display_name` in profile.
- Auto-confirm bookings after 24 h via Supabase Edge Function.
- **Krio locale** (`strings.kri.json`) — proves the i18n on-ramp.
- **Phase 8: Payload CMS** — all content + strings managed in the CMS admin UI.

---

## Contributing

This repo is a teaching artefact. External contributions are not expected, but the workflow is standard:

1. Branch from `dev` (see [`.claude/rules/branch-conventions.md`](./.claude/rules/branch-conventions.md)); `main` is promotion-only.
2. From `salone-explorer/`, run `npm run lint`, `npm run typecheck`, `npm run build`, `npm run test:a11y`.
3. **Do not add English strings to `.tsx`/`.ts` files** — add to `src/content/strings.en.json`.
4. **Do not add attraction facts to `.tsx`/`.ts` files** — add to `src/data/attractions.json`.
5. Open a PR — CI, CodeQL, Security, A11y must pass before merge.

For students: follow the phased delivery workflow in [`SPEC.md`](./SPEC.md). Commit at the end of each phase.

---

## License & Credits

**Publisher.** TpGroup (SL) Limited.
**Brand.** FambulTik.
**Design.** Based on the [TpGroup Design System](https://design.tpgroupsl.com/) (v1.0.0).
**Code.** © TpGroup (SL) Limited. Released for educational use. Not for commercial deployment without permission.
**Content.** Paraphrased from the sources listed under [Data Sources](#data-sources).
**Built with [Claude Code](https://docs.claude.com/claude-code).**

---

*For the full product specification — three-layer architecture, repository pattern, brand & visual identity, accessibility conformance, data model, schema, JSON-LD graph, phase-by-phase build workflow, acceptance criteria, Payload CMS migration plan — see [`SPEC.md`](./SPEC.md).*
