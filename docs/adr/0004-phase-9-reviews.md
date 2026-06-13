<!-- 0004-phase-9-reviews.md - ADR: real-time reviews schema, RLS, repository, and the SSG/JSON-LD aggregateRating tension for SPEC Phase 9 -->

# ADR 0004: Phase 9 real-time reviews — schema, RLS, repository, and SSG-vs-live aggregateRating

- Status: Accepted (human-ratified 2026-06-06)
- Date: 2026-06-06
- Deciders: Architect agent (draft); ratified by Tamba S Lamin
- Ratified decisions on the open questions: (1) JSON-LD aggregateRating +
  Review use a build-time snapshot baked into prerendered HTML, with
  graceful fallback to static attraction.rating when Supabase is
  unconfigured; (2) reviews.status is text + check, not a Postgres enum;
  (3) versioned migration dir, supabase/migrations/0001_reviews.sql;
  (4) newest 5 published Review nodes per page, aggregateRating over all
  published.
- Traces to: SPEC §6.6 (reviews DDL + RLS), §9.3 (Attraction Detail),
  §13.3 (AEO Review/aggregateRating), §14.1 (entity model), §15 (P9
  security), §19 Phase 9 (steps 38-41), §20 Phase 9 acceptance
- Relates to: ADR 0002 / ADR 0003 (browser-free build-time SSG)

## Context

What is true today:

- The detail page is **prerendered at build time** by a browser-free SSG
  (ADR 0002 amendment): `scripts/prerender.ts` imports the SSR bundle,
  runs each route's loader through React Router's static handler, and
  writes `dist/<route>/index.html`. The build runs with the **file**
  attractions repository, **no Supabase env, no browser, no auth session.**
- `src/seo/graph.ts#touristAttraction()` emits `aggregateRating` from the
  **static** `attraction.rating` / `attraction.reviewCount` fields baked
  into `src/data/attractions.json`. There is no `Review` node today.
- The account repositories (`src/lib/account/`) establish the canonical
  pattern: a TS interface, a Supabase-only implementation, a barrel
  export; `user_id` is read from `getUser()` to satisfy the RLS
  `with check`, and writes additionally filter `user_id` as
  defense-in-depth. RLS (`auth.uid() = user_id`) is the primary guard.
- SPEC §6.6 ships a **draft** `reviews` DDL and instructs: "Finalise via
  an architect ADR before building."

Forces:

1. The JSON-LD that answer engines crawl lives in **prerendered HTML**,
   but reviews are **live** in Postgres. These update on different clocks
   (build vs. user action). Something must give.
2. SPEC §6.6 RLS lets authors manage **only their own** reviews. SPEC §15
   and §19 step 41 require a **moderation path** (flag/remove). Pure
   client RLS cannot let a moderator act on **another** user's row.
3. The `Review.text` we would inject into JSON-LD is user-generated and
   lands inside a `<script type="application/ld+json">` tag — an XSS
   surface distinct from React's text rendering.
4. Supabase has **no built-in per-insert rate limit**. The §6.6
   `unique (user_id, attraction_id)` constraint already caps a user at
   one review per attraction.
5. §6.3 (profiles, saved_attractions, tour_bookings) **must not be
   touched** (api-conventions, CLAUDE.md). Reviews is a **new** table.

## Decisions

### D1 — Reviews schema: accept §6.6 DDL with three additive refinements

Adopt the §6.6 `reviews` table as the canonical schema, with the
following deltas (all additive; none change the §6.6 columns' meaning):

1. **Add `updated_at timestamptz not null default now()`** plus a
   `before update` trigger that sets it. Rationale: §9.3 allows a user to
   edit their own review; without `updated_at` the JSON-LD `Review`
   `dateModified` and "edited" affordances have no source. This is a new
   column on a new table — no §6.3 impact.
2. **Add a second index `on public.reviews (user_id)`.** The §6.6 index
   `(attraction_id, status)` serves the public list query; `(user_id)`
   serves "my reviews" and the defense-in-depth `user_id` write filter.
   The composite unique `(user_id, attraction_id)` does not left-cover
   bare `user_id` lookups well enough to rely on.
3. **Keep `status` as a `text` + `check`** (not a Postgres enum), unlike
   §6.3's `saved_kind` / `booking_status` enums. Rationale: moderation
   states are more likely to grow (e.g. `pending`, `spam`); a `check`
   constraint is cheaper to evolve than `alter type ... add value`. This
   is a deliberate, documented divergence from the §6.3 enum convention,
   justified by the moderation lifecycle. (Flagged for human review.)

Confirmed as-is from §6.6: `rating int check between 1 and 5`,
`body text check char_length between 1 and 2000`, status set
`{published, flagged, removed}` default `published`,
`unique (user_id, attraction_id)`, `on delete cascade` to `auth.users`.

### D2 — RLS: §6.6 author policies in Phase 9; cross-user moderation is a service-role path, deferred to a follow-up

Ship the four §6.6 client policies verbatim in the Phase 9 migration:

- `select using (status = 'published' or auth.uid() = user_id)` —
  public reads published; authors also read their own non-published.
- `insert with check (auth.uid() = user_id)`,
  `update using (auth.uid() = user_id)`,
  `delete using (auth.uid() = user_id)` — own-manage only.

**Cross-user moderation (flag/remove someone else's review) is NOT done
through client RLS.** Granting a "moderator" client role would require a
policy that reads a role claim, widening the table's write surface and
adding an admin-role mechanism that does not exist in the codebase today.
Phase 9 ships the **author-managed lifecycle** plus the **schema and the
gating** (`status` controls public visibility), but the **moderator
action surface** is performed out-of-band:

- **In Phase 9 (this ADR):** moderation is **manual via the Supabase
  dashboard / service role** (an operator sets `status='removed'` or
  `'flagged'`). The public list already excludes non-`published` rows by
  RLS, so a dashboard status change is sufficient to take a review down.
  No moderator UI, no admin role, no Edge Function in Phase 9.
- **Deferred (follow-up issue):** a self-serve **flag** affordance for
  signed-in users (report another user's review) and an automated
  moderation queue require either a separate `review_flags` table
  (user-scoped, RLS `auth.uid() = user_id`, one flag per user per
  review) feeding an operator view, or a Supabase Edge Function holding
  the service-role key. Both are **out of Phase 9 scope**; tracked
  separately so Phase 9 stays shippable.

This satisfies §20 Phase 9 ("only published reviews publicly visible; RLS
verified across two accounts") and §19 step 41 ("status gating,
flag/remove") at the data/operator level, while being explicit that the
*end-user* flag button and admin role are follow-on work.

### D3 — aggregateRating + Review JSON-LD: build-time snapshot, baked into the prerendered HTML (chosen); live ReviewList hydrates client-side

This is the crux. Three options were weighed (see Alternatives). The
decision:

**The JSON-LD `aggregateRating` and `Review` nodes are a build-time
snapshot baked into the prerendered HTML.** At build, the prerender step
reads published reviews and computes per-attraction aggregates, and
`graph.ts` emits `aggregateRating` (count + mean) and up to N `Review`
nodes from that snapshot. The **visible** `ReviewList` on the page
hydrates **client-side** from Supabase Realtime and is always live.

Concretely:

- Because the SSG build has **no Supabase session and runs the file
  repository**, the build cannot call the browser Supabase client. The
  snapshot is produced by a **build-time read** using the **anon key**
  (resolved at implementation: published reviews are public-read under
  RLS, so the anon key has exactly the access the aggregate needs and
  **no service-role secret is introduced into the build** — this
  supersedes the earlier service-role assumption and resolves Open
  Question 1, neutralising risk R1), written to a generated, git-ignored
  data artifact (`src/data/reviews.snapshot.json`, committed as an empty
  `{}` default) that the graph reads at
  prerender time. If the snapshot is absent (e.g. local build with no
  Supabase configured), `graph.ts` **falls back to the existing static
  `attraction.rating` / `attraction.reviewCount`** — the Phase 1
  behaviour — so the build never fails for lack of live data.
- `aggregateRating` therefore reflects reviews **as of the last deploy**
  (stale between deploys). For a tour-guide site this is acceptable:
  answer engines re-crawl on their own cadence and a daily/weekly deploy
  (or a deploy hook on review volume) keeps it fresh enough. The
  **on-page** rating the human sees is the live one.
- The live `ReviewList` is a **client-only** component (renders nothing
  meaningful during SSG, or a skeleton). It must not block prerender and
  must not throw when Supabase is unconfigured (mirror `isSupabaseConfigured()`).

Rationale for choosing snapshot over client-injected JSON-LD: JSON-LD
injected only after client hydration is **unreliable for crawlers** that
read static HTML (the whole reason ADR 0002 prerenders). Baking a
snapshot keeps the crawlable contract in the static HTML — consistent
with the SSG architecture — while the live list serves humans.

### D4 — Repository contract: `ReviewRepository` in `src/lib/account/reviews.ts`

Reviews are user-authored, Supabase-only data — the same shape as
saved/bookings. Place them in the existing account module, not a new
top-level lib, to reuse the established pattern and barrel.

- Types in `src/lib/account/types.ts`: `Review`, `NewReview`,
  `ReviewStatus`, and an aggregate `AttractionRating { mean, count }`.
- Interface in `src/lib/account/reviews.ts`:

  ```
  listPublished(attractionId): Promise<Review[]>      // published only, newest first
  getOwn(attractionId): Promise<Review | null>        // the caller's review, any status
  create(input: NewReview): Promise<Review>           // user_id from getUser()
  updateOwn(id, patch): Promise<Review>               // rating/body; user_id-filtered
  deleteOwn(id): Promise<void>                         // user_id-filtered
  subscribe(attractionId, onChange): () => void        // Realtime; returns unsubscribe
  ```

- `subscribe` wraps a Supabase Realtime channel filtered to the
  attraction and `status=published`; it returns the teardown function for
  `useEffect` cleanup. It is **client-only** and must no-op (return a
  noop teardown) when Supabase is unconfigured rather than throw.
- `create`/`updateOwn`/`deleteOwn` follow the saved/bookings precedent:
  read `getUser()`, set/filter `user_id` explicitly as defense-in-depth.
- Export via `src/lib/account/index.ts` as `reviews: ReviewRepository`.

The **aggregate** the JSON-LD needs at build time is computed by a
**separate build-time reader** (anon key; published reviews are
public-read), not this browser repository — keep the two read paths
distinct. Note: Supabase Realtime `postgres_changes` filters are
single-column, so `subscribe` filters on `attraction_id` only and relies
on the RLS-gated `listPublished` refetch for the published view; the
original "filtered to ... `status=published`" wording was not achievable
in one filter.

### D5 — Security

- **JSON-LD XSS:** the existing `JsonLd.tsx` and `prerender.ts` both
  already `JSON.stringify(...).replace(/</g, '\\u003c')`, which neutralises
  `</script>` breakout for any string node, **including** user-generated
  `Review.text`. This is the primary control and it already exists — the
  ADR's requirement is that review text flow through the **same**
  serializer (it does, via `graph.ts`). In addition, **store-side
  sanitisation**: strip control chars and cap length at the DB `check`
  (1-2000). Render review text in React as **plain text only** (no
  `dangerouslySetInnerHTML`), so the on-page surface is safe by React's
  default escaping.
- **Rate limiting:** the §6.6 `unique (user_id, attraction_id)` is the
  **primary guard** — one row per user per attraction caps spam
  structurally. Accept it as sufficient for Phase 9. An insert-rate
  trigger or Edge Function is **deferred** (only meaningful once a user
  can post many reviews, which the unique constraint prevents). Document
  this explicitly so a reviewer knows it was a decision, not an omission.
- **Moderation gating:** public visibility is enforced by the RLS
  `select` predicate (`status = 'published' ...`), not by client
  filtering — a removed review is invisible at the data layer.
- **No new secret anywhere.** The build-time aggregate read uses the
  **anon key** (published reviews are public-read), so there is no
  service-role key in the build or the client. The browser keeps the
  anon key (`isSupabaseConfigured`).
- **No other-user ids exposed.** `listPublished` omits `user_id`, so a
  visitor never receives other reviewers' auth UUIDs (the form's own
  review is matched by id via the separately-fetched `getOwn`).

### D6 — Content keys and graph changes

- New content namespace `reviews.*` in `src/content/strings.en.json`:
  list heading, empty state, the submit form labels/placeholders, rating
  input label, submit/edit/delete CTAs, success/error microcopy, the
  "sign in to review" gate, and the "one review per attraction" notice.
  All read via `t("reviews.*")`. No strings in components.
- `graph.ts`: add a `reviewNode()` builder and extend `touristAttraction`
  /`attractionGraph` to (a) source `aggregateRating` from the snapshot
  aggregate when present, else the static fields, and (b) attach up to N
  `Review` nodes (`author` as `Person` with display name only — no email
  or PII; `reviewRating`, `reviewBody`, `datePublished`). This is the
  only change to `graph.ts`'s contract and it is additive.

### D7 — Schema delivery: new migration file; §6.3 untouched

Do **not** edit `supabase/schema.sql` in place (it is the canonical §6.3
artifact). Add a new ordered migration
`supabase/migrations/0001_reviews.sql` (or `supabase/reviews.sql` if the
project keeps flat files) containing the table, indexes, RLS enable, the
four policies, and the `updated_at` trigger — RLS in the **same**
migration (api-conventions hard rule). `schema.sql` remains the §6.3
baseline; the migration layers Phase 9 on top.

## Consequences

Positive:

- Crawlable `aggregateRating`/`Review` stays in static HTML — consistent
  with the SSG architecture (ADR 0002), no regression for answer engines.
- The repository reuses the proven account pattern; RLS is the primary
  guard with defense-in-depth writes.
- §6.3 is untouched; Phase 9 is purely additive.
- Phase 9 ships without an admin-role mechanism or Edge Function.

Negative / cost:

- **Staleness:** JSON-LD ratings lag the live list by up to one deploy
  cycle. Mitigation: deploy hook or scheduled rebuild; documented as a
  known tradeoff.
- **Build coupling:** the build now optionally reads Supabase (service
  role) to produce the snapshot, adding a build-env secret and a
  graceful-fallback path. The fallback to static fields keeps local and
  unconfigured builds working.
- **Moderation is operator-manual in Phase 9** — no end-user flag button,
  no queue. Acceptable for launch; tracked as follow-up.

Follow-on work (separate issues, not Phase 9):

1. End-user **flag** affordance + `review_flags` table (RLS) or Edge
   Function moderation queue.
2. Admin/moderator role and a moderation UI.
3. Optional insert-rate trigger if abuse appears despite the unique
   constraint.
4. Deploy-on-review-volume hook to cut JSON-LD staleness.

## Alternatives considered

- **Client-side-only JSON-LD (inject aggregateRating/Review after
  hydration).** Rejected: crawlers that read static HTML (the reason ADR
  0002 prerenders at all) would miss it; defeats the AEO goal of §13.3.
- **Fully dynamic detail page (SSR per request / drop prerender for this
  route).** Rejected: contradicts ADR 0002/0003 (browser-free SSG, no
  server runtime on the Vercel static path); large, irreversible
  architecture change for a freshness gain answer engines don't reward.
- **Moderator client RLS via a role claim.** Rejected for Phase 9: adds
  an admin-role mechanism and widens the table write surface; the
  service-role/dashboard path achieves take-downs with no new attack
  surface. Revisit when a moderation UI is actually built.
- **`status` as a Postgres enum (matching §6.3 convention).** Rejected:
  moderation states are likely to grow; `alter type add value` is more
  rigid than editing a `check`. Documented divergence (D1.3).
- **Reviews in a new `src/lib/reviews/` top-level module.** Rejected:
  reviews are user-scoped Supabase data identical in shape to
  saved/bookings; the `src/lib/account/` module already owns that pattern
  and barrel. A new tree would duplicate structure.

## Open questions — RESOLVED at ratification (2026-06-06)

1. **Build-time read.** RESOLVED: use a **build-time snapshot** baked into
   the prerendered HTML. Refined at implementation to use the **anon key**
   (published reviews are public-read), so there is **no service-role
   secret in the build** — this neutralises risk R1. Fallback to the
   static `attraction.rating` when the snapshot is empty.
2. **enum-vs-check.** RESOLVED: `status` is `text + check` (D1.3).
3. **Migration layout.** RESOLVED: versioned dir,
   `supabase/migrations/0001_reviews.sql`; `schema.sql` (§6.3) untouched.
4. **Review nodes per page.** RESOLVED: newest **5** published Review
   nodes; `aggregateRating` covers all published.

### Implementation deltas from the draft (recorded for traceability)
- **Pseudonymous reviews (refines D6):** profiles are not publicly
  readable and `display_name` is largely unset, so Phase 9 reviews carry
  no author name on-page or in JSON-LD (`author` is a generic Person).
  Named reviews are a tracked follow-up.
- **Anon key, not service-role (refines D3/D5/R1):** see above.
- **RLS update hardening (security review):** the `own review update`
  policy gates BOTH `using` and `with check` on `status = 'published'`,
  so an author cannot edit or re-publish a review an operator took down.
- **`listPublished` omits `user_id`** so other users' auth UUIDs never
  reach the client.
