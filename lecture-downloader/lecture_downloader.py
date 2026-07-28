#!/usr/bin/env python3
"""Safe downloader for user-authorized course material sources."""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
import shutil
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import unquote, urljoin, urlparse

import requests

APP_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG = APP_DIR / "config.json"
SAMPLE_CONFIG = APP_DIR / "samples" / "config.sample.json"
CHUNK_SIZE = 64 * 1024
USER_AGENT = "CyberLaunch-Lecture-Downloader/1.0"


@dataclass(frozen=True)
class Item:
    url: str
    filename: str = ""


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._href: str | None = None
        self._download = ""
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        values = dict(attrs)
        self._href = values.get("href")
        self._download = values.get("download") or ""
        self._text = []

    def handle_data(self, data: str) -> None:
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._href is not None:
            self.links.append((self._href, self._download or " ".join(self._text)))
            self._href = None


def safe_name(value: str, fallback: str = "download") -> str:
    value = unquote(value).strip()
    value = re.sub(r"[\x00-\x1f/:\\?*\"<>|]", "_", value)
    value = re.sub(r"\s+", " ", value).strip(" .")
    return value[:180] or fallback


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"File not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return data


def resolve_local(value: str, base_dir: Path) -> Path:
    path = Path(value).expanduser()
    return (base_dir / path).resolve() if not path.is_absolute() else path.resolve()


def extension_set(config: dict[str, Any]) -> set[str]:
    raw = config.get("extensions", [".pdf", ".pptx", ".docx", ".txt"])
    if not isinstance(raw, list) or not raw:
        raise ValueError("'extensions' must be a non-empty list")
    return {str(ext).lower() if str(ext).startswith(".") else f".{str(ext).lower()}" for ext in raw}


def validate_remote_url(url: str, allowed_hosts: set[str]) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError(f"Remote URLs must use HTTPS: {url}")
    if parsed.username or parsed.password:
        raise ValueError("Credentials must not be embedded in URLs")
    if parsed.hostname.lower() not in allowed_hosts:
        raise ValueError(f"Host is not allowlisted: {parsed.hostname}")


def make_session() -> requests.Session:
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    return session


def fetch(session: requests.Session, url: str, allowed_hosts: set[str], timeout: int, *, stream: bool = False) -> requests.Response:
    validate_remote_url(url, allowed_hosts)
    response = session.get(url, timeout=timeout, stream=stream, allow_redirects=True)
    response.raise_for_status()
    validate_remote_url(response.url, allowed_hosts)
    return response


def filename_for(item: Item, final_url: str, extensions: set[str]) -> str:
    candidate = safe_name(item.filename, "") or safe_name(Path(unquote(urlparse(final_url).path)).name)
    if Path(candidate).suffix.lower() not in extensions:
        raise ValueError(f"Unsupported file type: {candidate}")
    return candidate


def items_from_manifest(path: Path) -> list[Item]:
    data = load_json(path)
    raw = data.get("files")
    if not isinstance(raw, list):
        raise ValueError(f"Manifest needs a 'files' list: {path}")
    items: list[Item] = []
    for entry in raw:
        if isinstance(entry, str):
            items.append(Item(entry))
        elif isinstance(entry, dict) and isinstance(entry.get("url"), str):
            items.append(Item(entry["url"], str(entry.get("filename", ""))))
        else:
            raise ValueError(f"Invalid manifest entry in {path}")
    return items


def discover_html(text: str, base_url: str, extensions: set[str], allowed_hosts: set[str]) -> list[Item]:
    parser = LinkParser()
    parser.feed(text)
    found: dict[str, Item] = {}
    for href, label in parser.links:
        url = urljoin(base_url, href)
        parsed = urlparse(url)
        if parsed.scheme == "https":
            validate_remote_url(url, allowed_hosts)
        elif parsed.scheme not in {"", "file"}:
            continue
        suffix = Path(unquote(parsed.path)).suffix.lower()
        label_suffix = Path(label.strip()).suffix.lower()
        if suffix in extensions or label_suffix in extensions:
            found.setdefault(url, Item(url, label.strip()))
    return list(found.values())


def discover_source(source: dict[str, Any], config_dir: Path, session: requests.Session, extensions: set[str], allowed_hosts: set[str], timeout: int) -> list[Item]:
    kind = source.get("type")
    value = source.get("path") if kind in {"manifest", "html"} else source.get("url")
    if not isinstance(value, str):
        raise ValueError("Every source needs a string path or url")
    if kind == "manifest":
        return items_from_manifest(resolve_local(value, config_dir))
    if kind == "html":
        path = resolve_local(value, config_dir)
        return discover_html(path.read_text(encoding="utf-8"), path.as_uri(), extensions, allowed_hosts)
    if kind == "html_url":
        with fetch(session, value, allowed_hosts, timeout) as response:
            if "html" not in response.headers.get("Content-Type", "").lower():
                raise ValueError(f"HTML source returned another content type: {value}")
            return discover_html(response.text, response.url, extensions, allowed_hosts)
    if kind == "url":
        return [Item(value, str(source.get("filename", "")))]
    raise ValueError(f"Unsupported source type: {kind!r}")


def unique_path(directory: Path, filename: str) -> Path:
    target = directory / filename
    counter = 2
    while target.exists():
        target = directory / f"{Path(filename).stem} ({counter}){Path(filename).suffix}"
        counter += 1
    return target


def save_item(item: Item, destination: Path, config_dir: Path, session: requests.Session, extensions: set[str], allowed_hosts: set[str], timeout: int, max_bytes: int) -> tuple[Path, str, int]:
    parsed = urlparse(item.url)
    response: requests.Response | None = None
    if parsed.scheme == "https":
        response = fetch(session, item.url, allowed_hosts, timeout, stream=True)
        final_url = response.url
        chunks: Iterable[bytes] = response.iter_content(CHUNK_SIZE)
        announced = int(response.headers.get("Content-Length", "0") or 0)
        if announced > max_bytes:
            response.close()
            raise ValueError("File exceeds the configured size limit")
    elif parsed.scheme in {"", "file"}:
        source_path = Path(unquote(parsed.path)) if parsed.scheme == "file" else resolve_local(item.url, config_dir)
        if not source_path.is_file():
            raise ValueError(f"Local source not found: {source_path}")
        final_url = source_path.as_uri()
        chunks = ()
    else:
        raise ValueError(f"Unsupported URL scheme: {parsed.scheme}")

    filename = filename_for(item, final_url, extensions)
    destination.mkdir(parents=True, exist_ok=True)
    temporary = destination / f".{filename}.part"
    digest = hashlib.sha256()
    total = 0
    source_handle = None
    try:
        if parsed.scheme in {"", "file"}:
            source_path = Path(unquote(parsed.path)) if parsed.scheme == "file" else resolve_local(item.url, config_dir)
            source_handle = source_path.open("rb")
            chunks = iter(lambda: source_handle.read(CHUNK_SIZE), b"")
        with temporary.open("wb") as output:
            for chunk in chunks:
                total += len(chunk)
                if total > max_bytes:
                    raise ValueError("File exceeds the configured size limit")
                digest.update(chunk)
                output.write(chunk)
        return temporary, digest.hexdigest(), total
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    finally:
        if source_handle:
            source_handle.close()
        if response:
            response.close()


def run(config_path: Path, *, dry_run: bool = False, baseline: bool = False) -> int:
    config = load_json(config_path)
    config_dir = config_path.resolve().parent
    extensions = extension_set(config)
    allowed_hosts = {str(host).lower() for host in config.get("allowed_hosts", [])}
    timeout = int(config.get("timeout_seconds", 30))
    max_bytes = int(config.get("max_file_size_mb", 100)) * 1024 * 1024
    output_dir = resolve_local(str(config.get("download_dir", "downloads")), config_dir)
    state_path = resolve_local(str(config.get("state_file", ".lecture-downloader-state.json")), config_dir)
    state = load_json(state_path) if state_path.exists() else {"urls": {}, "hashes": {}}
    courses = config.get("courses")
    if not isinstance(courses, list) or not courses:
        raise ValueError("'courses' must be a non-empty list")
    session = make_session()
    failures = 0
    for course in courses:
        if not isinstance(course, dict) or not isinstance(course.get("sources"), list):
            raise ValueError("Each course needs a name and sources list")
        name = safe_name(str(course.get("name", "")), "")
        if not name:
            raise ValueError("Each course needs a name")
        items: dict[str, Item] = {}
        for source in course["sources"]:
            if not isinstance(source, dict):
                raise ValueError("Sources must be objects with a type")
            for item in discover_source(source, config_dir, session, extensions, allowed_hosts, timeout):
                items.setdefault(item.url, item)
        course_state = state["urls"].setdefault(name, {})
        new_items = [item for item in items.values() if item.url not in course_state]
        for item in new_items:
            if dry_run:
                print(f"WOULD DOWNLOAD [{name}] {item.url}")
                continue
            if baseline:
                course_state[item.url] = {"status": "baseline"}
                continue
            try:
                temporary, digest, size = save_item(item, output_dir / safe_name(str(course.get("folder", name))), config_dir, session, extensions, allowed_hosts, timeout, max_bytes)
                duplicate = state["hashes"].get(digest)
                if duplicate:
                    temporary.unlink()
                    course_state[item.url] = {"status": "duplicate", "same_as": duplicate, "sha256": digest}
                    print(f"DUPLICATE [{name}] {item.url}")
                else:
                    target = unique_path(temporary.parent, temporary.name[1:-5])
                    temporary.replace(target)
                    state["hashes"][digest] = str(target)
                    course_state[item.url] = {"status": "downloaded", "path": str(target), "sha256": digest, "bytes": size}
                    print(f"DOWNLOADED [{name}] {target}")
            except Exception as exc:
                failures += 1
                logging.error("%s: %s", item.url, exc)
    if not dry_run:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_state = state_path.with_suffix(state_path.suffix + ".tmp")
        temporary_state.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temporary_state.replace(state_path)
    return 1 if failures else 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--sample", action="store_true", help="run the bundled offline demonstration")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--baseline", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    config = SAMPLE_CONFIG if args.sample else args.config
    try:
        return run(config, dry_run=args.dry_run, baseline=args.baseline)
    except (ValueError, OSError, requests.RequestException) as exc:
        logging.error("%s", exc)
        return 2


if __name__ == "__main__":
    sys.exit(main())
