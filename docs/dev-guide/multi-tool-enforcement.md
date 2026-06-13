# Multi-tool enforcement floor

The AI-led SDLC harness enforces governance through Claude Code-specific
mechanisms: `settings.json` hook events (`PreToolUse`, `UserPromptSubmit`,
`Stop`) and bash scripts that read Claude Code's `.tool_input.*` JSON
payloads. Codex CLI and Gemini CLI do not emit those events or payloads,
so none of the Claude Code hooks fire for them.

This page documents the tool-agnostic enforcement floor that holds
regardless of which assistant authored the change. It is the portable
subset of the harness — not full parity.

## What is portable

Every commit, from any tool or a bare terminal, passes through versioned
git hooks in `.githooks/` (activated via `core.hooksPath`):

| Hook         | Enforces                                                | Mirrors                          |
| ------------ | ------------------------------------------------------- | -------------------------------- |
| `commit-msg` | `Requirement:`/`Phase:`/`Incident:` traceability trailer | `pre-tool-bash.sh` trailer check |
| `pre-commit` | secret scan on staged files                             | `scan-secrets.sh` / `pre-tool-bash.sh` |
| `pre-commit` | new source file has a one-line purpose header           | `pre-tool-edit.sh`               |
| `pre-commit` | three-layer separation grep on staged app source        | `verification-loop` SKILL        |

The hooks call the existing `.claude/scripts/` logic — one source of
truth, invoked by both the Claude Code hooks and the git hooks. The
three-layer grep is scoped to `salone-explorer/src/{components,pages,lib}`
and is a no-op until the app is scaffolded.

Agent memory is generated for each tool. Each file opens with a
tool-specific preamble (what is mechanically enforced for that tool, and
which Claude Code-native mechanisms do not apply) followed by the shared
binding rules and `CLAUDE.md` as reference. The preamble is the only
per-tool content; the governance is single-sourced.

| File        | Tool       | Composition                                                |
| ----------- | ---------- | ---------------------------------------------------------- |
| `AGENTS.md` | Codex CLI  | Codex preamble + `.claude/rules/*.md` + `CLAUDE.md`        |
| `GEMINI.md` | Gemini CLI | Gemini preamble + `.claude/rules/*.md` + `CLAUDE.md`       |

Do not edit `AGENTS.md` or `GEMINI.md` by hand - they are generated. Adapt
the preamble in `gen-agent-memory.sh` or the shared rules, then regenerate.
`CLAUDE.md` is written for Claude Code; the preamble tells the other tools
which parts apply to them and which are Claude Code-only background.

## Setup (per clone)

```
.claude/scripts/install-git-hooks.sh     # sets core.hooksPath = .githooks
.claude/scripts/gen-agent-memory.sh      # writes AGENTS.md and GEMINI.md
```

`core.hooksPath` is local config and is not set automatically on clone;
each developer runs the install script once. Reverse with
`git config --unset core.hooksPath`.

Regenerate the memory files whenever `CLAUDE.md` or a rule changes.
`gen-agent-memory.sh --check` exits non-zero if either file is stale (use
it in CI or a pre-push check).

## Known gaps — not enforceable at the git layer

These remain Claude Code-only. Document them; do not assume parity.

- **`git reset --hard` and `git push --force`.** Neither fires a git
  hook. `reset --hard` triggers nothing; `pre-push` can inspect refs but
  cannot see the `--force` flag. Enforced for Claude Code via
  `settings.json` deny + `pre-tool-bash.sh`; unprotected for Codex and
  Gemini.
- **`git commit --no-verify`.** By definition skips every git hook, so
  the floor cannot self-enforce against it. The only backstop is CI: the
  same checks must run in `ci.yml` so a bypassed local hook still fails
  the pipeline. (CI mirror is a planned follow-up.)
- **The spec-first prompt gate** (`user-prompt-submit.sh`) gates prompts,
  which have no git analogue. The `commit-msg` trailer is its commit-time
  equivalent — the violation is caught at commit instead of at prompt.
- **Slash commands, subagents, skills, output styles, statusline.** These
  are Claude Code-native formats with no Codex/Gemini equivalent and are
  out of scope for the floor.

## Why a floor, not parity

The harness's value is mechanical enforcement. A naive port of the
Claude Code hooks to Codex/Gemini would degrade every hard block to a
soft suggestion in the agent's context, because the host event systems
differ. Git hooks are the one layer all three tools share — they all
shell out to `git` — so the floor gives the same hard guarantees on the
checks that can live there, and names the gaps for the rest.
