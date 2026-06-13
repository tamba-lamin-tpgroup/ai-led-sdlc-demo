---
description: Every line of code in Salone Explorer traces to SPEC.md, a tracked GitHub issue, or an approved requirement. SPEC.md is the single source of truth. The orchestrator enforces it; the product-analyst fills the gap when a spec detail is missing. Loaded every session.
---

# Rule: spec-first

No code without a traceable source. `SPEC.md` is the single source of
truth - read it before generating any code; it is authoritative over
`CLAUDE.md` and over these rules when they disagree.

## What counts as a traceable source

One of:

| Source                         | Use for                                                  |
| ------------------------------ | -------------------------------------------------------- |
| A `SPEC.md` phase (section 19) | The primary delivery path. Phases 1-8.                   |
| A `SPEC.md` section            | A specific behaviour, type, or schema (e.g. section 6.1) |
| A tracked GitHub issue         | The implementation ticket; references the SPEC section   |
| `STORY-/FR-/NFR-/TASK-` file   | Optional durable requirement in `requirements/` if used  |
| `docs/incidents/<id>.md`       | Hotfix work (incidents count as a source)                |

## The delivery phases (SPEC.md section 19)

Work proceeds phase by phase. Commit at the end of each phase.

| Phase | Scope                                                        |
| ----- | ----------------------------------------------------------- |
| 1     | Scaffold the Vite + React + TS app                          |
| 2     | Data, content, repository pattern                           |
| 3     | SEO, JSON-LD, brand, UI, accessibility                      |
| 4     | CI + deploy v1 (Vercel)                                     |
| 5     | Supabase provisioning (schema + RLS)                        |
| 6     | Auth + account (sign-in, bookmarks, favorites, bookings)   |
| 7     | Ship v2                                                     |
| 2.5   | Optional: migrate attractions JSON -> Supabase             |
| 8     | Future: Payload CMS (out of scope for class)               |

## When the rule fires

### On every `/orchestrate <issue-url>` invocation

The orchestrator pre-flight runs FOUR checks BEFORE dispatching an
engineer:

1. **Traceable source exists.** The issue references a SPEC phase /
   section or an approved requirement. If missing -> spawn
   `product-analyst` to write the spec/acceptance criteria and stop.
2. **Phase preconditions met.** Confirm the phase's prerequisites hold
   (e.g. Phase 6 auth requires Phase 5 Supabase provisioning done and
   `supabase/schema.sql` applied with RLS). If not -> list blockers,
   post on the issue, stop.
3. **Dependencies satisfied.** Any referenced prior phase/issue is done.
4. **Edge cases enumerated** and the work is in the correct phase
   sequence. If gaps -> spawn `product-analyst` to fill, then re-check.

Only when all four pass does the orchestrator route to an engineer.

### On every commit (via `/code-push` and the pre-tool-bash hook)

Every commit message carries a traceability trailer:

```
Requirement: SPEC Phase 3 - accessibility
```

or `Phase: 3`, or `Requirement: <id>`, or (hotfix) `Incident: <id>`.
`/code-push` validates this; the hook blocks commits that lack it.

### On every prompt (via the user-prompt-submit hook)

A prompt that produces code/files must reference a SPEC phase/section, a
GitHub issue, or be covered by a session linked to an issue. The hook
blocks prompts that do not.

### On every PR

The PR description references the SPEC phase/section and the issue.
`docs-writer` produces the body.

## Hard rules

- No feature branch is cut until its SPEC phase/section or requirement
  is identified.
- The `product-analyst` agent NEVER approves scope; it only drafts the
  spec detail and acceptance criteria. A human approves.
- Stop and ask before deviating from SPEC.md section 5, 6.1, 6.3, 8, 10,
  or 12 (per `CLAUDE.md`).
- Hotfix work satisfies the rule with a `docs/incidents/<id>.md` entry.

## Cross-references

- `SPEC.md` - the single source of truth (read it fully first)
- `product-analyst.md` agent - the gap-filler
- `orchestrate.md` command - runs the four-check pre-flight
- `plan-then-code.md` skill - planning template includes the source ref
- `commit-conventions.md` - the trailer format
- `branch-conventions.md` - the dev -> main model
