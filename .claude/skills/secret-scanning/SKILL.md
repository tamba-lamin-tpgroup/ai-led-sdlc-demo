---

name: secret-scanning
description: Use to scan staged or modified files for secrets, tokens, API keys, and absolute personal paths before commit. Wraps .claude/scripts/scan-secrets.sh, invoked by the verification-loop skill and the pre-commit hook. Returns non-zero on any finding so callers block.
triggers:
  - "secret scan"
  - "API key leak"
  - "credential"
  - "sensitive data"
  - "hardcoded key"
  - "token leak"
  - "secrets"
  - "pre-commit scan"
context: fork
allowed-tools:
  - Bash
argument-hint: "[<file-path> | --staged]"
---
# Skill: secret-scanning

Block secrets at the commit boundary. Cheap, fast, deterministic,
block-on-finding.

## Implementation

The scanner lives at `.claude/scripts/scan-secrets.sh`. It applies this
rule set to its input paths:

| Pattern (regex)                                         | Why                          |
| ------------------------------------------------------- | ---------------------------- |
| `AKIA[0-9A-Z]{16}`                                      | AWS access key               |
| `gh[ps]_[A-Za-z0-9]{36,}`                               | GitHub PAT (classic / FG)    |
| `xox[baprs]-[A-Za-z0-9-]{10,}`                          | Slack token                  |
| `sk-ant-[A-Za-z0-9_-]{32,}`                             | Anthropic key                |
| `sk-[A-Za-z0-9]{32,}`                                   | OpenAI key                   |
| `sbp_[A-Za-z0-9]{40,}`                                  | Supabase access token        |
| `service_role`                                          | Supabase service-role key    |
| `eyJ...\.[...]\.[...]`                                  | JWT (Supabase keys, etc.)    |
| `-----BEGIN (RSA\|EC\|OPENSSH\|PRIVATE) KEY-----`       | Private key                  |
| `/Users/[a-z][a-z0-9._-]+/`                             | Personal absolute paths      |
| `(password\|secret\|api_key\|service_role)=['"]...['"]` | Inline secret literal        |

Vercel deploy tokens, generic password/secret pairs, and absolute
`/Users/` paths are covered by the same set.

## Salone Explorer specifics

- Only `VITE_`-prefixed env vars are exposed to the browser by Vite.
- The Supabase **service-role key** must NEVER appear in client code or
  any `VITE_`-prefixed variable. It bypasses RLS. Client code uses only
  the anon (publishable) key via `VITE_SUPABASE_ANON_KEY`. Server-only
  secrets stay out of `src/` entirely.
- `.env.example` is intentionally committed with placeholder values and
  is skipped by the scanner.

## Usage

```
.claude/scripts/scan-secrets.sh <path> [path ...]
.claude/scripts/scan-secrets.sh --staged          # all staged paths
```

Exit codes: `0` clean; `1` finding(s); `2` invocation error.

## When findings appear

- **Real secret:** rotate it, then rewrite the change to read from
  `import.meta.env.VITE_*` (client) or a server-side env var. Do not
  commit the original blob; purge it from history if already committed.
- **Service-role key in client code:** treat as critical. Move it server
  side, rotate, and re-scan.
- **False positive:** add a narrowly-scoped allowlist line to
  `.claude/scripts/scan-secrets.allowlist` with a comment explaining why.
  The line must be the exact full output line the scanner prints.

## Hard rules

- Never commit past a finding by using `--no-verify`.
- Never broaden the allowlist to silence a real secret.
