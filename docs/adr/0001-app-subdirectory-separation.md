<!-- 0001-app-subdirectory-separation.md - ADR: isolate the shippable app from the AI-led SDLC harness in a subdirectory -->

# ADR 0001: Isolate the shippable app in a subdirectory, separate from the harness

- Status: Accepted
- Date: 2026-06-06
- Deciders: Project owner (TpGroup SL), Claude Code
- Traces to: SPEC.md §12 (Project Structure), §18 (Build & Run), §19 (Delivery Workflow), §16 (Environment Variables)

## Context

This repository serves two purposes at once:

1. It is the build context for the **shippable application** (Salone
   Explorer), deployed to Vercel.
2. It ships an **AI-led SDLC harness** under `.claude/` (rules, agents,
   skills, hooks, slash commands) plus authoring docs under `docs/` and
   the `SPEC.md` source of truth.

If the application were scaffolded at the repository root, the production
deployment's build context would be mixed with the tooling. The harness,
session logs, ADRs, and onboarding material are not part of the product;
they should never travel with — or be reachable from — the deployed
artefact. Keeping them out of the build also keeps the build context
smaller and removes any chance of tooling files leaking into `dist/`.

A Vite production bundle only contains modules reachable from the app's
entry point, so harness files would not end up in `dist/` by default.
The risk this ADR addresses is the **build context and repository
clarity**, not the bundle contents: an explicit, enforced boundary is
better than relying on "Vite happens not to import it."

## Decision

Scaffold the application into a **`salone-explorer/` subdirectory** of the
repository, physically separate from the harness:

```
ai-led-sdlc-demo/          # repo root: harness + docs + spec (NOT deployed)
├── .github/workflows/      # CI at repo root; jobs use working-directory: salone-explorer
├── .claude/                # AI-led SDLC harness
├── docs/                   # documentation, including this ADR
├── SPEC.md  README.md
└── salone-explorer/        # the Vite app — Vercel Root Directory
    ├── package.json  vite.config.ts  tsconfig.json
    └── src/{components,pages,lib,data,content,...}
```

- **Vercel Root Directory = `salone-explorer`.** Vercel clones the repo
  but builds only from that folder, so `.claude/`, `docs/`, and the spec
  are excluded from the deployment by construction.
- **App commands run from the app dir** (`cd salone-explorer`).
- **GitHub Actions workflows stay at the repo root** (`.github/` cannot
  live in a subfolder) and run with
  `defaults.run.working-directory: salone-explorer`. Dependabot points at
  `salone-explorer/package.json`.
- **Path convention:** `src/...` paths in `CLAUDE.md` and the rules are
  relative to `salone-explorer/`. Harness checks that execute from the
  repo root (the three-layer grep in `verification-loop`, the
  `code-reviewer` diff pathspec) `cd salone-explorer` first or target
  `salone-explorer/src/...`.

The folder name `salone-explorer` is reused from SPEC §19 Phase 1 step 1
(`npm create vite@latest salone-explorer`), which already produces it —
so this ADR clarifies rather than changes the scaffold command.

## Consequences

Positive:

- The production deployment cannot contain the harness or docs.
- The app is self-contained and portable; it could be extracted to its
  own repository later with no path surgery inside it.
- The repository root reads clearly as "spec + tooling," the subfolder as
  "the product."

Negative / cost:

- One extra `cd` for every app command, and CI must set a
  `working-directory`. Both are one-line conventions, documented in
  CLAUDE.md, SPEC §18, and the `verification-loop` skill.
- Harness checks that run from the repo root must use the
  `salone-explorer/` prefix; a check pointed at a stale root-level `src/`
  would silently pass. This failure mode is called out explicitly in the
  three-layer rule and the `verification-loop` skill.

## Alternatives considered

- **App at repo root + `.vercelignore`.** Rejected: leaves the app and
  harness mixed in one tree, and `.vercelignore` is an exclusion list
  that must be maintained as the harness grows — the opposite of an
  explicit boundary. The owner's requirement was a clean separation in
  the repository, not just an ignore filter.
- **Two repositories (app and harness split).** Rejected for the teaching
  demo: the whole point is to show the harness and the app it produces in
  one place. A subdirectory gives the separation without losing that.
- **npm/turbo workspaces.** Unnecessary for a single app; adds tooling
  with no benefit until there is a second package.
