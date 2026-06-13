<!--
  GENERATED FILE - do not edit by hand.
  Source: per-tool preamble + CLAUDE.md + .claude/rules/*.md
  Regenerate: .claude/scripts/gen-agent-memory.sh
-->

# GEMINI.md - Gemini CLI working agreement for Salone Explorer

You are Gemini CLI. This file is your project memory: the Gemini CLI counterpart
of CLAUDE.md. The governance in this repo is identical for every assistant
that touches it; only the *enforcement mechanics* differ by tool. Read this
preamble first - it tells you which parts of the Claude Code-oriented
content below actually apply to you.

## What is mechanically enforced for you

Commits you author pass through versioned git hooks (`.githooks/`,
activated via `core.hooksPath`). They run for any tool and block on
failure:

- `commit-msg` - every commit message needs a
  `Requirement:`/`Phase:`/`Incident:` traceability trailer.
- `pre-commit` - secret scan on staged files, a one-line purpose header on
  each new source file, and the three-layer separation grep over
  `salone-explorer/src`.

Activate them once per clone:

    .claude/scripts/install-git-hooks.sh

## What does NOT apply to you

The `.claude/` harness is Claude Code-native. Its slash commands
(`/session-start`, `/orchestrate`, `/handoff`, ...), `settings.json`
hooks, skills, subagents, output styles, and statusline DO NOT run under
Gemini CLI. Where the rules and CLAUDE.md below reference those mechanisms,
treat them as background and use the manual equivalent:

- No `/session-start` automation: if you do long-running work, record
  intent and outcomes in `.claude/sessions/` by hand following the
  existing file format.
- No prompt-level spec-first gate: satisfy spec-first at commit time via
  the trailer (enforced by `commit-msg` above) - reference a SPEC phase /
  section, a GitHub issue, or an incident.
- No automated `reset --hard` / `push --force` block: the git hooks
  cannot stop these, so the discipline is on you. Do not run them; do not
  bypass the hooks.
- No automated reviewer agents: request human review before merge. Gemini CLI
  never merges to `main`.

## Binding rules

The rules below (from `.claude/rules/`) are binding and tool-neutral.

<!-- source: .claude/rules/80-20-split.md -->

---
description: The contract that defines what AI does (80 percent) and what humans do (20 percent) on Salone Explorer. Loaded for every session.
---

# Rule: the 80 / 20 split

This rule encodes the AI-led operating model. It applies repo-wide.

## What AI does (the 80 percent)

- Read SPEC.md, the GitHub issue, and any linked artefacts.
- Produce the context pack (`/orchestrate`).
- Write the implementation plan and wait for approval (`plan-then-code`).
- Implement the plan: code, data, content, tests, docs - respecting the
  three-layer separation.
- Run the verification loop: lint, typecheck, unit tests, a11y smoke,
  secret scan, build.
- Spawn `code-reviewer` and `security-reviewer` for first-pass review.
- Update README, in-code headers, ADRs as required.
- Open the draft PR with a complete description (`/handoff`).

## What humans do (the 20 percent)

- Approve the plan before implementation begins.
- Sign off on architecture decisions (ADRs) and any SPEC deviation.
- Review the draft PR and apply judgement.
- Resolve ambiguous requirements.
- Final security and business-logic sign-off.
- Click merge. (Claude is denied this action by `settings.json`.)

## Hard boundaries (enforced by hooks and settings)

- Claude must not run `gh pr merge`.
- Claude must not `git push --force` or `git reset --hard`.
- Claude must not bypass hooks (`--no-verify`).
- Claude must not introduce secrets; the secret scanner blocks the
  commit.
- Claude must not deviate from SPEC.md section 5, 6.1, 6.3, 8, 10, or 12
  without stopping to ask.

## What this rule is NOT

This is not a model of what Claude is *capable* of - Claude can do the
20 percent. It is a *responsibility* model: the human is the accountable
party for those steps. Routing them through a human is what makes the
program AI-Led, not AI-only.

---

<!-- source: .claude/rules/api-conventions.md -->

---
description: Contract conventions for Salone Explorer. Path-scoped - applies when editing the repository barrel, domain types, content keys, or the Supabase schema. A contract is anything another layer or module depends on.
paths:
  - "**/src/lib/content/**"
  - "**/src/data/**"
  - "**/src/content/**"
  - "**/supabase/**"
  - "**/*.schema.json"
  - "**/schema.sql"
---

# Rule: contract conventions

A contract is anything another layer or module depends on: the
`Attraction` type, the repository interface, the content string keys, the
Supabase schema. Treat changes here with care - they ripple.

## The repository contract

- Components and pages consume `attractions` from the barrel
  `src/lib/content/index.ts`. They never import `src/data/*.json`.
- The barrel selects the implementation from `VITE_ATTRACTIONS_SOURCE`:
  `file` (default), `supabase` (Phase 2.5), `payload` (Phase 8).
- Adding a new domain type: **define the interface first**, then the
  file-based implementation, then optionally Supabase. Never bypass the
  repository.
- The `Attraction` type in `src/lib/content/types.ts` is canonical and
  matches `SPEC.md` section 6.1. Do not diverge from it without an ADR.

## The content contract

- All user-facing copy lives in `src/content/strings.en.json` and is
  read via `t("namespace.key")` from `src/lib/content/strings.ts`.
- Keys are dot-namespaced: `home.hero.heading`, `cta.scheduleTour`.
- Strings never contain HTML. Compose rich text from multiple keys in
  the component.
- Renaming a key: add the new key, migrate all read sites in the same
  PR, then remove the old. Never rename in place and leave dangling
  `t()` calls.

## The data contract

- `src/data/attractions.json` records match the `Attraction` type
  exactly. Schema-validated.
- Do not invent facts. Paraphrase from the five sources in SPEC.md
  section 4. Unconfirmed hours -> `hours.notes: "Hours vary - confirm
  locally"`.

## The Supabase contract (Phase 2+)

- `supabase/schema.sql` is canonical and matches `SPEC.md` section 6.3.
- Every user-scoped table (`profiles`, `saved_attractions`,
  `tour_bookings`) has RLS enabled with `auth.uid() = user_id` policies.
- **Never add a user-scoped table without an RLS policy in the same
  migration.** Never disable RLS.
- Schema changes require an ADR and a migration; they do not edit data
  in place.

## Routes

- Route paths are kebab-case nouns: `/attractions`,
  `/attractions/:slug`, `/about`, `/signin`, `/signup`, `/account`.
- No verbs in route paths.

## Forbidden

- Importing `src/data/*.json` directly from a component or page.
- Inlining a user-facing string instead of using `t()`.
- Renaming a type field or content key in place without migrating all
  consumers in the same PR.
- Adding a user-scoped Supabase table without an RLS policy.
- Diverging the `Attraction` type or Supabase schema from SPEC.md
  without an ADR.

---

<!-- source: .claude/rules/branch-conventions.md -->

---
description: Branch model and lifecycle for Salone Explorer. Simple two-branch model - feature branches from dev, promote dev to main behind the four CI gates. Hotfix from main. Loaded every session.
---

# Rule: branch conventions

## The two long-lived branches

| Branch | Purpose                                                            | Protection                                   |
| ------ | ----------------------------------------------------------------- | -------------------------------------------- |
| `dev`  | Integration trunk. All feature work merges here first.            | CI must be green                             |
| `main` | Production. Deployed to Vercel. Tagged for release.               | `ci.yml`, `codeql.yml`, `security.yml`, `a11y.yml` all green + 1 human approval |

Promotion is one-directional: `dev -> main`. Feature work never targets
`main` directly. Hotfix is the only exception.

## Branch types

| Type      | Naming                          | Source | Target            |
| --------- | ------------------------------- | ------ | ----------------- |
| Feature   | `issue-<num>-<slug>`            | `dev`  | `dev`             |
| Bugfix    | `fix-<num>-<slug>`              | `dev`  | `dev`             |
| Chore     | `chore-<slug>`                  | `dev`  | `dev`             |
| Promotion | `promote-dev-to-main-<date>`    | `dev`  | `main`            |
| Hotfix    | `hotfix-<num>-<slug>`           | `main` | `main` (then back-merge to dev) |

`<slug>` is lowercase-kebab-case, derived from the issue/phase title,
max 40 chars. For phase work without an issue, use a descriptive slug:
`phase-3-accessibility`, `phase-5-supabase-schema`.

## Feature lifecycle

```
1. git fetch origin
2. git checkout -b issue-<num>-<slug> origin/dev          (always from dev)
3. Commit small, push often. /code-push enforces conventions.
4. verification-loop green; /handoff opens a draft PR -> dev
5. CI green + 1 human approval
6. Squash-merge to dev (human action)
7. Delete the branch on merge
```

## Promotion lifecycle (dev -> main)

Promotions move accumulated dev work to production.

```
git fetch origin
git checkout -b promote-dev-to-main-2026-06-05 origin/dev
/handoff      # opens the promotion PR dev -> main
```

The promotion PR must have all four CI workflows green before merge:

- `ci.yml`        - lint, typecheck, unit tests, build
- `codeql.yml`    - static analysis
- `security.yml`  - SAST / secret scan
- `a11y.yml`      - Playwright + axe on `/`, `/attractions/tiwai-island`,
                    `/about`, `/signin`, `/signup`; fails on serious or
                    critical violations

After merge to main, Vercel deploys automatically. Tag main `vN.N.N`.

## Hotfix lifecycle

The only path that bypasses dev. Use only when production has a defect
that cannot wait.

```
1. git fetch origin
2. git checkout -b hotfix-<num>-<slug> origin/main
3. Smallest viable diff. No drive-by changes.
4. /code-push, /handoff opens the hotfix PR -> main.
5. CI green + 1 human approval.
6. Merge to main; tag vN.N.N+1.
7. Back-merge to dev so history stays aligned.
8. Open a follow-up issue to add a regression test if not already added.
```

Hotfix work references a `docs/incidents/<id>.md` entry (spec-first rule
still applies; incidents count as a source).

## What is forbidden

- Branching from a stale source. Always `git fetch` first.
- Branching from another feature branch.
- Reusing a branch name across issues.
- Working on `dev` or `main` directly.
- Force-pushing `dev` or `main` (denied by hook and branch protection).
- Creating a feature branch from `main` (hotfix is the only exception).
- Merging a hotfix without back-merging to dev.

## Cross-references

- `commit-conventions.md` - message format + required trailers
- `spec-first.md` - every change traces to SPEC.md
- `CLAUDE.md` - the four CI workflows required to merge to main

---

<!-- source: .claude/rules/commit-conventions.md -->

---
description: Commit message conventions. Applies to every commit in the repository.
---

# Rule: commit conventions

## Format

```
<type>: <imperative summary, max 72 chars>

<wrapped body, lines max 72 chars, optional>

<trailers>
```

## Types

- `feat:`     a new user-visible capability
- `fix:`      a bug fix
- `chore:`    maintenance with no user-visible behaviour change
- `docs:`     documentation-only
- `test:`     test-only
- `refactor:` internal restructuring with no behaviour change
- `perf:`     performance improvement
- `build:`    build / dependency / tooling change
- `ci:`       CI configuration

## Trailers

Required on every commit (one of the traceability trailers):
- `Requirement: <ref>` - references a SPEC phase/section or a durable
  requirement id. Examples:
  `Requirement: SPEC Phase 3 - accessibility`,
  `Requirement: SPEC section 6.1 - Attraction type`,
  `Requirement: STORY-0042-tour-booking`.
- `Phase: <n>` - shorthand for SPEC.md phase n.
- `Incident: <id>` - hotfix only.

Enforced by `/code-push` and the `pre-tool-bash` hook.

Issue linkage (when an issue exists):
- `Refs: #<num>` for in-progress work, OR
- `Closes: #<num>` only on the commit that finishes the issue

Forbidden:
- `Co-Authored-By: Claude ...` or any AI signature
- Emoji or icons anywhere in the message

## Examples

```
feat: add attractions repository with file-based implementation

Defines the AttractionRepository interface and the file-backed
implementation that reads src/data/attractions.json. The barrel in
src/lib/content/index.ts selects it when VITE_ATTRACTIONS_SOURCE=file.

Requirement: SPEC section 5.2 - file-based repository
Refs: #12
```

```
fix: move hard-coded "Schedule a Tour" label into content layer

The CTA string was inlined in TourCard.tsx, violating the three-layer
rule. Moved to src/content/strings.en.json and read via t().

Requirement: SPEC section 5 - three-layer separation
Closes: #31
```

```
feat: enable RLS on saved_attractions with auth.uid policy

Phase: 5
Refs: #40
```

---

<!-- source: .claude/rules/engineering-principles.md -->

---
description: The canonical engineering principles for Salone Explorer. Loaded for every session; binding on every agent and human contributor. Adapted to this stack (React, Vite, TypeScript, Supabase, Tailwind, Playwright). Path-scoped rules (commit, branch, test, api) extend; this file does not duplicate them.
---

# Rule: engineering principles

The non-negotiables. Read in conjunction with `three-layer-separation.md`,
`commit-conventions.md`, `branch-conventions.md`, `test-conventions.md`,
`api-conventions.md`, and `spec-first.md` (each covers its area; this file
does not repeat them).

## 1. Architectural mindset

- **Plan before code.** For any change beyond a one-line edit, run
  `plan-then-code`; produce a plan and get approval before
  implementation. Justify the architectural decision before writing.
- **Architecture over quick fixes.** Choose the right shape, not the
  fast one. Quick fixes that defer cost are technical debt; do not
  ship them.
- **Design for clarity and correctness first**, performance second,
  cleverness never.
- **Highly performant, highly available, highly secure.** Treat each
  as a first-class non-functional requirement, not an afterthought.
- **Security up-front.** Think through OWASP top-10 and stack-specific
  vulnerabilities (XSS, open-redirect, missing auth, Supabase RLS gaps,
  exposed `VITE_` secrets) BEFORE writing the code, not after.
- **No silent fallbacks** that mask errors. Errors raise loudly with
  context.
- **Validate explicitly at boundaries** (route params, form input, env
  var, Supabase response, repository return).
- **Fail fast** with clear, actionable messages including the failing
  input and the expected shape.
- **No magic values, no hardcoded defaults.** Constants in a named
  config or token; environment-specific values via `VITE_` env vars.
- **No duplicate code, files, or folders** in nested trees. Reuse via
  modules and shared lib functions.

## 2. Stack-idiomatic style

Use the paradigms native to the tool. Do not import paradigms across
stacks.

| Stack                         | Idioms                                                                                  |
| ----------------------------- | --------------------------------------------------------------------------------------- |
| TypeScript / React            | Strict mode, no `any`, function components + hooks, Zod (or equivalent) at every boundary, repository pattern for data access |
| JSON (data + content layers)  | Schema-validated, sorted keys where order is non-significant, no comments, no logic     |
| Tailwind / CSS                | Visuals derive from `src/styles/tokens.css` (TpGroup design tokens); no magic colours   |
| Supabase / SQL                | RLS enabled on every user-scoped table, `auth.uid() = user_id` policies, migrations in `supabase/schema.sql` |
| Bash (hooks, scripts)         | `set -euo pipefail`, ShellCheck clean, no `eval` on tainted input                       |

## 3. Planning and scope

- **Ask for clarification** whenever any instruction or requirement is
  ambiguous. Do not guess. Stop and ask before deviating from SPEC.md
  section 5 (architecture), 6.1 (`Attraction` type), 6.3 (Supabase
  schema), 8 (brand), 10 (a11y), or 12 (project structure).
- **Suggest options** when there is more than one reasonable approach;
  request user input before proceeding.
- **Smallest viable diff.** Edit only what the phase/issue requires. No
  drive-by refactors.
- **Granular TODOs.** "Change the Home alert heading from h2 to h1"
  beats "fix accessibility". The granular form is testable.
- **Keep work focused and modular** to fit comfortably within the
  context window.

## 4. Code quality

- **Lint and format must be clean** before commit: ESLint (including
  `jsx-a11y` recommended) + Prettier. Errors fail the build.
- **Typecheck clean**: `tsc --noEmit` with no errors.
- **No linting errors or warnings** that would fail the quality gate.
- **Do not** `eslint-disable` a `jsx-a11y` rule to make a build pass.
- **Be succinct and concise** in code, docs, and conversation.
- **Never disable** a feature, assertion, lint rule, or check solely to
  make a test or build pass. Fix the root cause.

## 5. Documentation (in-code)

- **File-purpose comment** on every new source file - one line at the
  top. The `pre-tool-edit` hook enforces this.
- **Conceptual overview** at the top of each non-trivial file: a brief
  JSDoc `@file` block describing purpose and any non-obvious design.
- **Function documentation** in TSDoc / JSDoc on every exported symbol.
- **Inline comments** explain tricky logic, edge cases, or non-obvious
  reasoning. Hard-wrap at 80 characters.

## 6. Public-API documentation

A contract is anything another module or layer depends on. See
`api-conventions.md`. Key surfaces here:

| Surface                              | Where it lives                                  |
| ------------------------------------ | ----------------------------------------------- |
| Attraction domain type               | `src/lib/content/types.ts` (canonical)          |
| Repository interface                 | `src/lib/content/index.ts` (barrel)             |
| Supabase schema                      | `supabase/schema.sql` (matches SPEC 6.3)        |
| Content string keys                  | `src/content/strings.en.json` (read via `t()`)  |

## 7. Documentation (project-level)

- **README** kept current with public-facing project shape.
- **General documentation** as `.md` files in `docs/`.
- **Conversation log** in `docs/scratch-pad/`; per-session updates land
  in `.claude/sessions/<id>.md`.
- **ADRs** for cross-cutting decisions in `docs/adr/`.
- **Dev guide** for the harness in `docs/dev-guide/`.

## 8. Output formatting

- **Plain text only** in code, documentation, and commit messages.
- **No emojis or icons** anywhere in code, docs, or commits.
- **Lowercase kebab-case** for all filenames.
- **Before commit**, scan code and docs for emojis or icons and remove.

## 9. Repository hygiene

- **Keep the root clean.** Only files that must live at root belong
  there (README, SPEC.md, package.json, vite/ts config, .gitignore).
- **Tests live in `tests/`** per `test-conventions.md`; never beside the
  unit under test.
- **No duplicate code, files, or folders.** Consolidate before adding.

## 10. Testing

- **Write tests** for new behaviour. Run them green before commit.
- **Never disable** an assertion, skip a test, or weaken a check to make
  CI green. Fix the underlying issue.
- **Run `test:a11y`** (Playwright + axe) - the a11y CI gate fails on
  serious or critical violations on the five smoke routes.
- **Run the verification loop** (`verification-loop` skill) before every
  `/handoff`.

## 11. Version control and commits

- **Commit messages**: conventional, imperative, max 72 chars first
  line, plain text. Full rule in `commit-conventions.md`.
- **No emojis or icons** in commit messages.
- **No AI signatures** (`Co-Authored-By: Claude ...`) in commit messages.
- **Do not skip hooks** (`--no-verify` is forbidden; the hook blocks it).
- **Branch naming** per `branch-conventions.md`.

## 12. Workflow discipline

- **Sessions are mandatory** (`/session-start`, `/session-update`,
  `/session-end`).
- **SPEC.md is the source of truth** (`spec-first.md`).
- **Plan before code** for non-trivial work (`plan-then-code`).
- **Smallest viable diff** - no drive-by refactors.
- **Verify before handoff** (`verification-loop`).

## 13. Security and secrets

- **No secrets in client code.** Only `VITE_`-prefixed env vars are
  exposed to the browser. The Supabase service-role key never reaches
  the client.
- **Never disable RLS** or weaken CI to make a build pass.
- **The disclaimer ships in three places**: Home alert, footer,
  `/about`. Do not ship without all three.
- **Do not invent attraction facts.** Paraphrase from the five sources
  in SPEC.md section 4. When a fact is unconfirmed, set
  `hours.notes: "Hours vary - confirm locally"`.

## 14. Hard rules (enforced by hooks or settings)

These are enforced mechanically; do not assume a rule was optional:

- `gh pr merge` is denied to Claude (settings + hook).
- `git push --force` is denied (settings + hook).
- `git reset --hard` is denied (hook).
- `git commit --no-verify` is denied (hook).
- New source files without a one-line header are blocked
  (`pre-tool-edit` hook).
- Commits with secrets are blocked (`scan-secrets.sh` via pre-tool-bash).
- Commits without a `Requirement:`/`Phase:`/`Incident:` trailer are
  blocked (pre-tool-bash hook).
- Prompts with no SPEC/issue reference are blocked (user-prompt-submit).
- Sessions left open at terminal close trigger a stderr nag (Stop hook).

## How rules interact with skills and agents

- Every agent loads the `.claude/rules/` set at session start.
- Skills assume these rules; they do not re-state them.
- When a skill conflicts with a rule, the rule wins. If the skill is
  right and the rule is wrong, raise it as an open question and update
  the rule via PR rather than ignoring it ad hoc.
- When a rule conflicts with `SPEC.md`, SPEC.md wins - it is the single
  source of truth. Raise the discrepancy and update the rule.

---

<!-- source: .claude/rules/spec-first.md -->

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

---

<!-- source: .claude/rules/test-conventions.md -->

---
description: Test file conventions. Path-scoped - applies when editing test files. Stack is Vitest (unit) + Playwright with axe-core (e2e/a11y).
paths:
  - "**/tests/**"
  - "**/*.test.ts"
  - "**/*.test.tsx"
  - "**/*.spec.ts"
  - "**/*.spec.tsx"
---

# Rule: test conventions

## Location

- Unit (Vitest):       `tests/unit/` or co-located `*.test.ts(x)` per the
  scaffold convention chosen in Phase 1 - pick one and keep it.
- E2E + a11y (Playwright): `tests/a11y/` and `tests/e2e/`.

Tests never sit beside production code unless the Phase 1 scaffold
explicitly adopts co-location. Default to `tests/`.

## Naming

- File mirrors the unit under test:
  - `src/lib/content/file-attraction-repository.ts`
    -> `tests/unit/lib/content/file-attraction-repository.test.ts`
- Test name describes behaviour in plain English:
  - good: `it("returns an empty list when no attractions match the region")`
  - bad:  `it("calls filterByRegion")`

## Authoring rules

- One behaviour per test. If you need many assertions, that is multiple
  tests.
- No mocks for systems running locally. A Phase 2 integration test hits
  the real local Supabase instance.
- No `skip` / `xit` / `test.skip` without a tracking issue and a TODO
  with the issue link.
- Test data lives in `tests/fixtures/`, not inline.
- Snapshot tests are a last resort. Prefer assertion on shape.

## Forbidden

- Editing a test to make a failing test pass.
- Weakening an assertion to make CI green.
- `eslint-disable`-ing a `jsx-a11y` rule in a component to dodge an a11y
  test.
- Removing a test because it is "flaky" without filing an issue first.

## Accessibility tests are not optional

The a11y CI gate (`a11y.yml`) runs Playwright + `@axe-core/playwright`
across five routes: `/`, `/attractions/tiwai-island`, `/about`,
`/signin`, `/signup`. It fails on serious or critical violations. Every
new route or interactive component adds or extends an a11y smoke test.

## Test generation structure (phases)

When authoring a suite from acceptance criteria, cover these in order:

| Phase | Type          | Notes                                                     |
| ----- | ------------- | --------------------------------------------------------- |
| 1     | Happy path    | Nominal success; one per acceptance criterion             |
| 2     | Negative      | Wrong input, missing required field, unauthenticated      |
| 3     | Boundary      | Empty list, min/max length, missing optional fields       |
| 4     | State / flow  | Repository source toggle, auth state transitions          |
| 5     | Integration   | Real Supabase (Phase 2+); RLS denies cross-user reads     |
| 6     | Regression    | Guards an existing behaviour touched by the change        |
| 7     | Accessibility | WCAG 2.2 AA: keyboard, focus, contrast, labels (axe)      |
| 8     | Security      | XSS probe in user input, RLS enforcement, no exposed keys |

### Rules

- Never default a test result to "passed". The assertion must observe a
  positive signal.
- Phase 7 (a11y) and Phase 8 (security) are mandatory - at least one
  each per feature, even if the acceptance criteria do not name them.
- Phase 5 (integration) hits real dependencies in the test environment;
  mocks are not accepted there.

---

<!-- source: .claude/rules/three-layer-separation.md -->

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

---

## Project reference (shared with Claude Code)

The full project guide follows. It is written for Claude Code, but the
architecture, the three-layer rule, the repository pattern, the branding
constants, and the post-scaffold commands apply to you unchanged. Only the
"AI harness (.claude/)" and activation sections are Claude Code-only - see
"What does NOT apply to you" above.

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository state

This directory currently contains only specification artefacts — no application code has been scaffolded yet:

- `SPEC.md` — the single source of truth. Read it before generating any code. It is authoritative over this file when they disagree.
- `README.md` — the public-facing project front door. Mirrors `SPEC.md` at a higher level.
- `STUDENT_GUIDE.md` — teaching narrative documenting how `SPEC.md` was authored. Not a build artefact; do not generate code from it.

The project target is **Salone Explorer**, a Sierra Leone tour-guide SPA published by TpGroup (SL) Limited under the **FambulTik** brand. Target GitHub remote: `git@github.com:tamba-lamin-tpgroup/ai-led-sdlc-demo.git`. Target deploy: Vercel (Vite preset).

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
- **Activation** (one-time, human-only): move `.claude/settings.json.proposed`
  to `.claude/settings.json` and copy `settings.local.json.template` to
  `settings.local.json`, then restart Claude Code.

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

Before touching auth or any user-scoped feature, Supabase must be provisioned and `supabase/schema.sql` (from `SPEC.md` §6.3) applied. Every user-scoped table — `profiles`, `saved_attractions`, `tour_bookings` — has RLS enabled with `auth.uid() = user_id` policies. Never add a new user-scoped table without an RLS policy in the same migration.

## Branding constants

- Publisher: TpGroup (SL) Limited.
- Brand: FambulTik (Krio: *family stick*).
- Design system: [design.tpgroupsl.com](https://design.tpgroupsl.com/). All component visuals derive from tokens in `src/styles/tokens.css` (see `SPEC.md` §8.4 for the full token table). Tailwind reads them as CSS variables.
- Logo assets live in `src/assets/brand/fambultik/`.
