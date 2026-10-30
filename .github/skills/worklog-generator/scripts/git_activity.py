#!/usr/bin/env python3
"""Collect Git activity evidence for a worklog draft. Does not estimate time.

Examples:
  python git_activity.py --since "yesterday" --until "now"
  python git_activity.py --since "2026-10-29" --until "2026-10-30" --output activity.md
"""
from __future__ import annotations
import argparse
import subprocess
import sys
from pathlib import Path

def git(*args: str) -> str:
    result = subprocess.run(["git", *args], text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Git command failed")
    return result.stdout.strip()

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--since", default="yesterday", help="Git date expression (default: yesterday)")
    parser.add_argument("--until", default="now", help="Git date expression (default: now)")
    parser.add_argument("-o", "--output", help="Write Markdown evidence to this file")
    args = parser.parse_args()
    try:
        branch = git("branch", "--show-current") or "(detached HEAD)"
        commits = git("log", f"--since={args.since}", f"--until={args.until}", "--date=short", "--pretty=format:%h | %ad | %s")
        changed = git("log", f"--since={args.since}", f"--until={args.until}", "--name-only", "--pretty=format:")
        status = git("status", "--short")
        paths = sorted({line.strip() for line in changed.splitlines() if line.strip()})
        lines = [
            "# Git activity evidence", "",
            f"- Branch: `{branch}`", f"- Period: `{args.since}` to `{args.until}`", "",
            "## Commits", commits or "No commits found for this period.", "",
            "## Files changed in commits",
            *( [f"- `{p}`" for p in paths] if paths else ["No committed file changes found."] ),
            "",
            "## Current working tree", status or "Clean working tree.", "",
            "> This is activity evidence only. It does not measure time spent. Confirm the actual hours and add work not represented by Git (meetings, analysis, support, reviews, etc.).", ""
        ]
        output = "\n".join(lines)
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
        else:
            print(output)
    except (RuntimeError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
