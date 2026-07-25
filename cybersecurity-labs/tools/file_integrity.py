#!/usr/bin/env python3
"""Create and compare SHA-256 baselines for a user-selected lab directory."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inventory(root: Path) -> dict[str, str]:
    if not root.is_dir():
        raise ValueError(f"Monitored path is not a directory: {root}")

    results: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            print(f"Skipping symbolic link: {path}", file=sys.stderr)
        elif path.is_file():
            results[path.relative_to(root).as_posix()] = sha256_file(path)
    return results


def write_baseline(root: Path, baseline_path: Path) -> None:
    if baseline_path.resolve().is_relative_to(root.resolve()):
        raise ValueError("Store the baseline outside the monitored directory.")

    data = {
        "algorithm": "sha256",
        "root_label": root.name,
        "files": inventory(root),
    }
    baseline_path.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"Baseline created for {len(data['files'])} file(s): {baseline_path}")


def compare(root: Path, baseline_path: Path) -> int:
    data = json.loads(baseline_path.read_text(encoding="utf-8"))
    if data.get("algorithm") != "sha256" or not isinstance(data.get("files"), dict):
        raise ValueError("Baseline format is not supported.")

    before: dict[str, str] = data["files"]
    after = inventory(root)

    added = sorted(after.keys() - before.keys())
    deleted = sorted(before.keys() - after.keys())
    modified = sorted(
        name for name in after.keys() & before.keys() if after[name] != before[name]
    )

    print(f"Added: {len(added)}")
    for name in added:
        print(f"  + {name}")
    print(f"Modified: {len(modified)}")
    for name in modified:
        print(f"  ~ {name}")
    print(f"Deleted: {len(deleted)}")
    for name in deleted:
        print(f"  - {name}")

    if not (added or modified or deleted):
        print("No changes detected.")
        return 0
    return 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baseline or compare files in an authorized lab directory."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in ("baseline", "check"):
        sub = subparsers.add_parser(command)
        sub.add_argument("directory", type=Path)
        sub.add_argument("baseline_file", type=Path)

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        root = args.directory.expanduser().resolve()
        baseline_path = args.baseline_file.expanduser().resolve()
        if args.command == "baseline":
            write_baseline(root, baseline_path)
            return 0
        return compare(root, baseline_path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

