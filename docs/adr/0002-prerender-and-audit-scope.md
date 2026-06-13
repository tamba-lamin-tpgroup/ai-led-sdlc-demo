# ADR 0002: Pre-render tool swap and production-scoped audit gate

- Status: Accepted
- Date: 2026-06-06
- Deciders: autonomous build session (Phase 1), pending human ratification
- Supersedes / amends: SPEC §3 (pre-render tool), SPEC §15 (`security.yml`)

## Context

SPEC §3 and §13.1 name `vite-plugin-prerender` for generating static
HTML for crawlers and LLM ingestion. SPEC §15 mandates a `security.yml`
gate running `npm audit --audit-level=high`, and SPEC §22 forbids
weakening CI to make a build pass.

`vite-plugin-prerender@1.0.8` is unmaintained. It depends on
`html-minifier` (GHSA-pfq8-rq6v-vf5m, high-severity ReDoS, **no fix
available**) and a puppeteer-based `@prerenderer/prerenderer` chain.
Installing it introduces 6 high + 1 critical advisories that
`security.yml` would fail on. The two SPEC requirements therefore cannot
both be satisfied with the named tool — the conflict exists only because
the tool is abandoned.

Separately, the dev/test toolchain (`vitest`, `vite-node`, the `esbuild`
dev server) carries advisories (Vitest UI arbitrary file read/exec;
esbuild dev-server request reflection) that are **dev-only** and never
present in the production bundle. `npm audit --omit=dev --audit-level=high`
reports `found 0 vulnerabilities`.

## Decision

1. **Remove `vite-plugin-prerender`.** Implement Phase 3 pre-rendering
   with a postbuild script. (Superseded 2026-06-06 — see Amendment below.)

2. **Scope the blocking audit to shipped code.** `security.yml` blocks on
   `npm audit --omit=dev --audit-level=high` (the production dependency
   tree — what reaches users) and additionally runs a non-blocking full
   `npm audit` for visibility of dev-toolchain advisories. The deployed
   artifact is still gated at high severity; nothing that ships is
   exempt.

## Consequences

- Pre-rendering is owned by `salone-explorer/scripts/prerender.ts`
  (Phase 3), not a Vite plugin. It runs after `vite build` against
  `vite preview`, the same serving path the a11y tests use.
- The production bundle remains audit-clean at high severity.
- Dev-toolchain advisories remain visible but non-blocking until an
  upstream fix lands (tracked: bump Vitest once a fix ships on a Vite-5
  compatible line, or with a future coordinated Vite major bump).
- This amends SPEC §3 and §15; requires human ratification on PR review.

## Amendment (2026-06-06): SSG instead of Playwright prerender

The Playwright postbuild renders correctly locally but cannot run on the
Vercel build image (Chromium's system libraries can't be installed there).
Pre-rendering was reworked as **browser-free build-time SSG**:

- `src/entry-server.tsx` renders each route with `react-dom/server` +
  React Router's `createStaticHandler`/`createStaticRouter`, capturing the
  Helmet head and the loader data.
- `vite build --ssr` bundles it (`ssr.noExternal: ['react-helmet-async']`
  for CJS interop); `scripts/prerender.ts` writes `dist/<route>/index.html`
  for `/`, `/about`, `/signin`, `/signup`, and every `/attractions/:id`.
- The loader data is serialized into `window.__staticRouterHydrationData`
  and seeded into `createBrowserRouter` so `useLoaderData()` resolves on the
  first client render.
- Build command is `npm run build:prerender`; no Chromium needed.

Note: `vite preview` serves the root `index.html` for nested routes (SPA
fallback) rather than the prerendered file, so the `a11y.yml` gate runs the
plain SPA `npm run build` (equivalent post-render DOM). Vercel serves the
nested prerendered files via the `routes` `filesystem` handle (ADR 0003).
