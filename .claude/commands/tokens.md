---
description: Show Claude Code token usage for this project (per day, or per session with --by-session). Reads the project transcripts directly; scoped to this repo and Claude Code only.
allowed-tools: Bash
---

# /tokens

Report Claude Code token usage for THIS project. Exact counts, deduped,
no leakage from other repos or other agent CLIs.

## Procedure

1. Run the aggregator with any arguments the user passed (`$ARGUMENTS`):

   ```
   python3 "$CLAUDE_PROJECT_DIR/.claude/scripts/token-report.py" $ARGUMENTS
   ```

   With no arguments it prints an all-time, per-day table. Common flags:

   - `--by-session` group by Claude Code session id instead of day
   - `--since 2026-06-01` filter from a date
   - `--since-ts 2026-06-05T03:00:00Z` filter from an ISO timestamp
   - `--summary` one compact line (used by `/session-end`)
   - `--json` machine-readable output

2. Print the table back to the user verbatim.

## Notes

- Token counts are always exact. The cost column reads `n/a` until real
  rates are filled into `.claude/config/model-pricing.json` - by design,
  no price is fabricated. Live, authoritative cost already shows in the
  statusline (`cost:$...`).
- Source of truth is `~/.claude/projects/<encoded-project-dir>/*.jsonl`,
  the transcripts Claude Code writes for this project.
- Once Phase 1 scaffolds `package.json`, add an alias:
  `"tokens": "python3 .claude/scripts/token-report.py"`.
