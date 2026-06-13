---
id: 2026-06-13-1400-cross-layer-autonomous-full-app-build
layer: cross-layer
issue: #1
context_pack: none
started: 2026-06-13 14:00 EDT
ended: in-progress
author: Tamba Lamin
actor: claude-autonomous
branch: chore-vercel-hello-world
---

# Session: autonomous-full-app-build

## Overview
Build the full Salone Explorer application autonomously from Phase 1 through
Phase 7, following SPEC.md §19 delivery phases in sequence. The app lives in
`salone-explorer/` (Vercel root). Work proceeds: create `dev` branch from
`main`, then one feature branch per phase (`issue-<num>-<slug>`), committing at
the end of each phase and opening draft PRs to `dev`. Phases 1-4 deliver the
static public site; Phases 5-7 add Supabase auth. Phase 8 (Payload CMS) and
Phases 9-11 (post-class) are out of scope unless explicitly asked.

## Goals
- [ ] Create `dev` branch from `main` (branch conventions prerequisite)
- [ ] Phase 1 (#1): Install deps, Tailwind, FambulTik tokens, project structure
- [ ] Phase 2 (#2): Data types, attractions.json (8 entries), regions.json, strings.en.json, repository abstraction
- [ ] Phase 3 (#3): Routes, pages (Home, Detail, About, NotFound), components, SEO/JSON-LD, a11y
- [ ] Phase 4 (#4): CI workflows, a11y smoke tests, Vercel deploy v1
- [ ] Phase 5 (#5): Supabase provisioning, schema + RLS, supabase.ts client
- [ ] Phase 6 (#6): Auth (email/password + social), AuthProvider, ProtectedRoute, BookmarkButton, FavoriteButton, ScheduleTourModal, AccountPage
- [ ] Phase 7 (#7): Smoke test, two-account RLS check, v2 deploy

## Plan
Autonomous policy:
  - Auto-fix lint/typecheck/test failures up to 3 attempts per failure
  - Auto-commit at every green verification-loop
  - Auto-/session-update after every commit
  - Auto-spawn code-reviewer + security-reviewer before /handoff
  - Escalate to human on:
      * architectural decision required (invoke architect, then stop)
      * ambiguous requirement or missing SPEC trace
      * security finding (Medium or High)
      * breaking change to a public contract (the Attraction type,
        the attractions repository interface, the Supabase schema,
        an env var)
      * 3 consecutive failed auto-fix attempts on the same step
      * Supabase project credentials/config needed for Phase 5+

Phase sequencing: each phase runs on its own feature branch cut from `dev`.
Branch naming: issue-1-scaffold, issue-2-data-content, issue-3-ui-seo,
issue-4-ci-deploy, issue-5-supabase-schema, issue-6-auth-account,
issue-7-ship-v2.

## Updates

## Findings

## Open questions

## Outcomes

## Next session
