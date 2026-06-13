---
description: Start the local dev server. Single repo — installs dependencies and runs the Vite dev server, then prints the local URL.
allowed-tools: Bash, Read
---

# /dev-start

Bring the local environment up. Salone Explorer is a single Vite + React
+ TypeScript SPA (one git repo, no submodules).

## Procedure

1. **Precondition**: `package.json` must exist (scaffolded in Phase 1 per
   SPEC.md section 18). If it does not, stop and tell the user to
   complete Phase 1 scaffolding first — there is no dev server yet.

2. **Run**:
   ```
   npm install && npm run dev
   ```

3. **Print** the local URL the dev server binds to:
   `http://localhost:5173`. Note the relevant env file:
   - `.env.local` (copy from `.env.example` if present); only
     `VITE_`-prefixed vars reach the browser.
   - `VITE_ATTRACTIONS_SOURCE` selects the repository implementation
     (`file` is the Phase 1 default).

4. **Run** `/session-update "dev-start: vite dev server running at http://localhost:5173"`.

## When dev fails to start

- Confirm Node 20+ (`node -v`).
- Check `.env.local` against `.claude/settings.local.json.template` and
  the `VITE_` variables the app expects.
- Read `README.md` / `SPEC.md` for prerequisites.
- Capture the exit code; do not silently retry.
