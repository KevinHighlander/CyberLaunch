#!/usr/bin/env python3
"""Create a readable Atlantic tropical-weather briefing from official NHC feeds."""

from __future__ import annotations

import argparse
import re
import sys
import textwrap
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ATLANTIC_FEED = "https://www.nhc.noaa.gov/index-at.xml"
OUTLOOK_FEED = "https://www.nhc.noaa.gov/xml/TWOAT.xml"
NHC_HOME = "https://www.nhc.noaa.gov/"
USER_AGENT = "CyberLaunch-Hurricane-Tracker/1.0 (educational portfolio project)"
DEFAULT_TIMEOUT_SECONDS = 20

SAMPLE_ATLANTIC_XML = """<?xml version="1.0"?>
<rss version="2.0"><channel>
  <title>NHC Atlantic</title>
  <pubDate>Fri, 24 Jul 2026 12:00:00 GMT</pubDate>
  <item>
    <title>Hurricane Example Public Advisory Number 8</title>
    <description>Example is moving northwest. This is demonstration data only.</description>
    <link>https://www.nhc.noaa.gov/</link>
    <pubDate>Fri, 24 Jul 2026 12:00:00 GMT</pubDate>
  </item>
  <item>
    <title>Atlantic Tropical Weather Outlook</title>
    <description>One demonstration disturbance has a low chance of formation.</description>
    <link>https://www.nhc.noaa.gov/gtwo.php</link>
    <pubDate>Fri, 24 Jul 2026 12:00:00 GMT</pubDate>
  </item>
</channel></rss>"""

SAMPLE_OUTLOOK_XML = """<?xml version="1.0"?>
<rss version="2.0"><channel>
  <title>Graphical Tropical Weather Outlook</title>
  <pubDate>Fri, 24 Jul 2026 12:00:00 GMT</pubDate>
  <item>
    <title>Atlantic 7-Day Graphical Tropical Weather Outlook</title>
    <description>Demonstration outlook: formation chance is low (20 percent).</description>
    <link>https://www.nhc.noaa.gov/gtwo.php</link>
    <pubDate>Fri, 24 Jul 2026 12:00:00 GMT</pubDate>
  </item>
</channel></rss>"""


@dataclass(frozen=True)
class FeedItem:
    """One entry from an NHC RSS feed."""

    title: str
    description: str
    link: str
    published: str


@dataclass(frozen=True)
class Feed:
    """Parsed RSS channel metadata and entries."""

    title: str
    published: str
    items: tuple[FeedItem, ...]


def clean_text(value: str | None) -> str:
    """Convert basic feed HTML and repeated whitespace to readable plain text."""
    if not value:
        return ""
    value = re.sub(r"<br\s*/?>", "\n", value, flags=re.IGNORECASE)
    value = re.sub(r"<[^>]+>", " ", value)
    value = unescape(value)
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in value.splitlines()]
    return "\n".join(line for line in lines if line)


def child_text(parent: ET.Element, name: str) -> str:
    """Read a direct RSS child while tolerating XML namespaces."""
    for child in parent:
        if child.tag.rsplit("}", 1)[-1] == name:
            return "".join(child.itertext()).strip()
    return ""


def parse_rss(xml_text: str) -> Feed:
    """Parse an RSS feed and raise ValueError when its structure is unusable."""
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        raise ValueError(f"invalid XML: {exc}") from exc

    channel = next(
        (node for node in root.iter() if node.tag.rsplit("}", 1)[-1] == "channel"),
        None,
    )
    if channel is None:
        raise ValueError("RSS channel was not found")

    items: list[FeedItem] = []
    for node in channel:
        if node.tag.rsplit("}", 1)[-1] != "item":
            continue
        title = clean_text(child_text(node, "title")) or "Untitled NHC update"
        items.append(
            FeedItem(
                title=title,
                description=clean_text(child_text(node, "description")),
                link=child_text(node, "link"),
                published=clean_text(child_text(node, "pubDate")),
            )
        )
    return Feed(
        title=clean_text(child_text(channel, "title")) or "NHC feed",
        published=clean_text(child_text(channel, "pubDate")),
        items=tuple(items),
    )


def fetch_text(url: str, timeout: int = DEFAULT_TIMEOUT_SECONDS) -> str:
    """Download public NHC data. The feeds require no key or account."""
    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/rss+xml, application/xml, text/xml",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def retrieve_feed(url: str, timeout: int) -> Feed:
    return parse_rss(fetch_text(url, timeout))


def likely_advisories(items: tuple[FeedItem, ...]) -> list[FeedItem]:
    """Select cyclone-specific products without claiming to replace NHC analysis."""
    product_terms = (
        "public advisory",
        "forecast advisory",
        "forecast discussion",
        "tropical cyclone update",
        "key messages",
    )
    return [item for item in items if any(term in item.title.lower() for term in product_terms)]


def format_item(item: FeedItem, width: int = 88) -> str:
    lines = [f"- {item.title}"]
    if item.published:
        lines.append(f"  Issued: {item.published}")
    if item.description:
        summary = " ".join(item.description.split())
        lines.extend(textwrap.wrap(summary, width=width, initial_indent="  ", subsequent_indent="  "))
    if item.link:
        lines.append(f"  More: {item.link}")
    return "\n".join(lines)


def build_report(atlantic: Feed, outlook: Feed, *, sample: bool = False) -> str:
    """Build a deterministic plain-text report from parsed feeds."""
    generated = (
        "2026-07-24 12:00 UTC (sample data)"
        if sample
        else datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    )
    advisories = likely_advisories(atlantic.items)
    outlook_items = list(outlook.items)

    sections = [
        "ATLANTIC HURRICANE TRACKER",
        "=" * 28,
        f"Generated: {generated}",
        f"Mode: {'OFFLINE DEMONSTRATION' if sample else 'LIVE NHC DATA'}",
        "",
        "ACTIVE-CYCLONE ADVISORY PRODUCTS",
        "-" * 32,
        (
            "\n\n".join(format_item(item) for item in advisories)
            if advisories
            else "No cyclone-specific advisory products were found in the Atlantic feed."
        ),
        "",
        "ATLANTIC FORMATION OUTLOOK",
        "-" * 27,
        (
            "\n\n".join(format_item(item) for item in outlook_items)
            if outlook_items
            else "No outlook entries were found."
        ),
        "",
        "DATA NOTES",
        "----------",
        f"- Atlantic advisory feed: {ATLANTIC_FEED}",
        f"- Atlantic outlook feed: {OUTLOOK_FEED}",
        f"- Official NHC website: {NHC_HOME}",
        (
            "- This report uses fictional sample entries and is not weather information."
            if sample
            else "- Feed entries are reproduced as a convenience; open the linked NHC product for details."
        ),
        "- This educational tool is not an emergency-alert service.",
        "- For safety decisions, use current NHC products and local emergency instructions.",
    ]
    return "\n".join(sections).rstrip() + "\n"


def default_output_path() -> Path:
    return Path(__file__).resolve().parent / "output" / "atlantic_hurricane_report.txt"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a plain-text Atlantic briefing from official NHC RSS feeds."
    )
    parser.add_argument("-o", "--output", type=Path, default=default_output_path())
    parser.add_argument("--print", action="store_true", dest="print_report")
    parser.add_argument(
        "--sample",
        action="store_true",
        help="use bundled fictional data instead of making an internet request",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=f"network timeout in seconds (default: {DEFAULT_TIMEOUT_SECONDS})",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.timeout < 1:
        print("Error: --timeout must be at least 1 second.", file=sys.stderr)
        return 2

    try:
        if args.sample:
            atlantic = parse_rss(SAMPLE_ATLANTIC_XML)
            outlook = parse_rss(SAMPLE_OUTLOOK_XML)
        else:
            atlantic = retrieve_feed(ATLANTIC_FEED, args.timeout)
            outlook = retrieve_feed(OUTLOOK_FEED, args.timeout)
        report = build_report(atlantic, outlook, sample=args.sample)
    except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
        print(f"Could not create the report: {exc}", file=sys.stderr)
        print("Check your internet connection, or run with --sample to test offline.", file=sys.stderr)
        return 1

    output = args.output.expanduser().resolve()
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report, encoding="utf-8")
    except OSError as exc:
        print(f"Could not save {output}: {exc}", file=sys.stderr)
        return 1

    if args.print_report:
        print(report, end="")
    print(f"Saved report: {output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
