# Sierra Leone Tour Guide — Project Specification

> **Publisher:** TpGroup (SL) Limited
> **Brand:** **FambulTik** — TpGroup's heritage-and-diaspora subsidiary
> **Repository:** `git@github.com:click2tman/ai-led-sdlc-demo.git`
> **Design system:** [TpGroup Design System](https://design.tpgroupsl.com/) (multi-brand, WCAG 2.2 AA)
> **Disclaimer:** *This application is built for demonstration and educational purposes only. It is not an official tourism service. Information is curated from public sources and may be out of date — confirm details with the operator before travelling.*

> **Purpose:** Build a deployable Sierra Leone tour-guide web app using Claude Code. Phase 1 (~45 min) ships a static, public-facing site. Phase 2 (~45–60 min) adds Supabase-backed auth, bookmarks, favorites, account view, and tour scheduling. Phase 8 (future) replaces file-based content with **Payload CMS**. Throughout, the app conforms to the TpGroup Design System under the **FambulTik** brand, meets **WCAG 2.2 Level AA**, is fully responsive, SEO- and GEO-optimised, structured-data-rich, and protected by SAST in CI. This spec is the single source of truth — read it fully before generating any code.

---

## 1. Project Overview

**Product name:** Salone Explorer
**Tagline:** Discover Sierra Leone, one attraction at a time.
**Publisher:** TpGroup (SL) Limited.
**Brand:** FambulTik. *"Fambul Tik"* is Krio for *"family stick"* — TpGroup's symbol of diaspora-to-homeland connection.
**Type:** Single-page web application. Phase 1 is fully static; Phase 2 adds a Supabase backend.
**Audience:** Sierra Leonean diaspora, domestic visitors, generative-AI assistants surfacing Sierra Leone tourism information.

**Primary user goals**

1. Browse a curated list of tourist attractions.
2. View rich detail (description, photos, video, hours, ratings) per attraction.
3. Get directions in one tap.
4. **(Phase 2)** Sign in, bookmark, mark favorites, schedule a tour, review activity in *My Account*.

---

## 2. Scope

### Phase 1 — Static foundation (in-class, ~45 min)
- Home and Attraction Detail views.
- **Attractions loaded from `src/data/attractions.json`** via a repository abstraction (§5).
- **All UI strings loaded from `src/content/strings.en.json`**.
- FambulTik branded UI; TpGroup Design System tokens.
- WCAG 2.2 Level AA conformance.
- SEO, GEO, JSON-LD, SAST.
- Public GitHub repo + Vercel deploy.

### Phase 2 — Authenticated features (~45–60 min)
- Supabase email/password auth.
- Bookmarks, favorites, scheduled tours.
- *My Account* page.
- RLS on every user-scoped table.
- **Optional (Phase 2.5):** migrate attractions from JSON to `public.attractions` Supabase table — demonstrates the repository swap.

### Phase 8 — Future: Payload CMS (out of scope for class)
- Replace JSON files and the strings module with a Payload CMS-backed repository.
- Editorial team manages attractions, strings, labels, page copy, disclaimer, FAQ entries through the Payload admin UI.
- Salone Explorer becomes a pure presentation layer; CMS owns all content.

### Out of scope (all phases)
- Payment or real bookings.
- Real-time reviews or social comments.
- Email or SMS notifications.

---

## 3. Tech Stack

| Layer            | Choice                                  | Rationale                                          |
| ---------------- | --------------------------------------- | -------------------------------------------------- |
| Build tool       | **Vite 5**                              | Sub-second dev server, minimal config.             |
| Framework        | **React 18**                            | Ubiquitous, well-known to Claude Code.             |
| Language         | **TypeScript** (strict)                 | Type safety; pairs well with AI-generated code.    |
| Routing          | **react-router-dom v6**                 | Declarative client-side routing.                   |
| Styling          | **Tailwind CSS v3** + FambulTik tokens  | Utility-first, fastest for AI-led builds.          |
| Components       | Radix UI primitives + `cva`, styled to TpGroup DS | Accessible primitives + brand styling.   |
| Icons            | `lucide-react`                          | Matches DS iconography guidance.                   |
| Document head    | **react-helmet-async**                  | Per-route `<title>`, meta, JSON-LD.                |
| **Data layer**   | **Repository pattern** (§5) over JSON files (P1), Supabase (P2 optional), Payload CMS (P8). | Swap stores without touching UI code. |
| **Content layer**| `src/content/*.json` strings module     | All copy externalised; CMS-ready.                  |
| **Backend (P2)** | **Supabase** (Postgres + Auth + RLS)    | Provisioned via Vercel ↔ Supabase integration.     |
| **Client SDK**   | `@supabase/supabase-js` v2              | Official client; works in browser.                 |
| Maps             | Google Maps deep links                  | No API key required.                               |
| Pre-render       | **vite-plugin-prerender**               | Static HTML for crawlers and LLM ingestion.        |
| SEO              | sitemap.xml, robots.txt, canonical URLs | Crawlable.                                         |
| GEO              | llms.txt, semantic content patterns     | Visibility in generative AI answers.               |
| Structured data  | Schema.org JSON-LD (`@graph`)           | Entity relationships across pages.                 |
| Deployment       | **Vercel** (framework preset = Vite)    | One-click deploy on push.                          |
| Version control  | **GitHub** (`click2tman/ai-led-sdlc-demo`) | Required for Vercel auto-deploy and CI.         |
| CI / SAST        | GitHub Actions — CodeQL, Semgrep, npm audit, axe-core | Static security + a11y checks.       |
| Dep updates      | Dependabot                              | Weekly supply-chain refresh.                       |

---

## 4. Data Sources (attraction content)

All attraction copy, hours, and imagery references must be derived from these authoritative sources. Cite them in `attractions.json` (`sources[]`), in the README, and in the on-page Sources block.

| Source                                                                                       | What to pull from it                                                |
| -------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| [Sierra Leone National Tourist Board](https://ntb.gov.sl/)                                   | Official designations, regulated attractions, opening hours.        |
| [Sierra Leone Tourism (Official)](https://tourismsierraleone.com/)                           | Curated "Top Things to Do" and "Where to Go" copy.                  |
| [Visit Sierra Leone (VSL Travel)](https://www.visitsierraleone.org/)                         | Tour-operator details, practical visitor info, regional routing.    |
| [Sierra Leone Heritage — National Museum](https://www.sierraleoneheritage.org/museum)        | Museum collections, artefact descriptions, cultural context.        |
| [sierra-leone.org](https://sierra-leone.org/)                                                | Country background, geography, supplementary context.               |

**Sourcing rules**

- Paraphrase — never copy more than one short sentence verbatim.
- Every attraction's `sources` field must list ≥ 1 URL from the table.
- If a fact is not confirmed, set `hours.notes: "Hours vary — confirm locally"`.
- Images: prefer Wikimedia Commons or official-site public media; Unsplash with attribution otherwise.

---

## 5. Content & Data Architecture

Salone Explorer enforces a strict **three-layer separation** between code, data, and content. This is the most important architectural rule in the project. Students must follow it; Claude Code is instructed in §22 never to violate it.

### 5.1 The three layers

| Layer       | Lives in            | Examples                                                       | Eventual home                                |
| ----------- | ------------------- | -------------------------------------------------------------- | -------------------------------------------- |
| **Code**    | `src/components/`, `src/pages/`, `src/lib/` | React components, route handlers, business logic. | Source repo (always).                        |
| **Data**    | `src/data/*.json`   | Attractions, regions, taxonomies, reference lists.             | Phase 2 (opt): Supabase table. Phase 8: Payload CMS collection. |
| **Content** | `src/content/*.json`| UI strings, button labels, page copy, microcopy, disclaimer.   | Phase 8: Payload CMS globals & collections.  |

**Rule:** no component, page, or library file may contain a user-facing string, an attraction fact, or a data fixture. If you find yourself typing `"Schedule a Tour"` or `"Tiwai Island"` inside a `.tsx` file, stop — the string belongs in `src/content/`, the fact belongs in `src/data/`.

### 5.2 Phase 1 — File-based (in-class)

#### 5.2.1 Domain data

`src/data/attractions.json` is an **array of `Attraction` objects**, conforming to the type in §6. JSON is used (not CSV) because the records contain nested arrays (`images[]`, `tags[]`, `sources[]`, `faqs[]`) and CSV cannot represent them cleanly. For flat reference data (e.g. `src/data/regions.json` mapping districts to provinces) CSV would be acceptable, but the project standardises on JSON for consistency.

#### 5.2.2 UI strings

`src/content/strings.en.json` is a **flat key→string map**. Keys use dot notation: `nav.home`, `home.hero.cta`, `disclaimer.full`, `schedule.modal.title`, etc. Strings never include HTML; rich text is composed in components from multiple keys.

#### 5.2.3 Loader and repository

A repository interface lives in `src/lib/content/attractions.ts`:

```ts
// src/lib/content/attractions.ts
import type { Attraction } from "@/data/types";

export interface AttractionRepository {
  getAll(): Promise<Attraction[]>;
  getById(id: string): Promise<Attraction | null>;
}
```

Phase 1 implementation reads from JSON:

```ts
// src/lib/content/attractions.file.ts
import attractionsData from "@/data/attractions.json";
import type { AttractionRepository } from "./attractions";

export const fileAttractionRepository: AttractionRepository = {
  async getAll() {
    return attractionsData as Attraction[];
  },
  async getById(id) {
    return (attractionsData as Attraction[]).find(a => a.id === id) ?? null;
  },
};
```

A barrel module selects the active implementation by environment variable:

```ts
// src/lib/content/index.ts
import { fileAttractionRepository } from "./attractions.file";
import { supabaseAttractionRepository } from "./attractions.supabase";

const source = import.meta.env.VITE_ATTRACTIONS_SOURCE ?? "file";

export const attractions =
  source === "supabase" ? supabaseAttractionRepository : fileAttractionRepository;
```

Pages and components import only from the barrel; they never know which backend serves the data:

```ts
// src/pages/HomePage.tsx
import { attractions } from "@/lib/content";

const list = await attractions.getAll();
```

Strings use the same indirection:

```ts
// src/lib/content/strings.ts
import en from "@/content/strings.en.json";

type Key = keyof typeof en;
export const t = (key: Key, fallback?: string): string =>
  en[key] ?? fallback ?? key;
```

Components call `t("nav.home")`, never write the literal.

### 5.3 Phase 2 — Database (Supabase, optional migration)

Phase 2 adds user-scoped tables (profiles, saved_attractions, tour_bookings — §6.3). Attractions remain in JSON unless students elect to migrate them as a Phase 2.5 stretch.

When migrating, a `public.attractions` table is added with public-read RLS:

```sql
create table public.attractions (
  id              text primary key,
  name            text not null,
  short_description text not null,
  long_description text not null,
  region          text not null,
  latitude        numeric not null,
  longitude       numeric not null,
  hours_open      time,
  hours_close     time,
  hours_days      text,
  hours_notes     text,
  rating          numeric,
  review_count    int,
  images          text[],
  video_url       text,
  tags            text[],
  sources         text[],
  faqs            jsonb,
  updated_at      timestamptz not null default now()
);

alter table public.attractions enable row level security;
create policy "public read attractions"
  on public.attractions for select
  using (true);
```

A migration script `scripts/migrate-attractions-to-supabase.ts` reads `src/data/attractions.json` and `upsert`s every row. Then `VITE_ATTRACTIONS_SOURCE=supabase` flips the active implementation — no UI code changes.

The Supabase repository:

```ts
// src/lib/content/attractions.supabase.ts
import { supabase } from "@/lib/supabase";
import type { AttractionRepository } from "./attractions";

export const supabaseAttractionRepository: AttractionRepository = {
  async getAll() {
    const { data, error } = await supabase
      .from("attractions")
      .select("*")
      .order("name");
    if (error) throw error;
    return data.map(toAttraction);
  },
  async getById(id) {
    const { data, error } = await supabase
      .from("attractions")
      .select("*")
      .eq("id", id)
      .maybeSingle();
    if (error) throw error;
    return data ? toAttraction(data) : null;
  },
};

function toAttraction(row: any): Attraction { /* shape the row */ }
```

### 5.4 Phase 8 — Payload CMS (future)

A future iteration replaces both JSON files and the strings module with **Payload CMS** — a self-hosted, TypeScript-first headless CMS. The architectural sketch:

- **Payload service** runs alongside (e.g. on Vercel as a Node API, on Render, or on Fly) with its own Postgres database.
- **Collections defined in Payload:**
  - `attractions` (mirrors the `Attraction` type).
  - `pages` (Home hero, About body, etc.).
  - `strings` (key → value, localised).
  - `faqs` (joined to attractions).
  - `media` (image library with alt-text metadata).
- **Globals:** `disclaimer`, `siteSettings`, `navigation`.
- **API consumption:** the Salone Explorer build fetches from Payload's REST or GraphQL endpoint at build time (for pre-rendered pages) and at runtime (for personalised data). A `payloadAttractionRepository` replaces the file/supabase ones.
- **Editorial roles:** Payload provides RBAC (role-based access control). Content editors manage all strings and attractions in the Payload admin UI; developers ship UI code only.
- **Supabase remains** for *user-generated* data (bookmarks, bookings, profiles). Payload owns *editorial* data. This is the production-grade split.

Phase 8 is **not** delivered in class. It is documented here so students understand the architectural endpoint and so the repository pattern they build in Phase 1 is recognised as the bridge to it.

### 5.5 Why this matters (the teaching point)

Hard-coding strings and data into components produces three failure modes that every senior engineer has seen:

1. **Editorial bottleneck.** Changing a button label requires a developer, a PR, and a deploy.
2. **i18n is impossible** without a six-month rewrite.
3. **Content drift.** The same product term ends up written three different ways in three components.

The repository pattern + externalised content fixes all three on day one — and graduates cleanly to a CMS when the team is ready.

---

## 6. Data Model

### 6.1 `Attraction` type (shared across all repositories)

```ts
// src/data/types.ts
export type Attraction = {
  id: string;                  // kebab-case slug
  name: string;
  shortDescription: string;    // < 140 chars
  longDescription: string;     // 2–4 paragraphs of plain text
  location: { region: string; latitude: number; longitude: number };
  hours: { open: string; close: string; daysOpen: string; notes?: string };
  rating: number;              // 0.0–5.0
  reviewCount: number;
  images: string[];
  videoUrl?: string;
  tags: string[];
  sources: string[];           // URLs from §4
  faqs?: { question: string; answer: string }[];
  lastReviewed?: string;       // ISO date — drives JSON-LD dateModified
};
```

### 6.2 Seed dataset (8 attractions, populated in `src/data/attractions.json`)

| # | Attraction                              | Region                                            | Suggested tags                       |
| - | --------------------------------------- | ------------------------------------------------- | ------------------------------------ |
| 1 | Tiwai Island Wildlife Sanctuary         | Pujehun District, Southern Province               | wildlife, ecotourism, island         |
| 2 | River No. 2 Beach                       | Western Area Peninsula                            | beach, swimming, family              |
| 3 | Bunce Island                            | Sierra Leone River estuary                        | history, heritage, slave-trade       |
| 4 | Tacugama Chimpanzee Sanctuary           | Western Area Peninsula National Park              | wildlife, conservation, primates     |
| 5 | Sierra Leone National Museum            | Freetown, Central                                 | history, culture, museum             |
| 6 | Banana Islands                          | Off the Freetown Peninsula                        | island, snorkeling, history          |
| 7 | Outamba-Kilimi National Park            | Bombali / Karene District, Northern Province      | safari, hippos, elephants            |
| 8 | Mount Bintumani (Loma Mountains)        | Koinadugu District, Northern Province             | hiking, mountain, biodiversity       |

### 6.3 Supabase schema (Phase 2 — user-scoped tables)

```sql
create table public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  display_name text,
  created_at timestamptz not null default now()
);

create type saved_kind as enum ('bookmark', 'favorite');

create table public.saved_attractions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  attraction_id text not null,
  kind saved_kind not null,
  created_at timestamptz not null default now(),
  unique (user_id, attraction_id, kind)
);
create index on public.saved_attractions (user_id, kind);

create type booking_status as enum ('pending', 'confirmed', 'cancelled');

create table public.tour_bookings (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  attraction_id text not null,
  tour_date date not null,
  party_size int not null check (party_size between 1 and 20),
  notes text,
  status booking_status not null default 'pending',
  created_at timestamptz not null default now()
);
create index on public.tour_bookings (user_id, tour_date);

alter table public.profiles            enable row level security;
alter table public.saved_attractions   enable row level security;
alter table public.tour_bookings       enable row level security;

create policy "own profile read"   on public.profiles for select using (auth.uid() = id);
create policy "own profile insert" on public.profiles for insert with check (auth.uid() = id);
create policy "own profile update" on public.profiles for update using (auth.uid() = id);

create policy "own saved read"     on public.saved_attractions for select using (auth.uid() = user_id);
create policy "own saved insert"   on public.saved_attractions for insert with check (auth.uid() = user_id);
create policy "own saved delete"   on public.saved_attractions for delete using (auth.uid() = user_id);

create policy "own bookings read"  on public.tour_bookings for select using (auth.uid() = user_id);
create policy "own bookings ins"   on public.tour_bookings for insert with check (auth.uid() = user_id);
create policy "own bookings upd"   on public.tour_bookings for update using (auth.uid() = user_id);
create policy "own bookings del"   on public.tour_bookings for delete using (auth.uid() = user_id);

create or replace function public.handle_new_user() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (id) values (new.id);
  return new;
end; $$;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();
```

### 6.4 UI strings catalogue (`src/content/strings.en.json`)

The strings file is a flat object. Required key namespaces:

- `app.*` — product name, tagline.
- `nav.*` — nav labels.
- `home.*` — hero, section headings, empty states.
- `attraction.*` — labels on the detail page (e.g. `attraction.openingHours`, `attraction.directions.cta`).
- `schedule.*` — modal labels and validation messages.
- `auth.*` — sign-in / sign-up form labels, errors.
- `account.*` — account page section titles, empty states.
- `footer.*` — footer columns and links.
- `disclaimer.*` — short and full disclaimer copy.
- `errors.*` — generic error messages.

Adding a new key is a documented PR step: update `strings.en.json` and use `t("namespace.key")` in the component. Translation to additional locales (e.g. `strings.kri.json` for Krio) is the i18n on-ramp.

### 6.5 Reference data (`src/data/regions.json`)

A small lookup file mapping Sierra Leone districts to provinces — used to render the region badge consistently and to validate `location.region`. Example shape:

```json
[
  { "district": "Pujehun", "province": "Southern" },
  { "district": "Koinadugu", "province": "Northern" }
]
```

---

## 7. Pages & Routes

| Route                    | Auth     | Purpose                                                   |
| ------------------------ | -------- | --------------------------------------------------------- |
| `/`                      | Public   | Home — hero + attraction grid.                            |
| `/attractions/:id`       | Public   | Detail page (modelled on DS Tour-detail / Place-detail).  |
| `/signin`                | Public   | Email/password sign-in.                                   |
| `/signup`                | Public   | Email/password sign-up.                                   |
| `/account`               | **Auth** | My Account — bookmarks, favorites, scheduled tours.       |
| `/about`                 | Public   | FambulTik / TpGroup attribution, disclaimer, credits.     |
| `*`                      | Public   | 404.                                                      |

---

## 8. Brand & Visual Identity (FambulTik)

### 8.1 What FambulTik is
FambulTik is TpGroup's heritage-and-diaspora brand. Its mission, per the [FambulTik home template](https://design.tpgroupsl.com/templates/fambultik-home), is to help diaspora members reconnect with their roots through homecoming, genealogy, and cultural education. Salone Explorer extends that mission by surfacing the attractions a diaspora visitor (or any traveller) might want to see.

### 8.2 Brand voice
- **Warm, welcoming, rooted.** Address the reader as someone returning home.
- **Authoritative but humble.** Cite sources; defer to local operators on practicalities.
- **Plain English with Krio framing where appropriate.** Use proper place-names.
- **Prose, not slogans.**

All voice decisions live in `strings.en.json`, not in components.

### 8.3 Logo usage
- Primary: FambulTik wordmark. Placed top-left of `NavBar`. Light-on-dark variant for the hero; dark-on-light variant elsewhere. Source from the [TpGroup DS Logo Usage page](https://design.tpgroupsl.com/foundations/logo-usage).
- Clear space ≥ the height of the `T` glyph.
- Minimum 24 px tall on mobile, 32 px on desktop.
- Footer carries the parent TpGroup wordmark + *"A TpGroup company."*
- Never stretch, recolour, rotate, or place over busy imagery without an overlay.
- Brand assets in `src/assets/brand/fambultik/`.

### 8.4 Design tokens (`src/styles/tokens.css`)

Tokens trace back to the TpGroup DS foundations and are themed for FambulTik.

```css
:root {
  /* Brand — FambulTik */
  --color-brand-primary:    #C2410C;
  --color-brand-secondary:  #15803D;
  --color-brand-accent:     #0369A1;
  --color-brand-sand:       #FEF3C7;

  /* TpGroup parent endorsement */
  --color-tpgroup-primary:  #011B54;

  /* Semantic */
  --color-bg:               #FFFFFF;
  --color-surface:          #FAFAF9;
  --color-text:             #1C1917;
  --color-text-muted:       #57534E;
  --color-border:           #E7E5E4;
  --color-focus-ring:       #0369A1;
  --color-success:          #15803D;
  --color-warning:          #B45309;
  --color-danger:           #B91C1C;

  /* Typography */
  --font-sans: "Inter", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --font-display: "Lora", Georgia, serif;
  --fs-12: 0.75rem;  --fs-14: 0.875rem;  --fs-16: 1rem;
  --fs-18: 1.125rem; --fs-20: 1.25rem;   --fs-24: 1.5rem;
  --fs-30: 1.875rem; --fs-36: 2.25rem;   --fs-48: 3rem;
  --lh-tight: 1.2;   --lh-snug: 1.35;    --lh-normal: 1.5;

  /* Spacing (4-px scale) */
  --sp-1: 0.25rem;  --sp-2: 0.5rem;  --sp-3: 0.75rem;  --sp-4: 1rem;
  --sp-6: 1.5rem;   --sp-8: 2rem;    --sp-12: 3rem;    --sp-16: 4rem;

  /* Radius */
  --r-sm: 0.25rem; --r-md: 0.5rem; --r-lg: 0.75rem; --r-xl: 1rem; --r-full: 9999px;

  /* Elevation */
  --shadow-sm: 0 1px 2px rgba(0,0,0,.06);
  --shadow-md: 0 4px 8px rgba(0,0,0,.08);
  --shadow-lg: 0 12px 24px rgba(0,0,0,.10);
  --shadow-xl: 0 24px 48px rgba(0,0,0,.12);
}
```

### 8.5 Component mapping (TpGroup DS → Salone Explorer)

| DS component                                                                                       | Where used                                |
| -------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| [Button](https://design.tpgroupsl.com/components/button)                                           | Primary CTAs, *Get Directions*, *Schedule*. |
| [Card](https://design.tpgroupsl.com/components/card)                                               | Attraction grid card.                      |
| [Badge / Chips](https://design.tpgroupsl.com/components/chips-badges)                              | Tag chips, region badge.                  |
| [Accordion](https://design.tpgroupsl.com/components/accordion)                                     | Attraction FAQ block.                     |
| [Dialog](https://design.tpgroupsl.com/components/dialog)                                           | Schedule-a-Tour modal.                    |
| [Sheet](https://design.tpgroupsl.com/components/sheet)                                             | Mobile nav drawer.                        |
| [Toast](https://design.tpgroupsl.com/components/toaster)                                           | Bookmark / favorite / save toasts.        |
| [Alert](https://design.tpgroupsl.com/components/alert)                                             | Demo-disclaimer banner.                   |
| [Breadcrumb](https://design.tpgroupsl.com/components/breadcrumb)                                   | Detail-page breadcrumb.                   |
| [Form Fields](https://design.tpgroupsl.com/components/form-fields)                                 | Sign-in / sign-up / scheduling.           |
| [FAQ (Schema-aware)](https://design.tpgroupsl.com/components/faq)                                  | Drives FAQ JSON-LD.                       |
| [Header / Navbar pattern](https://design.tpgroupsl.com/patterns/header)                            | Site header.                              |
| [Footer pattern](https://design.tpgroupsl.com/patterns/footer)                                     | Site footer with disclaimer + TpGroup line. |
| [Hero pattern](https://design.tpgroupsl.com/patterns/hero)                                         | Home hero.                                |
| [Tour-detail template](https://design.tpgroupsl.com/templates/tour-detail)                         | Detail-page reference.                    |
| [Place-detail template](https://design.tpgroupsl.com/templates/place-detail)                       | Heritage-site detail variant.             |

---

## 9. UI Requirements

### 9.1 Global
- **NavBar:** FambulTik logo + Home, About, Account links (`t("nav.*")`). Auth-aware.
- **Footer:** DS Footer pattern; renders `t("disclaimer.full")`, copyright with year, *A TpGroup company*, "Built with Claude Code."
- **Persistent disclaimer alert** on Home (dismissible; persists in `localStorage`).
- **Auth state** via `AuthProvider`.

### 9.2 Home (`/`)
- Hero band: `t("home.hero.title")` (display font), `t("home.hero.subtitle")`, CTA `t("home.hero.cta")`.
- Responsive grid (1 / 2 / 3 columns).
- Cards built from `Attraction` rows.

### 9.3 Attraction Detail (`/attractions/:id`)
- Breadcrumb: Home › Attractions › *{name}*.
- Hero image gallery.
- Title (display font) + region subtitle.
- Rating row, tag chips.
- Long description.
- Hours block (labels from `t("attraction.openingHours")` etc.).
- Responsive 16:9 YouTube embed if `videoUrl`.
- **Get Directions** button (`t("attraction.directions.cta")`).
- **(P2)** Action bar: Bookmark, Favorite, *Schedule a Tour*.
- FAQ accordion (from `faqs[]`).
- Sources footer.

### 9.4 Schedule a Tour (P2)
- Dialog opened from detail page.
- Fields: tour date, party size (1–20), notes.
- Submit → `tour_bookings` insert; toast `t("schedule.success")`.

### 9.5 My Account (`/account`) — P2
1. Profile — email, member-since, sign-out.
2. Bookmarks — grid with remove.
3. Favorites — same shape.
4. Scheduled Tours — list with cancel.

Empty states (DS EmptyState) for each section, copy from `t("account.*.empty")`.

### 9.6 Sign in / Sign up
- DS Form Fields. Email + password.
- Errors mapped from `errors.auth.*` keys.

### 9.7 About (`/about`)
- Short paragraph on FambulTik (`t("about.brand")`).
- Full disclaimer (`t("disclaimer.full")`).
- Data-source credits + DS credit link.

---

## 10. Accessibility — WCAG 2.2 Level AA

Salone Explorer **must** conform to WCAG 2.2 Level AA. The TpGroup Design System is WCAG 2.2 AA — using its tokens and components is the cheapest path to conformance, but the application code must still satisfy each criterion.

### 10.1 Perceivable
- **1.1.1 Non-text content (A).** Every `<img>` carries meaningful `alt`; decorative images `alt=""`.
- **1.2.2 Captions for prerecorded media (A).** YouTube embeds enable closed captions (`cc_load_policy=1`).
- **1.3.1 Info and relationships (A).** Semantic HTML; `<label>` for every input.
- **1.3.5 Identify input purpose (AA).** `autocomplete="email"`, `"new-password"`, etc.
- **1.4.3 Contrast minimum (AA).** Body ≥ 4.5 : 1; large/bold ≥ 3 : 1. Verified by axe-core.
- **1.4.4 Resize text (AA).** Usable at 200 % zoom without horizontal scrolling.
- **1.4.10 Reflow (AA).** Single-column reflow at **320 CSS px**.
- **1.4.11 Non-text contrast (AA).** UI components and focus indicators ≥ 3 : 1.
- **1.4.12 Text spacing (AA).** Layout survives the 1.5 / 2× / 0.12× / 0.16× test.
- **1.4.13 Content on hover or focus (AA).** Tooltips dismissable (`Esc`), hoverable, persistent.

### 10.2 Operable
- **2.1.1 Keyboard (A).** All functionality keyboard-reachable.
- **2.1.2 No keyboard trap (A).** Dialogs trap *and* return focus.
- **2.4.3 Focus order (A).** DOM order matches visual order.
- **2.4.4 Link purpose (A).** Meaningful link text.
- **2.4.7 Focus visible (AA).** Focus ring on every interactive element.
- **2.4.11 Focus not obscured — minimum (AA, new in 2.2).** Focused element at least partially visible.
- **2.4.13 Focus appearance (AA, new in 2.2).** Indicator ≥ 3 : 1 and ≥ 2 CSS px ring.
- **2.5.7 Dragging movements (AA, new in 2.2).** Carousel exposes prev/next alongside swipe.
- **2.5.8 Target size minimum (AA, new in 2.2).** ≥ 24 × 24 CSS px; project standard is **44 × 44**.

### 10.3 Understandable
- **3.1.1 Language of page (A).** `<html lang="en">`.
- **3.2.3 Consistent navigation (AA).** NavBar / Footer identical on every page.
- **3.2.4 Consistent identification (AA).** A heart icon is always "Favorite."
- **3.2.6 Consistent help (A, new in 2.2).** Footer help/contact link on every page.
- **3.3.1 Error identification (A).** Errors in plain text, `aria-describedby`.
- **3.3.2 Labels or instructions (A).** Every input has a visible label.
- **3.3.3 Error suggestion (AA).** Suggest corrections.
- **3.3.4 Error prevention (AA).** Schedule confirmation step.
- **3.3.7 Redundant entry (A, new in 2.2).** Pre-fill where possible.
- **3.3.8 Accessible authentication minimum (AA, new in 2.2).** No CAPTCHA; password paste allowed.

### 10.4 Robust
- **4.1.2 Name, role, value (A).** Correct ARIA on custom controls.
- **4.1.3 Status messages (AA).** Toasts use `role="status"` or `role="alert"`.

### 10.5 Testing posture
- **Automated:** `@axe-core/playwright` in CI; Lighthouse Accessibility ≥ 95.
- **Manual:** keyboard-only walkthrough + one VoiceOver/NVDA pass per release.
- **Linting:** `eslint-plugin-jsx-a11y` (`recommended`); errors fail the build.

---

## 11. Mobile & Responsive Standards

| Token | Min width | Layout                       |
| ----- | --------- | ---------------------------- |
| (base)| 0         | Single column, stacked.      |
| `sm`  | 640 px    | Two-column grids start.      |
| `md`  | 768 px    | Tablet nav, larger gutters.  |
| `lg`  | 1024 px   | Three-column attraction grid.|
| `xl`  | 1280 px   | Capped max-width container.  |

- Viewport meta with `viewport-fit=cover`.
- Touch targets ≥ **44 × 44 px**.
- Body 16 px, line-height 1.5.
- Explicit `width`/`height` on images.
- Correct `inputmode` and `autocomplete`.
- Verified at **320 / 375 / 414 / 768 / 1024 / 1440 px**.

---

## 12. Project Structure

```
salone-explorer/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml
│   │   ├── codeql.yml
│   │   ├── security.yml
│   │   └── a11y.yml
│   └── dependabot.yml
├── index.html
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
├── tsconfig.json
├── package.json
├── .env.example
├── public/
│   ├── robots.txt
│   ├── sitemap.xml
│   ├── llms.txt
│   └── favicon.svg
├── scripts/
│   ├── generate-sitemap.ts
│   └── migrate-attractions-to-supabase.ts  # Phase 2.5 (optional)
├── supabase/
│   └── schema.sql
├── tests/
│   └── a11y/
│       └── smoke.spec.ts
└── src/
    ├── main.tsx                    # router + HelmetProvider + AuthProvider
    ├── App.tsx
    ├── index.css                   # imports tokens.css + tailwind
    ├── assets/
    │   └── brand/fambultik/
    │       ├── logo-light.svg
    │       ├── logo-dark.svg
    │       └── favicon.svg
    ├── styles/
    │   └── tokens.css              # CSS variables (§8.4)
    ├── data/                       # ── DATA LAYER ────────────────
    │   ├── types.ts                # Attraction type
    │   ├── attractions.json        # 8 records, sourced from §4
    │   └── regions.json            # district → province lookup
    ├── content/                    # ── CONTENT LAYER ─────────────
    │   ├── strings.en.json         # flat key→string map
    │   └── pages/                  # longer-form copy (optional)
    │       ├── home.json
    │       └── about.json
    ├── lib/                        # ── CODE LAYER ────────────────
    │   ├── supabase.ts
    │   ├── content/
    │   │   ├── attractions.ts          # AttractionRepository interface
    │   │   ├── attractions.file.ts     # JSON implementation
    │   │   ├── attractions.supabase.ts # Supabase implementation (P2.5)
    │   │   ├── strings.ts              # t() helper
    │   │   └── index.ts                # barrel; picks active impl
    │   ├── bookmarks.ts
    │   └── bookings.ts
    ├── seo/
    │   ├── SeoHead.tsx
    │   ├── JsonLd.tsx
    │   └── graph.ts
    ├── auth/
    │   ├── AuthProvider.tsx
    │   └── ProtectedRoute.tsx
    ├── components/
    │   ├── NavBar.tsx
    │   ├── Footer.tsx
    │   ├── FambulTikLogo.tsx
    │   ├── AttractionCard.tsx
    │   ├── RatingBadge.tsx
    │   ├── HoursBlock.tsx
    │   ├── DirectionsButton.tsx
    │   ├── SourcesList.tsx
    │   ├── FaqAccordion.tsx
    │   ├── BookmarkButton.tsx
    │   ├── FavoriteButton.tsx
    │   └── ScheduleTourModal.tsx
    └── pages/
        ├── HomePage.tsx
        ├── AttractionDetailPage.tsx
        ├── AboutPage.tsx
        ├── SignInPage.tsx
        ├── SignUpPage.tsx
        ├── AccountPage.tsx
        └── NotFoundPage.tsx
```

---

## 13. SEO & GEO

### 13.1 Classic SEO
- Semantic HTML5; one `<h1>` per page.
- Per-page `<title>` (≤ 60 chars) and `<meta name="description">` (≤ 160 chars) via `react-helmet-async`.
- OG and Twitter Cards on every page.
- Canonical URLs from `VITE_SITE_URL`.
- `public/robots.txt` allows all; references `sitemap.xml`; blocks `/account`, `/signin`, `/signup`.
- `public/sitemap.xml` generated at build time from the active attractions repository.
- Pre-rendering via `vite-plugin-prerender` for `/`, `/about`, every `/attractions/:id`.

### 13.2 GEO
- Definitional lead sentences (sourced into `longDescription`).
- Inline source attributions (paraphrased from §4).
- Per-attraction FAQ blocks → `FAQPage` JSON-LD.
- `public/llms.txt` per [llmstxt.org](https://llmstxt.org/) — also generated from the attractions repository.
- Visible "Last reviewed" date echoed as `dateModified` in JSON-LD (driven by `Attraction.lastReviewed`).

---

## 14. Structured Data — JSON-LD Entity Graph

Each page emits a Schema.org `@graph`. Builders live in `src/seo/graph.ts`.

### 14.1 Entity model
- `Organization` — TpGroup (SL) Limited.
- `TouristInformationCenter` — FambulTik / Salone Explorer (per FambulTik DS template).
- `WebSite` — Salone Explorer.
- `WebPage`, `BreadcrumbList` per route.
- `TouristAttraction` per attraction — `address`, `geo`, `aggregateRating`, `openingHoursSpecification`, `image`, `video`, `containedInPlace` → `TouristDestination` "Sierra Leone".
- `FAQPage` per attraction with `faqs[]`.

### 14.2 Validation
- [Schema.org Validator](https://validator.schema.org/) + [Rich Results Test](https://search.google.com/test/rich-results) report zero errors on detail pages.

---

## 15. Security — SAST in CI

Four workflows; merges to `main` require all four green.

`ci.yml` — `npm ci`, ESLint (incl. `jsx-a11y`), `tsc --noEmit`, `npm run build`.

`codeql.yml` — GitHub CodeQL, `security-and-quality` queries.

`security.yml` — Semgrep (`p/owasp-top-ten`, `p/javascript`, `p/typescript`, `p/react`, `p/secrets`) + `npm audit --audit-level=high`.

`a11y.yml` — `@axe-core/playwright` across `/`, `/attractions/tiwai-island`, `/about`, `/signin`, `/signup`; fails on serious/critical.

`dependabot.yml` — weekly npm + actions updates.

### Application-level
- No secrets in client code.
- Supabase RLS on every user-scoped table.
- `target="_blank" rel="noopener noreferrer"` on outbound links.
- Security headers via `vercel.json` (`X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`, `X-Frame-Options`).

---

## 16. Environment Variables

```env
VITE_SITE_URL=https://ai-led-sdlc-demo.vercel.app

# Data source toggle: "file" (Phase 1 default) or "supabase" (Phase 2.5)
VITE_ATTRACTIONS_SOURCE=file

# Phase 2
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=
```

If using the Vercel ↔ Supabase integration, rename `NEXT_PUBLIC_*` → `VITE_*`.

---

## 17. Branding & Legal

**Publisher:** TpGroup (SL) Limited.
**Brand:** FambulTik.
**Repository:** `git@github.com:click2tman/ai-led-sdlc-demo.git`.

**Disclaimer (render verbatim via `t("disclaimer.full")` in footer, `/about`, and the Home alert):**
> *Salone Explorer is built by TpGroup (SL) Limited under the FambulTik brand for demonstration and educational purposes only. It is not an official tourism service and does not represent any government body. Attraction details, opening hours, and ratings are curated from public sources and may be inaccurate or out of date. Always verify directly with the operator before travelling. No payments or real bookings are processed by this application.*

---

## 18. Build & Run

```bash
npm install
npm run dev
npm run build
npm run preview
npm run lint
npm run test:a11y
# Phase 2.5 (optional):
npm run migrate:attractions          # JSON → Supabase
```

Node 20+ required.

---

## 19. Delivery Workflow

### Phase 1 — Scaffold (≈ 8 min)
1. `npm create vite@latest salone-explorer -- --template react-ts`
2. `npm install` and runtime deps: `react-router-dom react-helmet-async @radix-ui/react-dialog @radix-ui/react-accordion @radix-ui/react-toast lucide-react class-variance-authority`
3. Dev deps: `tailwindcss postcss autoprefixer eslint eslint-plugin-jsx-a11y vite-plugin-prerender @axe-core/playwright @playwright/test wait-on`
4. `npx tailwindcss init -p`; wire FambulTik tokens.
5. Drop FambulTik logos into `src/assets/brand/fambultik/`. Set `<html lang="en">` in `index.html`.
6. Initialise git; commit; push to `git@github.com:click2tman/ai-led-sdlc-demo.git` on `main`.

### Phase 2 — Data, content, repository (≈ 8 min)
7. Create `src/data/types.ts` with the `Attraction` type.
8. Create `src/data/attractions.json` with 8 entries paraphrased from §4 sources.
9. Create `src/data/regions.json`.
10. Create `src/content/strings.en.json` (all UI strings, no English literals in any component).
11. Create the repository abstraction in `src/lib/content/` per §5.2.3.

### Phase 3 — SEO, JSON-LD, brand, UI, accessibility (≈ 22 min)
12. Wire `BrowserRouter` + `HelmetProvider` in `main.tsx`.
13. Implement DS-aligned components and pages (Home, Detail, About, NotFound). Components use `t()` for every string and the repository for every datum.
14. Add `src/seo/graph.ts`, `JsonLd.tsx`, `SeoHead.tsx`.
15. Add `public/robots.txt`, `public/llms.txt`, `vercel.json`.
16. Add `scripts/generate-sitemap.ts`; wire to `npm run build`.
17. Verify keyboard navigation + 320 / 375 / 768 / 1024 / 1440 px.

### Phase 4 — CI + Deploy v1 (≈ 7 min)
18. Add `.github/workflows/*` and `dependabot.yml`.
19. Add `tests/a11y/smoke.spec.ts`.
20. Update README; commit; push.
21. Connect repo to Vercel (Vite preset, `dist`); set `VITE_SITE_URL` and `VITE_ATTRACTIONS_SOURCE=file`; deploy.
22. Validate live URL with Schema.org Validator + Lighthouse.

### Phase 5 — Supabase provisioning (≈ 10 min)
23. Provision Supabase (Vercel integration or manual).
24. Run §6.3 schema.
25. Enable Email auth; disable Confirm-email.
26. `npm install @supabase/supabase-js`; add `src/lib/supabase.ts`.
27. Set `VITE_SUPABASE_*`.

### Phase 6 — Auth + account (≈ 30 min)
28. `AuthProvider`, `ProtectedRoute`.
29. `SignInPage`, `SignUpPage`, `BookmarkButton`, `FavoriteButton`, `ScheduleTourModal`, `AccountPage`.
30. Update `NavBar`.

### Phase 7 — Ship v2 (≈ 10 min)
31. Smoke test full flow.
32. RLS check across two accounts.
33. Push; confirm Vercel deploy with env vars.

### Phase 2.5 — Optional: migrate attractions to Supabase (≈ 15 min)
34. Apply the `public.attractions` table + public-read RLS (§5.3).
35. Implement `attractions.supabase.ts`.
36. Write and run `scripts/migrate-attractions-to-supabase.ts` to upsert from JSON.
37. Set `VITE_ATTRACTIONS_SOURCE=supabase` in Vercel; redeploy. No UI changes.

### Phase 8 — Future: Payload CMS (out of scope)
Documented in §5.4 as the architectural endpoint.

---

## 20. Acceptance Criteria

### Phase 1
- [ ] `npm run build`, `tsc --noEmit`, ESLint (incl. `jsx-a11y`) clean.
- [ ] **No English literals appear in any `.tsx` or `.ts` source file outside `src/data/`, `src/content/`, or test files.** Verified by a quick grep.
- [ ] **No attraction facts appear in any `.tsx` or `.ts` source file** outside `src/data/attractions.json` and the repository module.
- [ ] FambulTik logo present in NavBar and footer; tokens applied.
- [ ] Home renders the attractions returned by `attractions.getAll()`.
- [ ] Detail page renders the attraction returned by `attractions.getById(id)`.
- [ ] Disclaimer alert renders on Home; full disclaimer in footer and `/about`.
- [ ] Usable at 320 / 375 / 414 / 768 / 1024 / 1440 px; touch targets ≥ 44 × 44 px.
- [ ] axe-core CI reports zero serious or critical violations on five routes.
- [ ] Lighthouse (mobile): A11y ≥ 95, SEO ≥ 90, BP ≥ 90, Perf ≥ 80.
- [ ] JSON-LD validates with zero errors on detail pages.
- [ ] `/robots.txt`, `/sitemap.xml`, `/llms.txt` resolve.
- [ ] CI, CodeQL, Security, A11y workflows green on `main`.

### Phase 2
- [ ] Sign-up, sign-in, sign-out work.
- [ ] Bookmark / Favorite persist across reloads.
- [ ] Scheduling a tour creates a row visible on `/account`.
- [ ] Cancelling sets `status='cancelled'`.
- [ ] `/account` redirects to `/signin` while signed out.
- [ ] RLS verified across two accounts.
- [ ] WCAG 2.2 AA still met on new pages.

### Phase 2.5 (optional)
- [ ] `VITE_ATTRACTIONS_SOURCE=supabase` produces identical pages.
- [ ] No component diff between file and supabase modes.
- [ ] `public.attractions` RLS allows public read; no write policy.

---

## 21. Roadmap

- Tag filters on Home (driven by tag list in content/).
- Client-side search.
- Dark mode; contrast and focus still 2.2 AA.
- Editable `display_name` in profile.
- Auto-confirm bookings after 24 h (Supabase Edge Function).
- Krio locale (`strings.kri.json`) — proves the i18n on-ramp.
- **Phase 8: Payload CMS** (§5.4). Replace `fileAttractionRepository` and the strings module with `payloadAttractionRepository` and a Payload-driven strings hook. Editorial team manages everything in the Payload admin UI.

---

## 22. Constraints & Guardrails for Claude Code

- **Do not** hard-code any user-facing string in a component, page, or library file. All strings live in `src/content/`.
- **Do not** hard-code any attraction fact, opening hour, rating, or coordinate in a component, page, or library file. All facts live in `src/data/`.
- **Do not** import `attractions.json` directly from a component or page. Components consume the `attractions` repository from `src/lib/content`.
- **Do not** invent attraction facts. Pull from §4 sources; when uncertain, set `hours.notes: "Hours vary — confirm locally"`.
- **Do not** introduce a payment gateway or external booking API.
- **Do not** add libraries beyond §3 unless strictly necessary; justify in a code comment.
- **Do not** store secrets in client code.
- **Do not** ship without the disclaimer alert, footer disclaimer, and `/about` disclaimer.
- **Do not** disable RLS, weaken CI, or `eslint-disable` jsx-a11y rules to make builds pass.
- **Do** enable RLS on every new Supabase table.
- **Do** keep the repository pattern intact — when adding a new data type, define the interface first, then a file-based implementation, then optionally a Supabase one.
- **Do** test every interactive element via keyboard before committing.
- **Do** run `npm run test:a11y` locally before pushing.
- **Do** validate JSON-LD before declaring a page done.
- **Do** commit after each phase.
- **Stop and ask** before deviating from §5 (architecture), §6.1 (type), §6.3 (schema), §8 (brand), §10 (a11y), or §12 (structure).

---

*End of specification. Begin scaffolding.*
