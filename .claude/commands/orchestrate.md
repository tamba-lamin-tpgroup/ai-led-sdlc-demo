---
description: Turn a GitHub issue into routed, scoped, context-packed work. Runs the spec-first four-check pre-flight, writes a context pack, classifies the layer(s) touched, and dispatches an engineer (or the architect for cross-layer work). Claude never merges.
argument-hint: "<github-issue-url-or-shortform>"
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, Agent
---

# /orchestrate

Entry point for AI-Led work. Routes an issue to the right layer with a
context pack. Single git repo.

## Procedure

1. **Parse `$ARGUMENTS`.** Accept either:
   - `https://github.com/<owner>/<repo>/issues/<num>`
   - `<owner>/<repo>#<num>`
   - bare `#<num>` (resolved against `git config --get remote.origin.url`)

2. **PRE-FLIGHT — four mandatory checks** (per
   `.claude/rules/spec-first.md`). Block dispatch if any check fails. Do
   not proceed; do not pass to any engineer; do not open a feature
   branch.

   ### a) Traceable source exists
   - The issue references a `SPEC.md` phase (section 19) or section, or
     an approved requirement (`STORY-/FR-/NFR-/TASK-` file), or — for a
     hotfix — a `docs/incidents/<id>.md` entry.
   - **If missing** -> spawn the `product-analyst` agent to draft the
     spec detail / acceptance criteria and stop. A human approves scope;
     the analyst only drafts. Re-invoke `/orchestrate` after approval.

   ### b) Phase preconditions met
   - Confirm the phase's prerequisites hold (e.g. Phase 6 auth requires
     Phase 5 Supabase provisioning done and `supabase/schema.sql` applied
     with RLS). If not -> list blockers, post on the issue, stop.

   ### c) Dependencies satisfied
   - Any referenced prior phase/issue is done. If a blocker is not done:
     list the blockers, post on the issue, stop.

   ### d) Edge cases enumerated and correct phase sequence
   - Confirm the requirement's edge-cases section is non-empty (or
     explicitly states "no edge cases") and the work is in the correct
     phase sequence. Gaps -> spawn `product-analyst` to fill, then
     re-check.

   Only when all four pass does routing proceed.

3. **Write the context pack** to `.claude/context-packs/<issue-num>/`
   (create the directory). Include:
   - `state.md` — issue summary, the SPEC phase/section trace inline,
     acceptance criteria, and a running status table.
   - the relevant `SPEC.md` excerpts inline so subagents do not re-read
     the whole file.

4. **Classify the layer(s)** the work touches, from the issue and the
   files it will change:
   - `code` — `src/components/`, `src/pages/`, `src/lib/`
   - `data` — `src/data/*.json`
   - `content` — `src/content/*.json`
   - `infra` — CI, Vercel, `supabase/`, tooling
   - `cross-layer` — two or more of the above

5. **Dispatch**:
   - For a single-layer change: spawn the engineer (the default claude
     agent) with the context-pack contents inline and the layer noted.
   - For cross-layer or architectural work (crosses layer boundaries,
     introduces a new dependency, or alters a public contract — the
     `Attraction` type, the attractions repository interface, the
     Supabase schema, an env var): invoke the `architect` agent FIRST to
     produce an ADR and a sequencing plan, then dispatch the engineer per
     that plan.
   - Track progress in `<pack>/state.md`. Do not write production code in
     this command.

6. **When the engineer(s) report back**, print the final `state.md` and
   tell the user to run `/handoff` to open the draft PR. Never
   `gh pr merge` — Claude opens PRs; humans merge them.
