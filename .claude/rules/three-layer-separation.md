---
description: The keystone architectural rule for Salone Explorer. Every file belongs to exactly one of three layers - code, data, content. Loaded every session; binding on every agent. Derived from SPEC.md section 5 and CLAUDE.md.
---

# Rule: three-layer separation (code / data / content)

This is the rule most likely to be violated by an AI agent and the one
that causes the most damage. It comes from `SPEC.md` section 5 and the
project `CLAUDE.md`.

## The three layers

| Layer   | Path                                        | Holds                                                                      |
| ------- | ------------------------------------------- | -------------------------------------------------------------------------- |
| Code    | `src/components/`, `src/pages/`, `src/lib/` | React components, route handlers, business logic. No strings. No facts.     |
| Data    | `src/data/*.json`                           | Attraction records, region lookups, taxonomies.                            |
| Content | `src/content/*.json`                        | All user-facing strings, page copy, microcopy, the disclaimer.             |

## Hard rule - no exceptions

If you are about to type an English string (`"Schedule a Tour"`) or an
attraction fact (`"Tiwai Island"`, `8.4831`, opening hours) inside a
`.tsx` or `.ts` file, **stop**.

- The string goes in `src/content/strings.en.json` and is read via
  `t("namespace.key")`.
- The fact goes in `src/data/attractions.json` and is read through the
  `attractions` repository.

The only places literals are allowed: tests, `src/data/`, and
`src/content/` themselves.

## Verification

The app lives in the `salone-explorer/` subdirectory (SPEC §12), kept
separate from the `.claude/` harness so the Vercel build excludes the
tooling. All `src/...` paths in this rule are relative to that app dir.

A grep for hard-coded English strings or known attraction names anywhere
under `src/components/`, `src/pages/`, or `src/lib/` (excluding
`src/lib/content/`) must return zero matches. Run it from
`salone-explorer/` (or target `salone-explorer/src/...` from the repo
root) — a grep pointed at a non-existent path returns zero and would
mask a real leak. The `code-reviewer` and `security-reviewer` agents run
this check; `verification-loop` runs it before `/handoff`.

## Repository pattern for all data access

Components and pages must never import `attractions.json` directly. They
consume `attractions` from the barrel module `src/lib/content/index.ts`.
The barrel picks the implementation based on `VITE_ATTRACTIONS_SOURCE`:

- `file` (default, Phase 1) - `fileAttractionRepository` reads JSON.
- `supabase` (Phase 2.5) - `supabaseAttractionRepository` reads Postgres.
- `payload` (Phase 8, future) - to be added.

When adding any new domain type: define the interface first, add the
file-based implementation, then optionally the Supabase one. Never bypass
the repository to "just read the JSON".

## Strings indirection

`src/lib/content/strings.ts` exports `t(key)`. All copy flows through it.
Strings never contain HTML - compose rich text in components from
multiple keys.

## Why this rule exists

It is the bridge to Phase 8 (Payload CMS). Code that reads facts through
a repository and copy through `t()` swaps its backing store without a
rewrite. Code that hard-codes facts and strings has to be rebuilt. The
separation is the entire point of the architecture; do not erode it for
convenience.

## Cross-references

- `SPEC.md` section 5 (architecture), section 6.1 (`Attraction` type)
- `api-conventions.md` - repository and contract conventions
- `engineering-principles.md` - the broader non-negotiables
