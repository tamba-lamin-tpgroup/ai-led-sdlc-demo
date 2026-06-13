# ADR 0003: Root-level vercel.json build shim

- Status: Accepted (maintainer-authorised)
- Date: 2026-06-06
- Amends: SPEC §12 / §19.21 (Vercel Root Directory = `salone-explorer`)

## Context

SPEC §12 deploys by setting the Vercel project's **Root Directory** to
`salone-explorer` (a dashboard setting), so Vercel builds only the app and
the app-level `salone-explorer/vercel.json` supplies headers and SPA
rewrites.

In the live project (`slint-ai-led-sdlc-s-projects/ai-led-sdlc-demo`) the Root Directory was
unset (`framework: null`, `rootDirectory: null`). Vercel therefore built
from the repo root — which has no app — and every route returned
`404 NOT_FOUND`. The Root Directory is dashboard-only; it cannot be set via
the API/MCP tools available here. The maintainer chose to fix it in code
rather than the dashboard.

## Decision

Add a **repo-root `vercel.json`** that builds the subdirectory:

- `installCommand` / `buildCommand` `cd salone-explorer` then install/build.
- `outputDirectory: salone-explorer/dist` is what Vercel serves.
- It also carries the security `headers` and SPA `rewrites`, because once
  Vercel builds from the repo root the app-level `salone-explorer/vercel.json`
  is ignored (Vercel reads `vercel.json` from the Root Directory only).

The build uses `npm run build` (client-rendered SPA + sitemap/llms/robots),
not `build:prerender`: Playwright/Chromium on the Vercel build image is
unverified, and JSON-LD/meta are still emitted client-side. Pre-rendering
can be enabled later by overriding the build command once the build image is
confirmed to support `npx playwright install`.

## Consequences

- The site deploys correctly from the repo root with no dashboard change.
- **Duplication:** the header/rewrite config now exists in both
  `/vercel.json` (active) and `salone-explorer/vercel.json` (inactive while
  Root Directory is repo root). Keep them in sync, or, if the dashboard Root
  Directory is later set to `salone-explorer` (the SPEC-native path), delete
  `/vercel.json` and the app-level one becomes authoritative again.
- `.claude/` and `docs/` are part of the build's source checkout but never
  served (only `outputDirectory` is published).
- This is the maintainer-authorised deviation from SPEC §12.

## Amendment (2026-06-06): routes config, SSG build, config alignment

- The rewrites-based SPA fallback did not serve `index.html` for client
  routes on this `framework: null` project. Both `vercel.json` files now use
  the legacy `routes` config (a header route with `continue`, the
  `filesystem` handle, then `/.* -> /index.html`), which is
  framework-independent and serves the nested prerendered files.
- The root build command is `cd salone-explorer && npm run build:prerender`
  (browser-free SSG, ADR 0002 amendment) — no Chromium on the build image.
- The two configs are aligned: identical `routes`/headers; the root file
  additionally carries the build shim (install/build/outputDirectory). The
  app-level file is the form used if the dashboard Root Directory is later
  set to `salone-explorer`.
