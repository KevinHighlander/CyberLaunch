#!/usr/bin/env python3
"""Display selected metadata and safe indicators from a local EML file."""

from __future__ import annotations

import argparse
import re
import sys
from email import policy
from email.parser import BytesParser
from pathlib import Path

DEFANGED_URL = re.compile(
    r"\bhxxps?://[^\s<>]+|\bhttps?://[^\s<>]*\[\.\][^\s<>]*", re.IGNORECASE
)


def text_parts(message: object) -> list[str]:
    parts: list[str] = []
    if message.is_multipart():
        for part in message.walk():
            if part.get_content_type() == "text/plain" and not part.get_filename():
                parts.append(part.get_content())
    elif message.get_content_type() == "text/plain":
        parts.append(message.get_content())
    return parts


def summarize(path: Path) -> None:
    with path.open("rb") as handle:
        message = BytesParser(policy=policy.default).parse(handle)

    for header in (
        "From",
        "To",
        "Reply-To",
        "Date",
        "Subject",
        "Message-ID",
        "Authentication-Results",
    ):
        print(f"{header}: {message.get(header, '[not present]')}")

    attachments = [
        part.get_filename()
        for part in message.walk()
        if part.get_content_disposition() == "attachment"
    ]
    print("Attachments:")
    if attachments:
        for filename in attachments:
            print(f"  {filename or '[unnamed attachment]'}")
    else:
        print("  none")

    indicators = sorted(
        {match.group(0).rstrip(".,)") for body in text_parts(message) for match in DEFANGED_URL.finditer(body)}
    )
    print("Defanged URL indicators:")
    if indicators:
        for indicator in indicators:
            print(f"  {indicator}")
    else:
        print("  none")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Summarize a local EML file without making network requests."
    )
    parser.add_argument("eml_file", type=Path)
    args = parser.parse_args()

    try:
        summarize(args.eml_file.expanduser())
        return 0
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

