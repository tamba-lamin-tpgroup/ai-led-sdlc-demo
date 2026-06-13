#!/usr/bin/env python3
# token-report.py - aggregate Claude Code token usage for THIS project only.
#
# @file
# Reads the project's own transcript JSONL files
# (~/.claude/projects/<encoded-project-dir>/*.jsonl), sums the per-message
# token usage, and prints a per-day table plus an overall total. Scope is a
# single project and a single tool (Claude Code) by construction, so figures
# never leak in from other repos or other agent CLIs.
#
# De-duplication: the same assistant turn can appear in more than one JSONL
# file (resumed sessions copy history). Lines are keyed by
# message.id|requestId and counted once, taking the max token total per key
# so streamed partials never inflate the sum.
#
# Cost: read from .claude/config/model-pricing.json. Rates ship as null so no
# price is ever fabricated; until they are filled the cost column reads "n/a".
# The live statusline already shows Claude Code's own authoritative cost.
#
# Usage:
#   python3 .claude/scripts/token-report.py                 # all-time, by day
#   python3 .claude/scripts/token-report.py --since 2026-06-01
#   python3 .claude/scripts/token-report.py --since-ts 2026-06-05T03:00:00Z
#   python3 .claude/scripts/token-report.py --by-session
#   python3 .claude/scripts/token-report.py --summary       # one compact line
#   python3 .claude/scripts/token-report.py --json

import argparse
import json
import os
import sys
from pathlib import Path

TOKEN_FIELDS = (
    "input_tokens",
    "output_tokens",
    "cache_creation_input_tokens",
    "cache_read_input_tokens",
)


def project_transcript_dir() -> Path:
    """Resolve the Claude Code transcript dir for the current project.

    Claude Code stores transcripts under ~/.claude/projects/<dir> where
    <dir> is the absolute project path with every '/' replaced by '-'.
    Fail fast with a clear message if the directory is absent.
    """
    project = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    encoded = str(Path(project).resolve()).replace("/", "-")
    transcript_dir = Path.home() / ".claude" / "projects" / encoded
    if not transcript_dir.is_dir():
        available = sorted(
            p.name for p in (Path.home() / ".claude" / "projects").glob("*")
        )
        sys.exit(
            f"No transcript directory for this project.\n"
            f"  expected: {transcript_dir}\n"
            f"  derived from: {project}\n"
            f"  available: {', '.join(available) or '(none)'}"
        )
    return transcript_dir


def load_pricing() -> dict:
    """Load the per-model pricing config, or an empty map if absent."""
    config = (
        Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
        / ".claude"
        / "config"
        / "model-pricing.json"
    )
    if not config.is_file():
        return {}
    with config.open(encoding="utf-8") as handle:
        return json.load(handle).get("models", {})


def iter_usage(transcript_dir: Path):
    """Yield (key, date, session_id, model, usage_dict) for each usage line."""
    for jsonl in sorted(transcript_dir.glob("*.jsonl")):
        with jsonl.open(encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    # A truncated final line in an active session is normal;
                    # skip it rather than aborting the whole report.
                    continue
                message = record.get("message") or {}
                usage = message.get("usage")
                if not usage:
                    continue
                key = f"{message.get('id', '')}|{record.get('requestId', '')}"
                if key == "|":
                    key = record.get("uuid", "")
                timestamp = record.get("timestamp", "")
                yield (
                    key,
                    timestamp[:10],
                    record.get("sessionId", ""),
                    message.get("model", ""),
                    timestamp,
                    usage,
                )


def total_tokens(usage: dict) -> int:
    return sum(int(usage.get(field, 0) or 0) for field in TOKEN_FIELDS)


def aggregate(transcript_dir: Path, since: str, by_session: bool):
    """Return (groups, totals, models) deduped and filtered by `since`."""
    seen: dict[str, int] = {}
    rows: dict[str, dict] = {}
    models: set[str] = set()
    for key, day, session_id, model, timestamp, usage in iter_usage(
        transcript_dir
    ):
        if since and timestamp < since:
            continue
        running = total_tokens(usage)
        # Keep the largest-token instance per key (final over partials).
        if key and seen.get(key, -1) >= running:
            continue
        if key:
            seen[key] = running
        bucket = session_id if by_session else day
        slot = rows.setdefault(
            bucket, {field: 0 for field in TOKEN_FIELDS} | {"_model": model}
        )
        for field in TOKEN_FIELDS:
            slot[field] += int(usage.get(field, 0) or 0)
        if model:
            models.add(model)
    totals = {field: sum(r[field] for r in rows.values()) for field in TOKEN_FIELDS}
    return rows, totals, models


def cost_for(usage: dict, pricing: dict, model: str):
    """Return USD cost for a token bundle, or None if rates are missing."""
    rates = pricing.get(model)
    if not rates:
        return None
    pairs = (
        ("input_tokens", "input"),
        ("output_tokens", "output"),
        ("cache_creation_input_tokens", "cache_write"),
        ("cache_read_input_tokens", "cache_read"),
    )
    if any(rates.get(rate_key) is None for _, rate_key in pairs):
        return None
    return sum(
        int(usage.get(tok_key, 0) or 0) / 1_000_000 * float(rates[rate_key])
        for tok_key, rate_key in pairs
    )


def fmt(n: int) -> str:
    return f"{n:,}"


def print_table(rows: dict, totals: dict, pricing: dict, label: str):
    header = f"{label:<26}{'Input':>12}{'Output':>12}{'CacheW':>14}{'CacheR':>14}{'Total':>14}{'Cost':>12}"
    print(header)
    print("-" * len(header))
    for bucket in sorted(rows):
        slot = rows[bucket]
        row_total = total_tokens(slot)
        cost = cost_for(slot, pricing, slot["_model"])
        cost_str = f"${cost:,.2f}" if cost is not None else "n/a"
        print(
            f"{bucket:<26}"
            f"{fmt(slot['input_tokens']):>12}"
            f"{fmt(slot['output_tokens']):>12}"
            f"{fmt(slot['cache_creation_input_tokens']):>14}"
            f"{fmt(slot['cache_read_input_tokens']):>14}"
            f"{fmt(row_total):>14}"
            f"{cost_str:>12}"
        )
    print("-" * len(header))
    grand = sum(totals.values())
    model = next(iter(rows.values()))["_model"] if rows else ""
    cost = cost_for(totals, pricing, model)
    cost_str = f"${cost:,.2f}" if cost is not None else "n/a"
    print(
        f"{'TOTAL':<26}"
        f"{fmt(totals['input_tokens']):>12}"
        f"{fmt(totals['output_tokens']):>12}"
        f"{fmt(totals['cache_creation_input_tokens']):>14}"
        f"{fmt(totals['cache_read_input_tokens']):>14}"
        f"{fmt(grand):>14}"
        f"{cost_str:>12}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Claude Code token usage for this project."
    )
    parser.add_argument("--since", help="Filter from date (YYYY-MM-DD).")
    parser.add_argument(
        "--since-ts", help="Filter from an ISO-8601 timestamp (inclusive)."
    )
    parser.add_argument(
        "--by-session",
        action="store_true",
        help="Group by Claude Code session id instead of day.",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print one compact line (for session snapshots).",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    args = parser.parse_args()

    since = args.since_ts or (args.since or "")
    transcript_dir = project_transcript_dir()
    pricing = load_pricing()
    rows, totals, models = aggregate(transcript_dir, since, args.by_session)
    grand = sum(totals.values())
    model = next(iter(models)) if len(models) == 1 else ""
    cost = cost_for(totals, pricing, model) if model else None

    if args.json:
        print(
            json.dumps(
                {
                    "project_dir": str(transcript_dir),
                    "since": since or None,
                    "models": sorted(models),
                    "totals": totals,
                    "total_tokens": grand,
                    "cost_usd": cost,
                },
                indent=2,
            )
        )
        return

    if args.summary:
        cost_str = f"cost:${cost:,.2f}" if cost is not None else "cost:n/a"
        print(
            f"tokens total:{fmt(grand)} "
            f"(in:{fmt(totals['input_tokens'])} "
            f"out:{fmt(totals['output_tokens'])} "
            f"cacheW:{fmt(totals['cache_creation_input_tokens'])} "
            f"cacheR:{fmt(totals['cache_read_input_tokens'])}) {cost_str}"
        )
        return

    label = "Session" if args.by_session else "Date"
    scope = f" since {since}" if since else ""
    print(f"Claude Code token usage - this project{scope}")
    print(f"models: {', '.join(sorted(models)) or '(none)'}\n")
    print_table(rows, totals, pricing, label)
    if cost is None:
        print(
            "\ncost: n/a - set rates in .claude/config/model-pricing.json "
            "(live cost shows in the statusline)."
        )


if __name__ == "__main__":
    main()
