#!/usr/bin/env python3
"""Best-effort local redaction of common secret patterns in text logs.

The source file is never modified in place. This is not a DLP scanner and
cannot guarantee that every secret or item of personal data is removed.
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

PATTERNS = [
    (re.compile(r"(?i)(authorization\s*[:=]\s*bearer\s+)[A-Za-z0-9._~+/=-]+"), r"\1[REDACTED]"),
    (re.compile(r"(?i)(\b(?:password|passwd|pwd|client_secret|clientsecret|access_token|refresh_token|id_token|api[_-]?key|secret)\b\s*[:=]\s*)([\"']?)([^\s,;\"']+)([\"']?)"), r"\1\2[REDACTED]\4"),
    (re.compile(r"(?i)(\bAKIA[0-9A-Z]{16}\b)"), "[REDACTED_AWS_KEY]"),
    (re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b"), "[REDACTED_JWT]"),
    (re.compile(r"(?i)(-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----).*?(-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)", re.S), r"\1[REDACTED_PRIVATE_KEY]\2"),
    (re.compile(r"(?i)(://[^:/\s]+:)[^@/\s]+(@)"), r"\1[REDACTED]\2"),
]

def redact(text: str) -> str:
    for pattern, replacement in PATTERNS:
        text = pattern.sub(replacement, text)
    return text

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Input text log file")
    parser.add_argument("-o", "--output", help="Output file (never overwrite input)")
    args = parser.parse_args()
    source = Path(args.input)
    if not source.is_file():
        parser.error(f"Input file does not exist: {source}")
    if args.output and Path(args.output).resolve() == source.resolve():
        parser.error("Output must be different from input; in-place redaction is disabled")
    try:
        content = source.read_text(encoding="utf-8", errors="replace")
        result = redact(content)
        if args.output:
            destination = Path(args.output)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(result, encoding="utf-8")
        else:
            sys.stdout.write(result)
    except OSError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
