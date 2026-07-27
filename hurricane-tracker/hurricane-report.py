#!/usr/bin/env python3
"""Atlantic Hurricane Report V2 — designed for iPhone/Pyto.

Uses only Python's standard library. Data comes from official NOAA services:
NHC Atlantic outlook/discussion RSS, NHC CurrentStorms.json, and NWS alerts.
This is a briefing aid, not a forecast; always follow official instructions.
"""

from __future__ import annotations

import argparse
import hashlib
import html
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

VERSION = "2.0.0"
USER_AGENT = "AtlanticHurricaneReport/2.0 (personal weather briefing)"
NHC_OUTLOOK_URL = "https://www.nhc.noaa.gov/xml/TWOAT.xml"
NHC_DISCUSSION_URL = "https://www.nhc.noaa.gov/xml/TWDAT.xml"
NHC_STORMS_URL = "https://www.nhc.noaa.gov/CurrentStorms.json"
NWS_ALERTS_URL = "https://api.weather.gov/alerts/active"
WATCH_STATES = ("FL", "GA", "SC", "NC", "VA")
RELEVANT_ALERT_TERMS = (
    "hurricane", "tropical storm", "storm surge", "coastal flood",
    "high surf", "rip current", "flood watch", "flash flood",
)
CLASSIFICATIONS = {
    "HU": "Hurricane", "TS": "Tropical Storm", "TD": "Tropical Depression",
    "SD": "Subtropical Depression", "SS": "Subtropical Storm",
    "PTC": "Potential Tropical Cyclone",
}
ZONES = (
    "Africa and Cabo Verde Region",
    "Eastern Tropical Atlantic",
    "Central Atlantic",
    "Caribbean and Lesser Antilles",
    "Bahamas and Western Atlantic",
    "Florida and Lower East Coast",
    "Unspecified Atlantic Area",
)
SAMPLE_OUTLOOK_TEXT = """
Atlantic Tropical Weather Outlook

1. Eastern Tropical Atlantic:
A broad area of low pressure associated with a tropical wave is moving west
away from the coast of Africa. Formation chance through 48 hours...low...
10 percent. Formation chance through 7 days...medium...40 percent.
"""
SAMPLE_DISCUSSION_TEXT = """
TROPICAL WAVES

An eastern Atlantic tropical wave has its axis along 25W, moving westward at
10 to 15 kt. Scattered showers are present. This is demonstration data only.

MONSOON TROUGH/ITCZ
"""
SAMPLE_STORMS = {
    "activeStorms": [{
        "id": "al012026",
        "name": "Example",
        "classification": "TS",
        "intensity": "50",
        "pressure": "998",
        "latitude": "20.0N",
        "longitude": "55.0W",
        "latitudeNumeric": 20.0,
        "longitudeNumeric": -55.0,
        "movementDir": 280,
        "movementSpeed": 12,
        "lastUpdate": "2026-07-27T12:00:00.000Z",
        "publicAdvisory": {"url": "https://www.nhc.noaa.gov/"},
    }]
}
SAMPLE_ALERT = {
    "features": [{
        "id": "https://api.weather.gov/alerts/sample",
        "properties": {
            "id": "https://api.weather.gov/alerts/sample",
            "event": "Tropical Storm Watch",
            "headline": "Demonstration Tropical Storm Watch for part of coastal Florida",
            "severity": "Severe",
            "urgency": "Expected",
            "areaDesc": "Sample coastal Florida area",
            "effective": "2026-07-27T12:00:00Z",
            "expires": "2026-07-28T12:00:00Z",
            "@id": "https://api.weather.gov/alerts/sample",
        },
    }]
}


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in {"br", "p", "div", "li"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"p", "div", "li"}:
            self.parts.append("\n")


def clean_text(value: str | None) -> str:
    parser = _TextExtractor()
    parser.feed(html.unescape(value or ""))
    text = "".join(parser.parts).replace("\xa0", " ")
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def fetch_bytes(url: str, timeout: int = 25) -> bytes:
    request = Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json, application/xml, text/xml"},
    )
    with urlopen(request, timeout=timeout) as response:
        return response.read()


def fetch_json(url: str) -> dict:
    return json.loads(fetch_bytes(url).decode("utf-8"))


def fetch_rss_text(url: str) -> tuple[str, str]:
    root = ET.fromstring(fetch_bytes(url))
    items = root.findall(".//item")
    if not items:
        raise ValueError("RSS feed contained no items")
    item = items[0]
    title = clean_text(item.findtext("title"))
    description = clean_text(item.findtext("description"))
    return title, description


def compact(value: str, limit: int = 500) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    return value if len(value) <= limit else value[: limit - 1].rstrip() + "…"


def parse_probability(text: str, hours: int) -> int | None:
    patterns = [
        rf"(?:through|during)\s+(?:the next\s+)?{hours}\s*hours?.{{0,55}}?(\d{{1,3}})\s*percent",
        rf"{hours}[- ]hour.{{0,55}}?(\d{{1,3}})\s*percent",
    ]
    if hours == 168:
        patterns.extend((
            r"(?:through|during)\s+(?:the next\s+)?7\s*days?.{0,55}?(\d{1,3})\s*percent",
            r"7[- ]day.{0,55}?(\d{1,3})\s*percent",
        ))
    for pattern in patterns:
        match = re.search(pattern, text, re.I | re.S)
        if match:
            return min(100, int(match.group(1)))
    return None


def longitude_from_text(text: str) -> float | None:
    matches = re.findall(r"(\d{1,3}(?:\.\d+)?)\s*°?\s*([EW])\b", text, re.I)
    if not matches:
        matches = re.findall(r"\b(\d{1,3}(?:\.\d+)?)\s*([EW])\b", text, re.I)
    if not matches:
        return None
    value, direction = matches[-1]
    longitude = float(value)
    return -longitude if direction.upper() == "W" else longitude


def zone_for(text: str, longitude: float | None = None) -> str:
    lower = text.lower()
    if any(word in lower for word in ("florida", "georgia", "carolina", "u.s. east coast")):
        return ZONES[5]
    if any(word in lower for word in ("bahamas", "western atlantic", "gulf stream")):
        return ZONES[4]
    if any(word in lower for word in ("caribbean", "lesser antilles", "windward", "leeward")):
        return ZONES[3]
    if any(word in lower for word in ("africa", "african coast", "cabo verde", "cape verde")):
        return ZONES[0]
    if "central atlantic" in lower:
        return ZONES[2]
    if "eastern atlantic" in lower or "tropical atlantic" in lower:
        return ZONES[1]
    if longitude is not None:
        if longitude >= -25:
            return ZONES[0]
        if longitude >= -45:
            return ZONES[1]
        if longitude >= -62:
            return ZONES[2]
        if longitude >= -75:
            return ZONES[3]
        if longitude >= -83:
            return ZONES[4]
        return ZONES[5]
    return ZONES[6]


def stable_id(kind: str, title: str, text: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    if normalized and normalized not in {"disturbance", "area"}:
        return f"{kind}:{normalized[:60]}"
    digest = hashlib.sha1(compact(text, 180).encode("utf-8")).hexdigest()[:10]
    return f"{kind}:{digest}"


def parse_outlook(text: str) -> list[dict]:
    # NHC outlook areas normally begin with "1. Area name:"; support bullets too.
    marker = re.compile(r"(?m)^\s*(?:\d+[\.\)]|\*)\s+([^\n:]{3,100}):?\s*$")
    matches = list(marker.finditer(text))
    chunks: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        chunks.append((match.group(1).strip(), text[match.end():end].strip()))
    if not chunks and "formation chance" in text.lower():
        chunks = [("Atlantic disturbance", text)]

    systems = []
    for title, body in chunks:
        if "formation chance" not in body.lower():
            continue
        p48, p7 = parse_probability(body, 48), parse_probability(body, 168)
        lon = longitude_from_text(body)
        systems.append({
            "id": stable_id("disturbance", title, body),
            "kind": "disturbance",
            "name": title,
            "zone": zone_for(title + " " + body, lon),
            "probability_48h": p48,
            "probability_7d": p7,
            "longitude": lon,
            "summary": compact(body),
        })
    return systems


def parse_tropical_waves(text: str) -> list[dict]:
    wave_section = text
    match = re.search(
        r"(?:\.\.\.)?TROPICAL WAVES?(?:\.\.\.)?\s*(.*?)"
        r"(?=(?:\.\.\.)?(?:MONSOON TROUGH|ITCZ|GULF OF|CARIBBEAN SEA))",
        text, re.I | re.S,
    )
    if match:
        wave_section = match.group(1)
    paragraphs = re.split(r"\n\s*\n|(?=\b(?:A|An|The)\s+(?:central |eastern |western )?tropical wave)", wave_section)
    waves = []
    for paragraph in paragraphs:
        if "tropical wave" not in paragraph.lower():
            continue
        body = compact(paragraph, 650)
        # Prefer the wave-axis longitude instead of a later convection range.
        axis_match = re.search(
            r"(?:axis[^.;]{0,80}?|wave\s+is\s+(?:along|near)\s+)"
            r"(\d{1,3}(?:\.\d+)?)\s*°?\s*([EW])\b",
            body,
            re.I,
        )
        if axis_match:
            lon = float(axis_match.group(1))
            if axis_match.group(2).upper() == "W":
                lon = -lon
        else:
            lon = longitude_from_text(body)
        direction_match = re.search(r"moving\s+([a-z-]+)(?:ward)?(?:\s+at\s+([^.;]+))?", body, re.I)
        movement = compact(direction_match.group(0), 90) if direction_match else "Movement not parsed"
        waves.append({
            "id": stable_id("wave", f"{lon}", body),
            "kind": "tropical_wave",
            "name": f"Tropical wave near {abs(lon):g}°{'W' if lon and lon < 0 else 'E'}" if lon is not None else "Tropical wave",
            "zone": zone_for(body, lon),
            "longitude": lon,
            "movement": movement,
            "summary": body,
        })
    return waves


def parse_active_storms(payload: dict) -> list[dict]:
    storms = []
    for raw in payload.get("activeStorms", []):
        storm_id = str(raw.get("id", "")).lower()
        if not storm_id.startswith("al"):
            continue
        lon = raw.get("longitudeNumeric")
        try:
            lon = float(lon)
        except (TypeError, ValueError):
            lon = longitude_from_text(str(raw.get("longitude", "")))
        classification = CLASSIFICATIONS.get(raw.get("classification"), raw.get("classification", "Cyclone"))
        storms.append({
            "id": f"storm:{storm_id}",
            "kind": "active_storm",
            "name": str(raw.get("name") or storm_id.upper()),
            "classification": classification,
            "intensity_mph": int(raw["intensity"]) if str(raw.get("intensity", "")).isdigit() else None,
            "pressure_mb": int(raw["pressure"]) if str(raw.get("pressure", "")).isdigit() else None,
            "latitude": raw.get("latitude"),
            "longitude_text": raw.get("longitude"),
            "longitude": lon,
            "movement_degrees": raw.get("movementDir"),
            "movement_mph": raw.get("movementSpeed"),
            "zone": zone_for(str(raw), lon),
            "last_update": raw.get("lastUpdate"),
            "advisory_url": (raw.get("publicAdvisory") or {}).get("url"),
        })
    return storms


def parse_alerts(payload: dict, state: str) -> list[dict]:
    alerts = []
    for feature in payload.get("features", []):
        props = feature.get("properties") or {}
        event = str(props.get("event") or "")
        headline = str(props.get("headline") or event)
        searchable = f"{event} {headline}".lower()
        if not any(term in searchable for term in RELEVANT_ALERT_TERMS):
            continue
        alerts.append({
            "id": f"alert:{props.get('id') or feature.get('id')}",
            "kind": "coastal_alert",
            "state": state,
            "event": event,
            "headline": compact(headline, 240),
            "severity": props.get("severity"),
            "urgency": props.get("urgency"),
            "area": compact(str(props.get("areaDesc") or ""), 220),
            "effective": props.get("effective"),
            "expires": props.get("expires"),
            "url": props.get("@id") or feature.get("id"),
            "zone": ZONES[5],
        })
    return alerts


def choose_output_directory(override: str | None) -> Path:
    candidates: list[Path] = []
    if override:
        candidates.append(Path(override).expanduser())
    env_dir = os.environ.get("HURRICANE_REPORT_DIR")
    if env_dir:
        candidates.append(Path(env_dir).expanduser())
    # Pyto's writable local Documents directory.
    candidates.append(Path.home() / "Documents" / "Hurricane Reports")
    # Safe fallback for regular desktop Python and unusual Pyto configurations.
    candidates.append(Path.cwd() / "Hurricane Reports")
    candidates.append(Path(tempfile.gettempdir()) / "Hurricane Reports")

    errors = []
    for candidate in candidates:
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            probe = candidate / ".write_test"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink()
            return candidate
        except OSError as exc:
            errors.append(f"{candidate}: {exc}")
    raise PermissionError("No writable report folder found:\n" + "\n".join(errors))


def read_history(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def item_map(snapshot: dict, key: str) -> dict[str, dict]:
    return {item["id"]: item for item in snapshot.get(key, []) if item.get("id")}


def compare_snapshots(previous: dict, current: dict) -> tuple[list[str], bool]:
    if not previous:
        return ["First run: baseline saved for future comparisons."], bool(
            current.get("data_health") == "unavailable"
            or current["active_storms"] or current["alerts"]
            or any((x.get("probability_7d") or 0) >= 40 for x in current["disturbances"])
        )

    changes: list[str] = []
    alert_required = False
    for key, label in (("disturbances", "disturbance"), ("active_storms", "Atlantic storm"), ("alerts", "coastal alert")):
        before, after = item_map(previous, key), item_map(current, key)
        for item_id in sorted(after.keys() - before.keys()):
            item = after[item_id]
            changes.append(f"New {label}: {item.get('name') or item.get('event') or item.get('headline')}.")
            if key != "disturbances" or (item.get("probability_7d") or 0) >= 40:
                alert_required = True
        for item_id in sorted(before.keys() - after.keys()):
            item = before[item_id]
            changes.append(f"No longer listed: {item.get('name') or item.get('event') or item.get('headline')}.")

    old_dist, new_dist = item_map(previous, "disturbances"), item_map(current, "disturbances")
    for item_id in sorted(old_dist.keys() & new_dist.keys()):
        old, new = old_dist[item_id], new_dist[item_id]
        for field, label in (("probability_48h", "48-hour"), ("probability_7d", "7-day")):
            a, b = old.get(field), new.get(field)
            if a is not None and b is not None and a != b:
                changes.append(f"{new['name']}: {label} formation chance changed from {a}% to {b}%.")
                if b > a and (b >= 40 or b - a >= 20):
                    alert_required = True

    old_storms, new_storms = item_map(previous, "active_storms"), item_map(current, "active_storms")
    for item_id in sorted(old_storms.keys() & new_storms.keys()):
        old, new = old_storms[item_id], new_storms[item_id]
        if old.get("classification") != new.get("classification"):
            changes.append(f"{new['name']} changed from {old.get('classification')} to {new.get('classification')}.")
            alert_required = True
        a, b = old.get("intensity_mph"), new.get("intensity_mph")
        if a is not None and b is not None and a != b:
            changes.append(f"{new['name']} maximum winds changed from {a} to {b} mph.")
            if b > a:
                alert_required = True

    old_level = previous.get("status", {}).get("rank", 0)
    new_level = current.get("status", {}).get("rank", 0)
    if new_level > old_level:
        changes.append(f"Overall status increased to {current['status']['label']}.")
        alert_required = True
    if previous.get("data_health") != "unavailable" and current.get("data_health") == "unavailable":
        changes.append("Core NHC feeds are unavailable; the report may be incomplete.")
        alert_required = True
    return changes or ["No meaningful changes detected since the prior run."], alert_required


def calculate_status(disturbances: list[dict], storms: list[dict], alerts: list[dict]) -> dict:
    reasons = []
    rank = 0
    if disturbances:
        rank = 1
        reasons.append(f"{len(disturbances)} NHC development area(s)")
    maximum = max((x.get("probability_7d") or x.get("probability_48h") or 0 for x in disturbances), default=0)
    if maximum >= 40:
        rank = max(rank, 2)
        reasons.append(f"formation probability reaches {maximum}%")
    if storms:
        rank = max(rank, 2)
        reasons.append(f"{len(storms)} active Atlantic cyclone(s)")
    if alerts:
        rank = 3
        reasons.append(f"{len(alerts)} relevant lower East Coast alert(s)")
    labels = ("GREEN — QUIET", "YELLOW — MONITOR", "ORANGE — WATCH", "RED — ELEVATED")
    return {"rank": rank, "label": labels[rank], "reason": "; ".join(reasons) or "No tracked hazards identified"}


def fmt_probability(item: dict) -> str:
    p48 = "not stated" if item.get("probability_48h") is None else f"{item['probability_48h']}%"
    p7 = "not stated" if item.get("probability_7d") is None else f"{item['probability_7d']}%"
    return f"48-hour: {p48}; 7-day: {p7}"


def build_report(snapshot: dict, changes: list[str], errors: list[str], alert_required: bool, output_dir: Path) -> str:
    generated = datetime.fromisoformat(snapshot["generated_at"].replace("Z", "+00:00"))
    lines = [
        "ATLANTIC HURRICANE REPORT — VERSION 2",
        f"Generated: {generated.astimezone().strftime('%A, %B %d, %Y at %I:%M %p %Z')}",
        f"Mode: {'OFFLINE DEMONSTRATION — NOT WEATHER INFORMATION' if snapshot.get('sample') else 'LIVE OFFICIAL DATA'}",
        "",
        "30-SECOND QUICK LOOK",
        f"Overall status: {snapshot['status']['label']}",
        f"Why: {snapshot['status']['reason']}",
        f"Tropical waves discussed by NHC: {len(snapshot['tropical_waves'])}",
        f"Official development areas: {len(snapshot['disturbances'])}",
        f"Active Atlantic cyclones: {len(snapshot['active_storms'])}",
        f"Relevant FL/GA/SC/NC/VA alerts: {len(snapshot['alerts'])}",
        f"Immediate lower East Coast signal: {'Review active storms/alerts below' if snapshot['active_storms'] or snapshot['alerts'] else 'None identified in the tracked official feeds'}",
        f"Shortcut notification requested: {'YES' if alert_required else 'NO'}",
        "",
        "CHANGES SINCE PRIOR RUN",
    ]
    lines.extend(f"• {change}" for change in changes)
    lines.extend(["", "ATLANTIC ZONES"])
    all_systems = snapshot["disturbances"] + snapshot["tropical_waves"] + snapshot["active_storms"]
    for zone in ZONES:
        items = [item for item in all_systems if item.get("zone") == zone]
        lines.extend(["", zone.upper()])
        if not items:
            lines.append("• No tracked systems.")
            continue
        for item in items:
            if item["kind"] == "disturbance":
                lines.append(f"• DISTURBANCE — {item['name']} ({fmt_probability(item)})")
                lines.append(f"  {item['summary']}")
            elif item["kind"] == "tropical_wave":
                lines.append(f"• TROPICAL WAVE — {item['name']} — {item['movement']}")
                lines.append(f"  {item['summary']}")
            else:
                wind = f", maximum winds {item['intensity_mph']} mph" if item.get("intensity_mph") is not None else ""
                lines.append(f"• ACTIVE: {item['classification']} {item['name']}{wind}")
                lines.append(
                    f"  Position {item.get('latitude') or '?'} {item.get('longitude_text') or '?'}, "
                    f"moving {item.get('movement_degrees') or '?'}° at {item.get('movement_mph') or '?'} mph."
                )
                if item.get("advisory_url"):
                    lines.append(f"  Official advisory: {item['advisory_url']}")

    lines.extend(["", "LOWER U.S. EAST COAST ALERTS (FL, GA, SC, NC, VA)"])
    if not snapshot["alerts"]:
        lines.append("• No matching active NWS alerts.")
    for alert in snapshot["alerts"]:
        lines.append(f"• {alert['state']} — {alert['event']} ({alert.get('severity') or 'severity not stated'})")
        lines.append(f"  {alert['headline']}")
        lines.append(f"  Area: {alert['area']}")
        if alert.get("url"):
            lines.append(f"  Official alert: {alert['url']}")

    if errors:
        lines.extend(["", "DATA SOURCE NOTES"])
        lines.extend(f"• {error}" for error in errors)
    lines.extend([
        "",
        "FILES",
        f"Saved in: {output_dir}",
        "",
        "OFFICIAL SOURCES",
        f"NHC Atlantic outlook: {NHC_OUTLOOK_URL}",
        f"NHC Atlantic discussion: {NHC_DISCUSSION_URL}",
        f"NHC active cyclones: {NHC_STORMS_URL}",
        f"NWS active alerts: {NWS_ALERTS_URL}",
        "",
        "SAFETY NOTE",
        "This automated summary can miss nuance or fail when a source changes. It does not predict landfall.",
        "Use the linked NHC/NWS products and follow instructions from public safety officials.",
        "",
        f"ALERT_REQUIRED={'true' if alert_required else 'false'}",
    ])
    return "\n".join(lines) + "\n"


def atomic_write(path: Path, content: str) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", help="Override report folder (normally auto-detected for Pyto).")
    parser.add_argument("--fixtures", help="Read TWOAT.xml, TWDAT.xml, CurrentStorms.json and alerts_STATE.json from this folder.")
    parser.add_argument("--sample", action="store_true", help="Use fictional built-in data and make no network requests.")
    parser.add_argument("--print-report", "--print", action="store_true", help="Print the full report, not only the Shortcuts flag.")
    args = parser.parse_args(argv)
    sample_default = str(Path.home() / "Documents" / "Hurricane Reports Demo") if args.sample and not args.output_dir else None
    output_dir = choose_output_directory(args.output_dir or sample_default)
    fixture_dir = Path(args.fixtures) if args.fixtures else None
    errors: list[str] = []

    def get_rss(filename: str, url: str) -> tuple[str, str]:
        if fixture_dir:
            root = ET.fromstring((fixture_dir / filename).read_bytes())
            item = root.find(".//item")
            if item is None:
                raise ValueError(f"{filename} has no RSS item")
            return clean_text(item.findtext("title")), clean_text(item.findtext("description"))
        return fetch_rss_text(url)

    try:
        _, outlook_text = ("Sample outlook", SAMPLE_OUTLOOK_TEXT) if args.sample else get_rss("TWOAT.xml", NHC_OUTLOOK_URL)
        disturbances = parse_outlook(outlook_text)
    except Exception as exc:
        disturbances = []
        errors.append(f"NHC outlook unavailable: {type(exc).__name__}: {exc}")
    try:
        _, discussion_text = ("Sample discussion", SAMPLE_DISCUSSION_TEXT) if args.sample else get_rss("TWDAT.xml", NHC_DISCUSSION_URL)
        waves = parse_tropical_waves(discussion_text)
    except Exception as exc:
        waves = []
        errors.append(f"NHC discussion unavailable: {type(exc).__name__}: {exc}")
    try:
        if args.sample:
            storms_payload = SAMPLE_STORMS
        else:
            storms_payload = json.loads((fixture_dir / "CurrentStorms.json").read_text()) if fixture_dir else fetch_json(NHC_STORMS_URL)
        storms = parse_active_storms(storms_payload)
    except Exception as exc:
        storms = []
        errors.append(f"NHC active storms unavailable: {type(exc).__name__}: {exc}")

    alerts: list[dict] = []
    for state in WATCH_STATES:
        try:
            if args.sample:
                payload = SAMPLE_ALERT if state == "FL" else {"features": []}
            elif fixture_dir:
                payload = json.loads((fixture_dir / f"alerts_{state}.json").read_text())
            else:
                payload = fetch_json(f"{NWS_ALERTS_URL}?{urlencode({'area': state, 'status': 'actual'})}")
            alerts.extend(parse_alerts(payload, state))
        except Exception as exc:
            errors.append(f"NWS alerts for {state} unavailable: {type(exc).__name__}: {exc}")

    status = calculate_status(disturbances, storms, alerts)
    core_failures = sum(
        any(error.startswith(prefix) for error in errors)
        for prefix in ("NHC outlook", "NHC discussion", "NHC active storms")
    )
    data_health = "unavailable" if core_failures == 3 else ("degraded" if errors else "complete")
    if data_health == "unavailable":
        status = {
            "rank": 2,
            "label": "GRAY — DATA UNAVAILABLE",
            "reason": "All core NHC feeds failed; do not interpret missing systems as quiet conditions",
        }
    snapshot = {
        "schema_version": 2,
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "sample": args.sample,
        "status": status,
        "data_health": data_health,
        "disturbances": disturbances,
        "tropical_waves": waves,
        "active_storms": storms,
        "alerts": alerts,
        "source_errors": errors,
    }
    state_path = output_dir / "hurricane_state.json"
    history = read_history(state_path)
    previous = history.get("current") or {}
    changes, alert_required = compare_snapshots(previous, snapshot)
    report = build_report(snapshot, changes, errors, alert_required, output_dir)

    latest_path = output_dir / "latest_report.txt"
    archive_path = output_dir / f"report_{datetime.now().astimezone():%Y-%m-%d}.txt"
    atomic_write(latest_path, report)
    atomic_write(archive_path, report)
    runs = list(history.get("history", []))
    if previous:
        runs.append(previous)
    history_doc = {"schema_version": 2, "current": snapshot, "history": runs[-30:]}
    atomic_write(state_path, json.dumps(history_doc, indent=2, ensure_ascii=False) + "\n")

    if args.print_report:
        print(report, end="")
    else:
        print(f"Report saved: {latest_path}")
        print(f"ALERT_REQUIRED={'true' if alert_required else 'false'}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("Cancelled.", file=sys.stderr)
        raise SystemExit(130)
    except (OSError, HTTPError, URLError, ValueError) as exc:
        print(f"Unable to create report: {exc}", file=sys.stderr)
        raise SystemExit(1)
