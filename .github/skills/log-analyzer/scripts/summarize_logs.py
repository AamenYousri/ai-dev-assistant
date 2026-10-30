#!/usr/bin/env python3
"""Summarize common log levels and recurring message patterns.

This is a lightweight heuristic helper. Redact sensitive values first and
verify its grouping: normalization can combine unrelated messages.
"""
from __future__ import annotations
import argparse
import re
import sys
from collections import Counter
from pathlib import Path

LEVEL_RE = re.compile(r"\b(TRACE|DEBUG|INFO|WARN|WARNING|ERROR|FATAL)\b", re.I)
TIMESTAMP_RE = re.compile(r"^\s*(?:\d{4}-\d{2}-\d{2}[T ][0-9:.+Z-]+|\d{2}/\d{2}/\d{4}\s+[0-9:,]+)\s*")
UUID_RE = re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b", re.I)
HEX_ADDRESS_RE = re.compile(r"\b0x[0-9a-f]+\b", re.I)
LONG_NUMBER_RE = re.compile(r"\b\d{5,}\b")
THREAD_RE = re.compile(r"\s+\[(?:[A-Za-z0-9_.-]+-)?\d+\]\s+")

def normalize_message(line: str) -> str:
    message = TIMESTAMP_RE.sub("", line.strip())
    message = LEVEL_RE.sub("<LEVEL>", message, count=1)
    message = UUID_RE.sub("<UUID>", message)
    message = HEX_ADDRESS_RE.sub("<ADDRESS>", message)
    message = LONG_NUMBER_RE.sub("<ID>", message)
    message = THREAD_RE.sub(" [THREAD] ", message)
    return message[:500]

def summarize(text: str, top: int = 20) -> str:
    levels: Counter[str] = Counter()
    repeated: Counter[str] = Counter()
    exceptions: Counter[str] = Counter()
    for line in text.splitlines():
        match = LEVEL_RE.search(line)
        if match:
            level = match.group(1).upper()
            if level == "WARNING":
                level = "WARN"
            levels[level] += 1
        if line.strip():
            repeated[normalize_message(line)] += 1
        exc = re.search(r"(?:Caused by:\s*)?([A-Za-z_$][\w.$]*(?:Exception|Error))\b", line)
        if exc:
            exceptions[exc.group(1)] += 1
    lines = ["# Log summary", "", "## Log levels"]
    if levels:
        lines.extend(f"- {key}: {value}" for key, value in levels.most_common())
    else:
        lines.append("- No recognized log levels found.")
    lines.extend(["", "## Most repeated message patterns"])
    if repeated:
        lines.extend(f"- {count}x - `{message}`" for message, count in repeated.most_common(top))
    else:
        lines.append("- No non-empty log lines found.")
    lines.extend(["", "## Exception types"])
    if exceptions:
        lines.extend(f"- {name}: {count}" for name, count in exceptions.most_common())
    else:
        lines.append("- No exception type names recognized.")
    lines.extend(["", "> Heuristic summary only. Review the original (redacted) log context before drawing conclusions. Similar-looking lines may have been grouped.", ""])
    return "\n".join(lines)

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Input log file (redact sensitive values first)")
    parser.add_argument("-o", "--output", help="Output Markdown report; default is stdout")
    parser.add_argument("--top", type=int, default=20, help="Maximum repeated patterns to show")
    args = parser.parse_args()
    if args.top < 1:
        parser.error("--top must be at least 1")
    source = Path(args.input)
    if not source.is_file():
        parser.error(f"Input file does not exist: {source}")
    try:
        report = summarize(source.read_text(encoding="utf-8", errors="replace"), args.top)
        if args.output:
            destination = Path(args.output)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(report, encoding="utf-8")
        else:
            sys.stdout.write(report)
    except OSError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
