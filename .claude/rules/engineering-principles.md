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
