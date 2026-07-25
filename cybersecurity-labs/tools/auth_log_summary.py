#!/usr/bin/env python3
"""Summarize selected authentication events from a local text log."""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

EVENT_PATTERNS = {
    "accepted_ssh": re.compile(r"\bAccepted (?:password|publickey)\b", re.IGNORECASE),
    "failed_ssh": re.compile(r"\bFailed password\b", re.IGNORECASE),
    "invalid_user": re.compile(r"\binvalid user\b", re.IGNORECASE),
    "sudo": re.compile(r"\bsudo(?:\[\d+\])?:", re.IGNORECASE),
}

SOURCE_PATTERN = re.compile(r"\bfrom ((?:\d{1,3}\.){3}\d{1,3})\b")


def summarize(path: Path) -> None:
    counts: Counter[str] = Counter()
    sources: Counter[str] = Counter()

    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            for name, pattern in EVENT_PATTERNS.items():
                if pattern.search(line):
                    counts[name] += 1
            source = SOURCE_PATTERN.search(line)
            if source:
                sources[source.group(1)] += 1

    print("Authentication event summary")
    for name in EVENT_PATTERNS:
        print(f"  {name}: {counts[name]}")

    print("Source addresses observed")
    if not sources:
        print("  none")
    for address, count in sorted(sources.items()):
        print(f"  {address}: {count} event(s)")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Summarize selected events in a local Linux authentication log."
    )
    parser.add_argument("log_file", type=Path)
    args = parser.parse_args()

    try:
        summarize(args.log_file.expanduser())
        return 0
    except OSError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

