# AI-Led Coding Class — Student Guide

> **Course:** AI-Led Software Development Lifecycle (SDLC) Demo
> **Instructor:** Tamba Slamin · TpGroup (SL) Limited
> **Brand:** FambulTik (TpGroup heritage-and-diaspora subsidiary)
> **Reference repo:** `git@github.com:click2tman/ai-led-sdlc-demo.git`
> **Design system:** [design.tpgroupsl.com](https://design.tpgroupsl.com/)
> **Deliverable:** A live, WCAG 2.2 AA, mobile-responsive, FambulTik-branded Sierra Leone tour-guide web app — with code, data, and content cleanly separated — built using Claude Code.

This handout has three jobs:

1. **Show you exactly how the spec for today's project was written** — seven prompts, in sequence, with commentary on each.
2. **Teach you the prompting pattern** so you can apply it to any project after the class.
3. **Give you the in-class workflow** for taking the spec from `SPEC.md` to a deployed Vercel URL.

You will leave the class with a public GitHub repo, a live Vercel URL, a branded and accessible working app whose content can be moved to a CMS without touching UI code, and a reusable method for building software with an AI agent.

---

## Table of Contents

1. [The Mental Model — Specs First, Then Code](#1-the-mental-model--specs-first-then-code)
2. [The Seven Prompts That Built This Spec](#2-the-seven-prompts-that-built-this-spec)
3. [Patterns You Should Steal](#3-patterns-you-should-steal)
4. [Common Pitfalls](#4-common-pitfalls)
5. [The In-Class Workflow](#5-the-in-class-workflow)
6. [Your Turn — Build Your Own Spec](#6-your-turn--build-your-own-spec)
7. [Reference Materials](#7-reference-materials)

---

## 1. The Mental Model — Specs First, Then Code

A common mistake when working with an AI coding agent is to **describe the code you want**, line by line. That just makes you a slow typist.

A better approach is to **describe the product** — its scope, data model, brand, content architecture, pages, accessibility bar, security posture, deployment target — and then let the agent generate, test, and revise the code. Your job is the spec; the agent's job is the implementation.

This class delivers three artefacts together:

- **`SPEC.md`** — the single source of truth for the build.
- **`README.md`** — the repo's front door.
- **A working, deployed app** — Claude Code builds it from the spec while we watch.

The interesting part of this handout is the *journey to the spec*. The spec was not written in one shot — it evolved through seven prompts. We will walk through each.

---

## 2. The Seven Prompts That Built This Spec

### Prompt 1 — Frame the problem and the constraints

```text
I am going to be teaching an AI-LED Coding class. The goal is to build a
small app within 45 mins using claude code inside terminal or IDE. The
students will come in with a spec. Claude code will use the spec file to
iterative develop the app, push code to github, publish the app on vercel.
Help me generate an example spec file to build a simple tour Guide app
Focussed on Sierra Leone Tourist Attractions. Attractions will include
descriptions, images, videos, opening hours, closing hours and ratings
and direction to the location.
```

**What it does well**

- States context (teaching artefact, not production).
- States the time budget (45 min) — sets a scope ceiling.
- States the deployment path (GitHub + Vercel) up front.
- Lists the data model in prose — fields of the data type.

**Takeaway.** A good first prompt is not a complete prompt. It establishes the frame.

---

### Prompt 2 — Replace defaults with explicit choices

```text
Use the following sources of data. Use Vite.
https://sierra-leone.org/, https://www.sierraleoneheritage.org/museum,
https://tourismsierraleone.com/, https://ntb.gov.sl/,
https://www.visitsierraleone.org/
```

**What it does well**

- **Constrains hallucination.** Five canonical URLs prevent invented attractions.
- **Overrides framework default** — "Use Vite" replaced Next.js in two words.
- Short and surgical. No need to restate the project.

**Takeaway.** Once the agent has a draft, you patch — you don't restart.

---

### Prompt 3 — Add features, add infrastructure

```text
Add bookmarking, favorites locations, my account, schedule a tour.
I will use supabase on Vercel for database.
```

**What it does well**

- Lists features as a bullet of nouns. The agent fills in tables, routes, and components.
- Names the backend choice — Supabase on Vercel signals the integration, env-var convention, and RLS expectations.

**Takeaway.** Trust the agent to add necessary scaffolding (RLS, contexts, protected routes) — but verify it added them.

---

### Prompt 4 — Productionise: branding, compliance, SEO/GEO, security

```text
Git repo for the work is git@github.com:click2tman/ai-led-sdlc-demo.git
- Company creating the app is TpGroup (SL) Limited. Add a disclaimer
that this app is for demo purposes only. Make sure the app is mobile
ready and responsive. Make sure the app is built with SEO and GEO in
mind. The content should have entity relationships with JSONLD. Include
SAST testing in the build on Github.
```

**What it does well**

- **Bundles concerns of the same shape.** Branding, legal, responsiveness, SEO, GEO, structured data, security — all "make this look like real software" requirements, designed coherently together.
- Names current best practices by their acronyms — "GEO," "JSON-LD," "SAST" unlock entire bodies of best practice.
- Pins the repo URL.

**Takeaway.** Use industry-standard acronyms when you know them. They unlock entire bodies of best practice in one prompt.

---

### Prompt 5 — Generate the front-door artefact

```text
Create a readme file for me
```

**What it does well**

- Trusts the established context.
- Shorter is fine when prior context is rich.

**Takeaway.** Late-stage prompts can be short. The conversation is the prompt.

---

### Prompt 6 — Design system, brand, and full accessibility

```text
Use https://design.tpgroupsl.com/ to inform the UI of the app. Following
the Fambul Tik Branding guide and use its logo. Make sure the app is
fully accessible and complies with WCAG 2.2 Level AA.
```

**What it does well**

- **Anchors the UI to a real, accessible design system.** The visual quality bar goes from "plausible" to "production-grade" in one prompt.
- Names the brand within the design system (FambulTik).
- Specifies the accessibility standard by version and level — the agent now knows to include the seven new criteria in WCAG 2.2.

**Takeaway.** Reference an external design system by URL when one exists. You inherit dozens of decisions for free.

---

### Prompt 7 — Separate code, data, and content

```text
Don't hard code the datasets. Can you create JSON or CSV files of the
datasets and load? Of can we store the datasets in the database? I don't
want to mix code with data or content. I want to make sure the students
are following industry best practice. Follow on work for this will be
to add Payload CMS in the backend where all the content, all strings,
labels, etc are stored in the CMS.
```

**What this prompt does well**

- **Names the architectural principle, not the implementation.** "I don't want to mix code with data or content" is *the* rule. The agent now derives the implementation (three-layer separation, repository pattern, strings module) from the principle.
- **Offers options instead of dictating.** "JSON or CSV files… or store in the database" lets the agent recommend, with reasoning. (For nested records like attractions, JSON wins; for flat reference data, CSV is fine.)
- **States the destination.** Naming **Payload CMS** as the eventual home tells the agent to build an abstraction today that swaps to a CMS tomorrow — not a one-off file loader that will be thrown away.
- **Frames it as pedagogy.** "Make sure the students are following industry best practice" pushes the agent past minimal solutions toward patterns that scale.

**What it produced**

- A new **§5 Content & Data Architecture** in the spec defining three layers: **code** (`src/components`, `src/pages`, `src/lib`), **data** (`src/data/*.json`), **content** (`src/content/*.json`).
- The **repository pattern**: an `AttractionRepository` interface in `src/lib/content/attractions.ts` with three planned implementations — `fileAttractionRepository` (Phase 1, JSON), `supabaseAttractionRepository` (Phase 2.5, Postgres), `payloadAttractionRepository` (Phase 8, CMS). A barrel module picks the active implementation by `VITE_ATTRACTIONS_SOURCE`.
- A **strings module** (`src/lib/content/strings.ts`) exposing `t(key)`; every component now calls `t("nav.home")` instead of hard-coding `"Home"`.
- A **Phase 2.5 migration script** that upserts attractions from JSON into a new `public.attractions` Supabase table with public-read RLS. Flip one env var, no UI changes.
- A **Phase 8 sketch** for Payload CMS — `attractions`, `pages`, `strings`, `faqs`, `media` collections; `siteSettings` global; CMS for editorial data, Supabase for user-generated data.
- **Two new acceptance criteria**: "No English literals in any `.tsx`/`.ts` source file outside `src/data/`, `src/content/`, or tests" and "No attraction facts outside `src/data/attractions.json` and its repository module" — both verifiable by `grep`.
- **Two new guardrails for Claude Code**: never import `attractions.json` directly from a component; never type a user-facing string outside `src/content/`.

**Takeaway.** When you name *both* the principle and the destination, the agent designs an abstraction. When you only name the implementation, you get a one-off. **Always name the destination.** "I'll migrate this to Payload CMS later" is worth ten minutes of explanation up front, because it shapes every decision the agent makes.

---

## 3. Patterns You Should Steal

These are the prompting patterns that did the heavy lifting today.

### 3.1 Start with frame, end with detail
Open with a wide-context prompt (audience, time budget, deployment target). Then **patch** with surgical follow-ups.

### 3.2 Name authoritative sources to suppress hallucination
LLMs invent facts when not constrained. Give the agent canonical URLs and instruct it to paraphrase and cite.

### 3.3 Use precise industry acronyms
"SAST," "RLS," "JSON-LD," "GEO," **"WCAG 2.2 Level AA,"** "CodeQL," "Payload CMS" each unlock substantial best practice in a few words.

### 3.4 State constraints, not just goals
"Use Vite" beats "use a fast modern frontend tool." Constraints reduce the agent's option space, which improves coherence.

### 3.5 Anchor to a real design system when one exists
If your org or client publishes a design system, link it. The agent will source tokens, components, logo, voice, and accessibility behaviour from it. Highest-leverage prompt you can write for the surface of the app.

### 3.6 Name the principle *and* the destination
"Don't mix code with data or content" is the principle. "Follow-on will be Payload CMS" is the destination. Together they force the agent to design an abstraction today. **This is the single most important pattern in the seven.** Without the destination, you get a JSON loader; with it, you get a repository pattern that survives three storage migrations.

### 3.7 Demand verification artefacts in the spec
The spec defines how to verify itself — acceptance criteria, axe-core in CI, Lighthouse thresholds, Schema.org validator passes, RLS smoke tests, grep checks for hard-coded strings. **"Demo code" vs "delivered software" is decided here.**

### 3.8 Let the agent push back on scope
A good agent should warn you when you've over-scoped — accept the warning.

---

## 4. Common Pitfalls

- **Trying to write the whole spec in one prompt.** You can't. Iterate.
- **Re-asking instead of patching.** Add the ninth attraction with "add Mount Bintumani," not by restating the spec.
- **Vague non-functional requirements.** "Make it secure" → "Add CodeQL and Semgrep…". "Make it accessible" → "WCAG 2.2 Level AA." "Make it modular" → "Don't mix code with data or content; future Payload CMS."
- **Inventing a design from scratch when a design system exists.** Always check.
- **Hard-coding strings or data inside components.** Pull them out. The repository pattern and the strings module exist for a reason.
- **Skipping verification.** A green CI badge is not a working app.
- **Trusting hallucinated facts.** Double-check opening hours and coordinates against the §4 sources.
- **Disabling tests to ship.** Fix the code — never weaken the workflow.

---

## 5. The In-Class Workflow

### Before class

1. Open Claude Code in your terminal or IDE.
2. Have a Vercel account ready (sign in with GitHub).
3. Have SSH set up (`ssh -T git@github.com` should succeed).
4. Skim the [TpGroup Design System](https://design.tpgroupsl.com/) homepage and the [FambulTik home template](https://design.tpgroupsl.com/templates/fambultik-home).
5. (Optional, for Phase 2) Have a Supabase account.

### In class — Phase 1

1. **Open `SPEC.md`** and skim §1–§5 (the architecture), §8 (brand), §10 (a11y). This is the brief.
2. **Start Claude Code** in an empty directory.
3. **Paste this prompt:**

   ```text
   Read SPEC.md in this directory. Execute Phase 1 (sections §19, phases 1–4)
   end to end. Enforce the three-layer separation in §5 — no English literals
   in components, no attraction facts outside src/data/attractions.json. Mirror
   the TpGroup Design System (§8) and conform to WCAG 2.2 Level AA (§10).
   Commit after each phase. The git remote is
   git@github.com:click2tman/ai-led-sdlc-demo.git — push to that. Stop and ask
   before deviating from §5 (architecture), §6.1 (type), §8 (brand), §10
   (a11y), or §12 (structure). Begin.
   ```

4. **Watch.** When Claude asks for clarification, answer briefly. When it commits, glance at the diff.
5. **Spot-check the separation early.** After the first UI commit, run `grep -rn '"Sign in"\|"Home"\|"Schedule a Tour"' src/components src/pages src/lib`. If anything matches, push back: "Move those literals to `src/content/strings.en.json`."
6. **Around minute 35**, open Vercel, import the GitHub repo, set Framework Preset = Vite, click Deploy.
7. **At minute 42**, open the live URL on your phone. Verify the FambulTik logo, the disclaimer, the responsive grid, keyboard focus rings, and Get Directions.

### In class — Phase 2 (if time permits)

8. Provision Supabase (Vercel integration or directly).
9. Paste this prompt:

   ```text
   Read SPEC.md. Execute Phases 5–7. Use the Supabase URL and anon key in
   .env.local (already set). Keep the three-layer separation: bookmarks and
   bookings logic in src/lib, no strings in components. Maintain WCAG 2.2 AA.
   Commit after each phase. Begin.
   ```

10. Smoke-test: sign up → bookmark → schedule → view `/account` → cancel → sign out.
11. Verify RLS with a second account.

### Phase 2.5 (optional, demonstrates the repository swap)

12. ```text
    Read SPEC.md §5.3 and the Phase 2.5 workflow in §19. Add the
    public.attractions table with public-read RLS. Implement
    attractions.supabase.ts. Write the migration script
    scripts/migrate-attractions-to-supabase.ts and run it. Then set
    VITE_ATTRACTIONS_SOURCE=supabase locally and verify the app renders
    identically — no component changes allowed.
    ```

### After class

- Update the live URL in `README.md`.
- Re-enable "Confirm email" in Supabase for production.
- Run Lighthouse on the live URL.
- One full keyboard-only walkthrough and one screen-reader pass (VoiceOver or NVDA).
- Verify the separation: `grep -rn '"[A-Z][a-z]' src/components src/pages | wc -l` — should return zero matches for user-facing strings.

---

## 6. Your Turn — Build Your Own Spec

Take the **seven-prompt pattern** and apply it to a domain of your choice.

| Topic                                | Why it's a good first project                                    |
| ------------------------------------ | ---------------------------------------------------------------- |
| Freetown restaurant guide            | Same data shape, different content.                              |
| Sierra Leone university directory    | Stronger SEO/GEO impact; fits TpLEARN brand.                     |
| Local farmers' market locator        | Geo-heavy, real map integration.                                 |
| Cultural events calendar             | Adds a time dimension.                                           |
| African football clubs encyclopedia  | Heavy entity relationships — perfect for JSON-LD practice.       |

### Template prompts to adapt

```text
PROMPT 1 — Frame
I'm building a [type of app] for [audience]. It should help them [primary
goal]. Constraints: deliverable in [time], deployed to [platform], code
hosted on [GitHub repo URL]. Generate a SPEC.md that includes scope, tech
stack, data model with seed data, pages and routes, acceptance criteria,
and a phased delivery workflow.

PROMPT 2 — Stack and sources
Use [framework choice]. Source content from the following authoritative
sites: [list of URLs]. The spec should require paraphrasing, not copying,
and every entity must cite at least one source.

PROMPT 3 — Features and backend
Add [feature 1], [feature 2], [feature 3]. Use [database/backend] hosted
on [platform]. Include the schema, RLS or equivalent, and the auth flow.

PROMPT 4 — Productionise
The repo is at [git URL]. Publisher is [company]. Add a [disclaimer/purpose
statement]. Requirements: mobile-responsive, SEO and GEO, JSON-LD entity
relationships, SAST testing on GitHub Actions.

PROMPT 5 — README
Create a README for the repo.

PROMPT 6 — Design system, brand, accessibility
Use [design system URL] to inform the UI. Follow the [brand name] brand
guide and use its logo. Make sure the app is fully accessible and
complies with WCAG 2.2 Level AA.

PROMPT 7 — Code/data/content separation
Don't hard-code datasets or strings. Externalise data to [JSON files / CSV
files / database] and externalise all UI copy to [content directory /
i18n files]. I want students to follow industry best practice. Follow-on
work will be [destination — e.g. Payload CMS / Sanity / Contentful],
where all content, strings, labels, etc., will eventually live.
```

### Exercise

Pick one of the topics. Run the seven prompts. Compare your output with `SPEC.md`. Notice:

- Where Claude made different defaults than for this project.
- Which prompts you had to extend with an eighth or ninth follow-up.
- Whether the agent flagged scope concerns.
- Whether the design system reference produced a more coherent UI than free-form.
- **Whether Prompt 7 changed the architecture meaningfully** — it should.

Bring your `SPEC.md` to the next session.

---

## 7. Reference Materials

- [`SPEC.md`](./SPEC.md) — the project specification.
- [`README.md`](./README.md) — the repo front door.
- [TpGroup Design System](https://design.tpgroupsl.com/)
  - [FambulTik home template](https://design.tpgroupsl.com/templates/fambultik-home)
  - [Logo usage](https://design.tpgroupsl.com/foundations/logo-usage)
  - [Colours](https://design.tpgroupsl.com/foundations/colors)
  - [Accessibility foundation](https://design.tpgroupsl.com/foundations/accessibility)
- [WCAG 2.2 specification](https://www.w3.org/TR/WCAG22/)
- [WCAG 2.2 quick reference](https://www.w3.org/WAI/WCAG22/quickref/)
- [Payload CMS docs](https://payloadcms.com/docs)
- [Repository pattern (Martin Fowler)](https://martinfowler.com/eaaCatalog/repository.html)
- [Claude Code documentation](https://docs.claude.com/claude-code)
- [Schema.org Validator](https://validator.schema.org/)
- [Google Rich Results Test](https://search.google.com/test/rich-results)
- [llmstxt.org](https://llmstxt.org/)
- [Supabase docs — Row Level Security](https://supabase.com/docs/guides/database/postgres/row-level-security)
- [GitHub CodeQL](https://codeql.github.com/)
- [axe-core for Playwright](https://www.npmjs.com/package/@axe-core/playwright)

---

## A Final Note

The point of this class is **not** that you memorise seven prompts. The point is that you internalise a workflow:

1. Frame.
2. Patch.
3. Productionise.
4. Style and brand.
5. **Separate.** Code, data, and content live in different folders for different reasons.
6. Verify.
7. Ship.

Specs first. Code second. Brand on a real system. Accessibility as a hard standard. **Architecture that survives the next storage decision.** Verification always.

That is the AI-led SDLC.

— TpGroup (SL) Limited
