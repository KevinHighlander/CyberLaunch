#!/usr/bin/env python3
"""Build a plain-text Atlantic tropical weather briefing from official NHC data."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

OUTLOOK_URL = "https://www.nhc.noaa.gov/text/MIATWOAT.shtml"
DISCUSSION_URL = "https://www.nhc.noaa.gov/text/MIATWDAT.shtml"
STORMS_URL = "https://www.nhc.noaa.gov/CurrentStorms.json"
USER_AGENT = "Atlantic-Hurricane-Report/1.1 (personal weather briefing)"


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def text(self) -> str:
        raw = unescape(" ".join(self.parts))
        lines = [re.sub(r"\s+", " ", line).strip() for line in raw.splitlines()]
        return "\n".join(line for line in lines if line)


def fetch(url: str, timeout: int = 25) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def html_to_text(source: str) -> str:
    parser = _TextExtractor()
    parser.feed(source)
    text = parser.text()
    # NHC pages place the operational product between predictable headings.
    for marker in ("ZCZC", "000\n", "Tropical Weather"):
        position = text.find(marker)
        if position >= 0:
            return text[position:]
    return text


def section(text: str, heading: str) -> str:
    pattern = rf"\.\.\.{re.escape(heading)}\.\.\.(.*?)(?=\n\.\.\.[A-Z /-]+\.\.\.|\Z)"
    match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else ""


def active_atlantic_storms(raw_json: str) -> list[dict]:
    data = json.loads(raw_json)
    candidates = data.get("activeStorms", data if isinstance(data, list) else [])
    storms = []
    for storm in candidates:
        basin = str(storm.get("basin", storm.get("basin2", ""))).upper()
        storm_id = str(storm.get("id", storm.get("stormId", ""))).upper()
        if basin in {"AT", "AL", "ATLANTIC"} or storm_id.startswith("AL"):
            storms.append(storm)
    return storms


def storm_summary(storm: dict) -> str:
    name = storm.get("name") or storm.get("stormName") or "Unnamed system"
    classification = storm.get("classification") or storm.get("type") or "Tropical cyclone"
    advisory = storm.get("publicAdvisory") or storm.get("publicAdvisoryLink")
    line = f"- {name}: {classification}"
    return f"{line}\n  Advisory: {advisory}" if advisory else line


def risk_level(outlook: str, storms: list[dict], discussion: str) -> str:
    combined = f"{outlook}\n{discussion}".lower()
    if storms or re.search(r"\b(high|80 percent|90 percent)\b", combined):
        return "ELEVATED"
    if re.search(r"\b(medium|40 percent|50 percent|60 percent|70 percent)\b", combined):
        return "WATCH"
    if re.search(r"\b(low|formation chance|disturbance|tropical wave)\b", combined):
        return "MONITOR"
    return "QUIET"


def build_report() -> str:
    errors: list[str] = []
    outlook = discussion = ""
    storms: list[dict] = []

    try:
        outlook = html_to_text(fetch(OUTLOOK_URL))
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        errors.append(f"Atlantic outlook unavailable: {exc}")
    try:
        discussion = html_to_text(fetch(DISCUSSION_URL))
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        errors.append(f"Tropical weather discussion unavailable: {exc}")
    try:
        storms = active_atlantic_storms(fetch(STORMS_URL))
    except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        errors.append(f"Active-storm feed unavailable: {exc}")

    waves = section(discussion, "TROPICAL WAVES")
    special = section(discussion, "SPECIAL FEATURES") or section(discussion, "SPECIAL FEATURE")
    coast_terms = re.compile(
        r"[^.\n]*(?:Bahamas|Florida|Georgia|Carolinas?|East Coast|United States|U\.S\.|"
        r"Caribbean|Gulf of (?:Mexico|America))[^.\n]*[.]?",
        re.IGNORECASE,
    )
    coast_mentions = coast_terms.findall(f"{outlook}\n{discussion}")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    parts = [
        "ATLANTIC HURRICANE REPORT",
        f"Generated: {now}",
        f"Overall status: {risk_level(outlook, storms, discussion)}",
        "",
        "ACTIVE ATLANTIC SYSTEMS",
        "\n".join(storm_summary(item) for item in storms) or "No active Atlantic tropical cyclones found.",
        "",
        "FORMATION OUTLOOK (2-DAY / 7-DAY)",
        outlook or "Outlook could not be retrieved.",
        "",
        "TROPICAL WAVES FROM AFRICA WESTWARD",
        waves or "No tropical-wave section was found in the latest discussion.",
        "",
        "SPECIAL FEATURES",
        special or "No special-features section was found.",
        "",
        "POSSIBLE U.S. / WESTERN ATLANTIC RELEVANCE",
        "\n".join(f"- {x.strip()}" for x in coast_mentions[:12])
        or "No location-specific mentions were found. This is not a forecast of no risk.",
    ]
    if errors:
        parts.extend(["", "DATA WARNINGS", *[f"- {item}" for item in errors]])
    parts.extend(
        [
            "",
            "Official sources:",
            f"- {OUTLOOK_URL}",
            f"- {DISCUSSION_URL}",
            f"- {STORMS_URL}",
            "",
            "Safety note: This automated summary is informational. Always follow current",
            "National Hurricane Center products and local emergency-management instructions.",
        ]
    )
    return "\n".join(parts).strip() + "\n"


def safe_default_output() -> Path:
    script_folder = Path(__file__).resolve().parent
    if script_folder.name.lower() == "inbox":
        return Path.home() / "Documents" / "Hurricane Reports" / "atlantic_hurricane_report.txt"
    return script_folder / "hurricane_reports" / "atlantic_hurricane_report.txt"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-o", "--output", type=Path, default=safe_default_output())
    parser.add_argument("--print", action="store_true", dest="print_report")
    args = parser.parse_args()

    report = build_report()
    output = args.output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")
    dated = output.with_name(f"{output.stem}_{datetime.now():%Y-%m-%d}{output.suffix}")
    dated.write_text(report, encoding="utf-8")
    if args.print_report:
        print(report, end="")
    print(f"Saved report: {output}", file=sys.stderr)
    print(f"Saved archive: {dated}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

