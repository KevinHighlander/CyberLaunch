#!/usr/bin/env python3
"""Download newly posted ENGL 200 files from Campuswire.

The watcher uses a persistent Playwright browser profile so credentials never
need to be stored in this project. Run ``login`` once, then ``baseline`` to
mark current files as seen, and use ``scan`` for subsequent checks.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote, urljoin, urlparse

try:
    from playwright.sync_api import (
        BrowserContext,
        Download,
        Page,
        TimeoutError as PlaywrightTimeoutError,
        sync_playwright,
    )
except ImportError:
    print("Playwright is not installed. Run ./0-install.command first.", file=sys.stderr)
    raise SystemExit(2)


COURSE_URL = "https://campuswire.com/c/G7F2FCEEC/modules/files"
DEFAULT_DOWNLOAD_DIR = Path.home() / "Downloads" / "ENGL 200 Slides"
APP_DIR = Path.home() / ".engl200-campuswire-downloader"
PROFILE_DIR = APP_DIR / "browser-profile"
HISTORY_FILE = APP_DIR / "download_history.json"
DEBUG_DIR = APP_DIR / "debug"
SUPPORTED_EXTENSIONS = {
    ".pdf", ".ppt", ".pptx", ".key", ".doc", ".docx",
}
FILE_URL_HINTS = (
    "files.campuswire.com",
    "storage.googleapis.com",
    "amazonaws.com",
)


@dataclass(frozen=True)
class FileLink:
    url: str
    name: str

    @property
    def identity(self) -> str:
        """Stable identity that ignores URL fragments but preserves queries."""
        parsed = urlparse(self.url)
        clean_url = parsed._replace(fragment="").geturl()
        return hashlib.sha256(clean_url.encode("utf-8")).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_history() -> dict:
    if not HISTORY_FILE.exists():
        return {"version": 1, "course_url": COURSE_URL, "files": {}}
    try:
        data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Could not read history file {HISTORY_FILE}: {exc}") from exc
    if not isinstance(data.get("files"), dict):
        raise RuntimeError(f"History file has an invalid format: {HISTORY_FILE}")
    return data


def save_history(history: dict) -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    temp_file = HISTORY_FILE.with_suffix(".tmp")
    temp_file.write_text(
        json.dumps(history, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    os.chmod(temp_file, 0o600)
    temp_file.replace(HISTORY_FILE)


def safe_filename(value: str, fallback: str = "campuswire-file") -> str:
    value = unquote(value).strip()
    value = re.sub(r"[\x00-\x1f/:\\?*\"<>|]", "_", value)
    value = re.sub(r"\s+", " ", value).strip(" .")
    return value[:180] or fallback


def name_from_url(url: str) -> str:
    return safe_filename(Path(unquote(urlparse(url).path)).name)


def supported(name_or_url: str) -> bool:
    path = unquote(urlparse(name_or_url).path)
    return Path(path).suffix.lower() in SUPPORTED_EXTENSIONS


def unique_destination(directory: Path, filename: str) -> Path:
    destination = directory / safe_filename(filename)
    if not destination.exists():
        return destination
    stem, suffix = destination.stem, destination.suffix
    counter = 2
    while True:
        candidate = directory / f"{stem} ({counter}){suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def discover_links(page: Page) -> list[FileLink]:
    """Collect supported attachment links visible in the rendered page."""
    raw_links = page.locator("a[href]").evaluate_all(
        """elements => elements.map(a => ({
            href: a.href,
            text: (a.innerText || a.getAttribute('aria-label') ||
                   a.getAttribute('title') || '').trim(),
            download: a.getAttribute('download') || ''
        }))"""
    )
    found: dict[str, FileLink] = {}
    for raw in raw_links:
        url = urljoin(page.url, raw.get("href", ""))
        label = raw.get("download") or raw.get("text") or name_from_url(url)
        hinted_host = any(hint in urlparse(url).netloc for hint in FILE_URL_HINTS)
        if not (supported(url) or supported(label) or hinted_host):
            continue
        filename = safe_filename(label)
        if not supported(filename):
            url_name = name_from_url(url)
            if supported(url_name):
                filename = url_name
            else:
                continue
        link = FileLink(url=url, name=filename)
        found.setdefault(link.identity, link)
    return list(found.values())


def wait_for_course_page(page: Page) -> None:
    page.goto(COURSE_URL, wait_until="domcontentloaded", timeout=60_000)
    try:
        page.wait_for_load_state("networkidle", timeout=15_000)
    except PlaywrightTimeoutError:
        pass
    page.wait_for_timeout(2_000)


def make_context(playwright, headless: bool) -> BrowserContext:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    context = playwright.chromium.launch_persistent_context(
        str(PROFILE_DIR),
        headless=headless,
        accept_downloads=True,
        viewport={"width": 1440, "height": 1000},
    )
    return context


def login() -> int:
    print("A browser will open. Log into Campuswire normally.")
    print("When the ENGL 200 Files page is visible, return here and press Enter.")
    with sync_playwright() as playwright:
        context = make_context(playwright, headless=False)
        page = context.pages[0] if context.pages else context.new_page()
        wait_for_course_page(page)
        input()
        context.close()
    print("Login session saved locally.")
    return 0


def record_entry(history: dict, link: FileLink, status: str, path: Path | None = None) -> None:
    history["files"][link.identity] = {
        "url": link.url,
        "name": link.name,
        "status": status,
        "first_seen": utc_now(),
        **({"saved_path": str(path)} if path else {}),
    }
    history["last_scan"] = utc_now()


def download_link(page: Page, link: FileLink, directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    destination = unique_destination(directory, link.name)
    try:
        response = page.context.request.get(link.url, timeout=60_000)
        if not response.ok:
            raise RuntimeError(f"HTTP {response.status}")
        destination.write_bytes(response.body())
        return destination
    except Exception as request_error:
        # Some attachment endpoints require browser navigation to trigger download.
        try:
            with page.expect_download(timeout=60_000) as download_info:
                page.evaluate("(url) => window.location.href = url", link.url)
            download: Download = download_info.value
            suggested = download.suggested_filename or link.name
            destination = unique_destination(directory, suggested)
            download.save_as(str(destination))
            return destination
        except Exception as browser_error:
            raise RuntimeError(
                f"request failed ({request_error}); browser download failed ({browser_error})"
            ) from browser_error


def scan(mode: str, visible: bool, download_dir: Path) -> int:
    history = load_history()
    with sync_playwright() as playwright:
        context = make_context(playwright, headless=not visible)
        page = context.pages[0] if context.pages else context.new_page()
        try:
            wait_for_course_page(page)
            if "login" in page.url.lower() or "sign" in page.url.lower():
                print("Campuswire needs a fresh login. Run ./1-login.command.", file=sys.stderr)
                return 3
            links = discover_links(page)
            if not links:
                print("No supported files were found.")
                print("If files are visible in Campuswire, run ./4-visible-debug-scan.command.")
            new_links = [item for item in links if item.identity not in history["files"]]
            if mode == "baseline":
                for link in new_links:
                    record_entry(history, link, "baseline")
                save_history(history)
                print(f"Baseline complete: {len(links)} file(s) recorded; nothing downloaded.")
                return 0

            downloaded = 0
            failed = 0
            for link in new_links:
                try:
                    path = download_link(page, link, download_dir)
                    record_entry(history, link, "downloaded", path)
                    save_history(history)
                    downloaded += 1
                    print(f"Downloaded: {path.name}")
                except Exception as exc:
                    failed += 1
                    print(f"Could not download {link.name}: {exc}", file=sys.stderr)
            history["last_scan"] = utc_now()
            save_history(history)
            print(
                f"Scan complete: {downloaded} new file(s) downloaded, "
                f"{len(links) - len(new_links)} already seen, {failed} failed."
            )
            return 1 if failed else 0
        finally:
            if visible and mode == "debug":
                DEBUG_DIR.mkdir(parents=True, exist_ok=True)
                stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                screenshot = DEBUG_DIR / f"campuswire-{stamp}.png"
                html = DEBUG_DIR / f"campuswire-{stamp}.html"
                page.screenshot(path=str(screenshot), full_page=True)
                html.write_text(page.content(), encoding="utf-8")
                print(f"Private diagnostic files saved in {DEBUG_DIR}")
            context.close()


def reset_history() -> int:
    if HISTORY_FILE.exists():
        backup = HISTORY_FILE.with_name(
            f"download_history-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        )
        shutil.move(HISTORY_FILE, backup)
        print(f"History reset. Backup: {backup}")
    else:
        print("No history file exists yet.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("login", help="Open a browser and save the Campuswire session")
    subparsers.add_parser("baseline", help="Record current files without downloading")
    scan_parser = subparsers.add_parser("scan", help="Download newly discovered files")
    scan_parser.add_argument("--visible", action="store_true", help="Show the browser")
    debug_parser = subparsers.add_parser("debug", help="Run a visible scan and save diagnostics")
    debug_parser.add_argument(
        "--download-dir", type=Path, default=DEFAULT_DOWNLOAD_DIR
    )
    subparsers.add_parser("reset-history", help="Back up and reset file history")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "login":
        return login()
    if args.command == "baseline":
        return scan("baseline", visible=False, download_dir=DEFAULT_DOWNLOAD_DIR)
    if args.command == "scan":
        return scan("scan", visible=args.visible, download_dir=DEFAULT_DOWNLOAD_DIR)
    if args.command == "debug":
        return scan("debug", visible=True, download_dir=args.download_dir)
    if args.command == "reset-history":
        return reset_history()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

