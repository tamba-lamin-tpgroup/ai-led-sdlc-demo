#!/usr/bin/env python3
# resume-context.py - compacts an active session into a returning-agent briefing.
# Usage: python3 resume-context.py [session-id]
#   session-id: optional bare id (without .md); defaults to .current-session pointer.
# Stdout: a compact briefing block the orchestrator or /session-resume can prepend
#         to a subagent prompt so it picks up with full context.
"""
Reads the active (or specified) session file and emits a compact briefing:
  - session id, layer/phase, branch
  - condensed Goals list
  - latest 3 Update summaries (one line each)
  - any open questions

Designed to be injected into the orchestrator's context-pack or directly into
a subagent's system prompt via the Agent tool's prompt parameter.
"""

import re
import sys
from pathlib import Path

SESS_DIR = Path(".claude/sessions")
POINTER = SESS_DIR / ".current-session"


def resolve_session(session_id: str | None) -> Path | None:
    if session_id:
        p = SESS_DIR / f"{session_id}.md"
        return p if p.exists() else None
    if POINTER.exists():
        raw = POINTER.read_text().strip()
        if not raw:
            return None
        candidate = raw if raw.endswith(".md") else f"{raw}.md"
        p = SESS_DIR / candidate
        return p if p.exists() else None
    return None


def parse_goals(text: str) -> list[str]:
    goals = []
    in_goals = False
    for line in text.splitlines():
        if re.match(r"^## Goals", line):
            in_goals = True
            continue
        if in_goals and re.match(r"^## ", line):
            break
        if in_goals and re.match(r"^- \[", line):
            done = line.startswith("- [x]")
            label = "[x]" if done else "[ ]"
            content = re.sub(r"^- \[[x ]\] ?", "", line)
            goals.append(f"{label} {content}")
    return goals


def parse_updates(text: str) -> list[dict]:
    updates: list[dict] = []
    current: dict | None = None
    for line in text.splitlines():
        m = re.match(r"^### Update - (.+)", line)
        if m:
            if current:
                updates.append(current)
            current = {
                "timestamp": m.group(1).strip(),
                "summary": "",
                "branch": "",
                "commit": "",
            }
            continue
        if current is None:
            continue
        if line.startswith("Summary:"):
            current["summary"] = line[len("Summary:"):].strip()
        elif line.strip().startswith("branch:"):
            current["branch"] = line.split(":", 1)[1].strip()
        elif line.strip().startswith("last-commit:"):
            current["commit"] = line.split(":", 1)[1].strip()
    if current:
        updates.append(current)
    return updates


def parse_open_questions(text: str) -> list[str]:
    questions = []
    in_oq = False
    for line in text.splitlines():
        if re.match(r"^## Open questions", line):
            in_oq = True
            continue
        if in_oq and re.match(r"^## ", line):
            break
        if in_oq and line.startswith("-"):
            questions.append(line.lstrip("- ").strip())
    return questions


def render_briefing(path: Path) -> str:
    text = path.read_text()

    def fm(key: str) -> str:
        m = re.search(rf"^{key}:\s*(.+)$", text, re.MULTILINE)
        return m.group(1).strip() if m else ""

    session_id = fm("id")
    layer = fm("layer")
    branch = fm("branch")

    goals = parse_goals(text)
    updates = parse_updates(text)
    open_qs = parse_open_questions(text)

    lines = [
        "==== session resume briefing ====",
        f"session: {session_id}",
        f"layer:   {layer}",
        f"branch:  {branch}",
        "",
        "Goals:",
    ]
    for g in goals:
        lines.append(f"  {g}")

    lines.append("")
    lines.append(f"Recent updates ({min(3, len(updates))} of {len(updates)}):")
    for u in updates[-3:]:
        commit_part = f" | {u['commit']}" if u["commit"] else ""
        lines.append(f"  [{u['timestamp']}]{commit_part}")
        if u["summary"]:
            summary = u["summary"]
            if len(summary) > 90:
                summary = summary[:87] + "..."
            lines.append(f"    {summary}")

    if open_qs:
        lines.append("")
        lines.append("Open questions:")
        for q in open_qs[:5]:
            lines.append(f"  - {q}")

    lines.append("=================================")
    return "\n".join(lines)


def main() -> None:
    session_id = sys.argv[1] if len(sys.argv) > 1 else None
    path = resolve_session(session_id)
    if path is None:
        target = session_id or "(active)"
        print(f"[resume-context] no session found for: {target}", file=sys.stderr)
        sys.exit(1)
    print(render_briefing(path))


if __name__ == "__main__":
    main()
