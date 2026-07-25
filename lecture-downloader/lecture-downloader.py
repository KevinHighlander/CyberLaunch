#!/usr/bin/env python3
"""Download newly posted course files from authorized pages or direct links."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import logging
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

try:
    from playwright.sync_api import BrowserContext, TimeoutError as PlaywrightTimeout
    from playwright.sync_api import sync_playwright
except ImportError:
    BrowserContext = Any  # type: ignore[assignment,misc]
    PlaywrightTimeout = TimeoutError
    sync_playwright = None

APP_NAME = "lecture-downloader"
DEFAULT_CONFIG = Path(__file__).with_name("config.json")
DEFAULT_STATE_DIR = Path.home() / ".local" / "share" / APP_NAME
DEFAULT_DOWNLOAD_DIR = Path.home() / "Downloads" / "CyberLaunch Lectures"
DEFAULT_EXTENSIONS = [".pdf", ".ppt", ".pptx", ".key", ".doc", ".docx"]
USER_AGENT = "CyberLaunch-Lecture-Downloader/1.0"
CHUNK_SIZE = 64 * 1024
CAMPUSWIRE_HOSTS = {"campuswire.com", "www.campuswire.com"}


@dataclass(frozen=True)
class Candidate:
    url: str
    label: str = ""


def safe_name(value: str, fallback: str = "download") -> str:
    value = unquote(value).strip()
    value = re.sub(r"[\x00-\x1f/:\\?*\"<>|]", "_", value)
    value = re.sub(r"\s+", " ", value).strip(" .")
    return value[:180] or fallback


def extension_from(value: str) -> str:
    return Path(unquote(urlparse(value).path)).suffix.lower()


def supported_extension(value: str, extensions: set[str]) -> str:
    decoded = unquote(value).lower()
    for extension in sorted(extensions, key=len, reverse=True):
        if re.search(rf"{re.escape(extension)}(?:$|[?&#\s\"'<>),\]])", decoded):
            return extension
    return ""


def filename_from_label(label: str, extensions: set[str]) -> str:
    decoded = unquote(label).strip()
    extension = supported_extension(decoded, extensions)
    if not extension:
        return ""
    match = re.search(
        rf"([^/\\\n\r]+?{re.escape(extension)})(?:$|[?&#\s\"'<>),\]])",
        decoded,
        re.IGNORECASE,
    )
    return safe_name(match.group(1)) if match else ""


def urls_from_text(value: str) -> list[str]:
    normalized = html.unescape(value)
    normalized = normalized.replace("\\u002F", "/").replace("\\/", "/")
    return re.findall(r"https?://[^\s\"'<>]+", normalized)


def host_allowed(url: str, source_url: str, allowed_hosts: set[str]) -> bool:
    host = (urlparse(url).hostname or "").lower()
    source_host = (urlparse(source_url).hostname or "").lower()
    return bool(host) and (host == source_host or host in allowed_hosts)


def is_campuswire_url(url: str) -> bool:
    return (urlparse(url).hostname or "").lower() in CAMPUSWIRE_HOSTS


def env_mapping(mapping: dict[str, str], kind: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for output_name, variable_name in mapping.items():
        value = os.getenv(variable_name)
        if not value:
            raise ValueError(
                f"Required {kind} environment variable {variable_name!r} is not set"
            )
        result[output_name] = value
    return result


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(
            f"Configuration not found: {path}. Copy config.example.json to config.json."
        ) from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Configuration must be a JSON object")
    return data


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"version": 1, "urls": {}, "hashes": {}}
    data = load_json(path)
    if not isinstance(data.get("urls"), dict) or not isinstance(data.get("hashes"), dict):
        raise ValueError(f"Invalid state file: {path}")
    return data


def save_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", "utf-8")
    os.chmod(temporary, 0o600)
    temporary.replace(path)


def configure_logging(state_dir: Path, verbose: bool) -> None:
    state_dir.mkdir(parents=True, exist_ok=True)
    handlers: list[logging.Handler] = [
        logging.StreamHandler(),
        logging.FileHandler(state_dir / "lecture-downloader.log", encoding="utf-8"),
    ]
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=handlers,
    )


def make_session(course: dict[str, Any]) -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    auth = course.get("auth", {})
    if not isinstance(auth, dict):
        raise ValueError("'auth' must be an object")
    session.headers.update(env_mapping(auth.get("headers_from_env", {}), "header"))
    session.cookies.update(env_mapping(auth.get("cookies_from_env", {}), "cookie"))
    return session


def require_playwright() -> None:
    if sync_playwright is None:
        raise ValueError(
            "Campuswire browser support is not installed. Run "
            "'python3 -m pip install -r requirements.txt' and "
            "'python3 -m playwright install chromium'."
        )


def make_browser_context(playwright: Any, state_dir: Path, headless: bool) -> BrowserContext:
    profile_dir = state_dir / "browser-profile"
    profile_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(profile_dir, 0o700)
    try:
        return playwright.chromium.launch_persistent_context(
            str(profile_dir),
            headless=headless,
            accept_downloads=True,
            viewport={"width": 1440, "height": 1000},
        )
    except Exception as exc:
        raise ValueError(
            "Chromium is unavailable. Run 'python3 -m playwright install chromium'."
        ) from exc


def sync_browser_cookies(
    browser_context: BrowserContext, session: requests.Session
) -> None:
    for cookie in browser_context.cookies():
        session.cookies.set(
            cookie["name"],
            cookie["value"],
            domain=cookie.get("domain"),
            path=cookie.get("path", "/"),
        )


def discover_browser(
    browser_context: BrowserContext,
    source: str,
    extensions: set[str],
    allowed_hosts: set[str],
    timeout: int,
    requested_tabs: list[str] | None = None,
    debug_dir: Path | None = None,
    debug_name: str = "campuswire",
) -> list[Candidate]:
    """Find file links across rendered tabs using the saved browser session."""
    page = browser_context.new_page()
    try:
        page.goto(source, wait_until="domcontentloaded", timeout=timeout * 1000)
        try:
            page.wait_for_load_state("networkidle", timeout=min(timeout, 15) * 1000)
        except PlaywrightTimeout:
            pass
        page.wait_for_timeout(2_000)
        current_url = page.url
        password_fields = page.locator('input[type="password"]').count()
        if "login" in current_url.lower() or password_fields:
            raise ValueError(
                "Campuswire login is required. Run "
                "'python3 lecture-downloader.py --login' first."
            )
        found: dict[str, Candidate] = {}
        network_candidates: list[Candidate] = []
        active_file_label = {"value": ""}

        def capture_file_response(response: Any) -> None:
            url = response.url
            content_type = response.headers.get("content-type", "").lower()
            is_supported_response = supported_extension(url, extensions) or any(
                marker in content_type
                for marker in (
                    "application/pdf",
                    "application/msword",
                    "application/vnd.openxmlformats",
                    "application/vnd.ms-powerpoint",
                )
            )
            if is_supported_response and host_allowed(
                url, page.url, allowed_hosts
            ):
                network_candidates.append(
                    Candidate(url=url, label=active_file_label["value"])
                )

        page.on("response", capture_file_response)

        def collect_current_view(view_name: str) -> tuple[int, str]:
            raw_elements = page.locator("*").evaluate_all(
                """elements => elements.map(link => ({
                    tag: link.tagName.toLowerCase(),
                    href: link.href || '',
                    label: (
                        link.getAttribute('download') ||
                        link.innerText ||
                        link.getAttribute('aria-label') ||
                        link.getAttribute('title') ||
                        ''
                    ).trim().slice(0, 500),
                    attributes: Array.from(link.attributes || []).map(
                        attribute => attribute.value
                    ).filter(Boolean)
                }))"""
            )
            for raw in raw_elements:
                label = raw.get("label", "")
                values = [raw.get("href", ""), *raw.get("attributes", [])]
                urls: list[str] = []
                for value in values:
                    if not value:
                        continue
                    urls.extend(urls_from_text(value))
                    if raw.get("tag") == "a" and value == raw.get("href"):
                        urls.append(urljoin(page.url, value))
                for url in urls:
                    url = url.rstrip(".,;)]}")
                    filename = filename_from_label(label, extensions)
                    if not supported_extension(url, extensions):
                        continue
                    if not host_allowed(url, page.url, allowed_hosts):
                        logging.warning("Blocked off-site discovered link: %s", url)
                        continue
                    found.setdefault(
                        url, Candidate(url=url, label=filename or label)
                    )

            view_html = page.content()
            for url in urls_from_text(view_html):
                url = url.rstrip(".,;)]}")
                if not supported_extension(url, extensions):
                    continue
                if host_allowed(url, page.url, allowed_hosts):
                    found.setdefault(url, Candidate(url=url))
            for candidate in network_candidates:
                found.setdefault(candidate.url, candidate)
            network_candidates.clear()
            logging.info(
                "Campuswire view %r inspected %d element(s)",
                view_name,
                len(raw_elements),
            )
            return len(raw_elements), view_html

        clicked_rows: set[str] = set()

        def candidate_already_found(filename: str) -> bool:
            expected = filename.casefold()
            for candidate in found.values():
                url_name = safe_name(
                    Path(unquote(urlparse(candidate.url).path)).name
                ).casefold()
                label_name = filename_from_label(
                    candidate.label, extensions
                ).casefold()
                if expected in {url_name, label_name}:
                    return True
            return False

        def inspect_clickable_file_rows(view_name: str) -> tuple[int, str]:
            inspected = 0
            latest = page.content()
            rows = page.locator(".group-files-list li")
            row_count = rows.count()
            for index in range(row_count):
                row = rows.nth(index)
                label = (row.inner_text() or "").strip()
                filename = filename_from_label(label, extensions)
                key = f"{view_name}:{index}:{filename}".casefold()
                if (
                    not filename
                    or key in clicked_rows
                    or candidate_already_found(filename)
                    or not row.is_visible()
                ):
                    continue
                clicked_rows.add(key)
                before = len(found)
                active_file_label["value"] = filename
                row.click()
                page.wait_for_timeout(750)
                count, latest = collect_current_view(f"{view_name}: {filename}")
                inspected += count
                if len(found) == before:
                    logging.warning(
                        "Campuswire file row did not expose a download URL: %s",
                        filename,
                    )
            active_file_label["value"] = ""
            return inspected, latest

        total_elements, latest_html = collect_current_view("default")
        count, latest_html = inspect_clickable_file_rows("default")
        total_elements += count

        visited_tabs: set[str] = set()
        role_tabs = page.locator('[role="tab"]')
        role_tab_count = role_tabs.count()
        for index in range(role_tab_count):
            tab = role_tabs.nth(index)
            tab_name = (tab.inner_text() or tab.get_attribute("aria-label") or "").strip()
            if not tab_name or tab_name in visited_tabs or not tab.is_visible():
                continue
            visited_tabs.add(tab_name)
            tab.click()
            page.wait_for_timeout(1_000)
            count, latest_html = collect_current_view(tab_name)
            total_elements += count
            count, latest_html = inspect_clickable_file_rows(tab_name)
            total_elements += count

        for tab_name in requested_tabs or []:
            if tab_name in visited_tabs:
                continue
            possible_tabs = page.get_by_text(
                re.compile(rf"^\s*{re.escape(tab_name)}\s*$", re.IGNORECASE)
            )
            try:
                possible_tabs.wait_for(state="visible", timeout=10_000)
            except PlaywrightTimeout:
                pass
            match_count = possible_tabs.count()
            if match_count != 1:
                logging.warning(
                    "Configured Campuswire tab %r matched %d element(s)",
                    tab_name,
                    match_count,
                )
                continue
            possible_tabs.click()
            page.wait_for_timeout(1_000)
            visited_tabs.add(tab_name)
            count, latest_html = collect_current_view(tab_name)
            total_elements += count
            count, latest_html = inspect_clickable_file_rows(tab_name)
            total_elements += count

        if debug_dir is not None:
            debug_dir.mkdir(parents=True, exist_ok=True)
            os.chmod(debug_dir, 0o700)
            debug_file = debug_dir / f"{safe_name(debug_name)}-page.html"
            debug_file.write_text(latest_html, encoding="utf-8")
            os.chmod(debug_file, 0o600)
            screenshot = debug_dir / f"{safe_name(debug_name)}-page.png"
            page.screenshot(path=str(screenshot), full_page=True)
            os.chmod(screenshot, 0o600)
            logging.info("Private diagnostics saved under %s", debug_dir)

        logging.info(
            "Rendered Campuswire page inspected %d view element(s) across "
            "%d tab(s) and found %d supported file link(s)",
            total_elements,
            len(visited_tabs) + 1,
            len(found),
        )
        return list(found.values())
    finally:
        page.close()


def campuswire_login(courses: list[dict[str, Any]], state_dir: Path) -> int:
    require_playwright()
    source = next(
        (
            str(source)
            for course in courses
            for source in course.get("sources", [])
            if is_campuswire_url(str(source))
        ),
        None,
    )
    if not source:
        raise ValueError("No Campuswire source was found in config.json")
    print("A private Chromium window will open.")
    print("Sign in to Campuswire normally and wait until the Files page is visible.")
    print("Then return to this Terminal window and press Return.")
    with sync_playwright() as playwright:
        context = make_browser_context(playwright, state_dir, headless=False)
        page = context.pages[0] if context.pages else context.new_page()
        try:
            page.goto(source, wait_until="domcontentloaded", timeout=60_000)
            input()
            if "login" in page.url.lower() or page.locator(
                'input[type="password"]'
            ).count():
                raise ValueError("Campuswire still appears to be on a login page")
            print("Campuswire session saved privately on this Mac.")
            return 0
        finally:
            context.close()


def discover(
    session: requests.Session,
    source: str,
    extensions: set[str],
    allowed_hosts: set[str],
    timeout: int,
) -> list[Candidate]:
    if extension_from(source) in extensions:
        return [Candidate(source)]
    response = session.get(source, timeout=timeout)
    response.raise_for_status()
    content_type = response.headers.get("Content-Type", "").lower()
    if "html" not in content_type:
        logging.warning("Skipping non-HTML source without a supported extension: %s", source)
        return []
    soup = BeautifulSoup(response.text, "html.parser")
    found: dict[str, Candidate] = {}
    for anchor in soup.select("a[href]"):
        url = urljoin(response.url, anchor.get("href", ""))
        label = anchor.get("download") or anchor.get_text(" ", strip=True)
        suffix = extension_from(url) or Path(label).suffix.lower()
        if suffix not in extensions:
            continue
        if not host_allowed(url, response.url, allowed_hosts):
            logging.warning("Blocked off-site discovered link: %s", url)
            continue
        found.setdefault(url, Candidate(url=url, label=label))
    return list(found.values())


def response_filename(response: requests.Response, candidate: Candidate) -> str:
    disposition = response.headers.get("Content-Disposition", "")
    match = re.search(r"filename\\*?=(?:UTF-8''|[\"']?)([^\"';]+)", disposition, re.I)
    if match:
        return safe_name(match.group(1))
    if candidate.label and Path(candidate.label).suffix:
        return safe_name(candidate.label)
    return safe_name(Path(unquote(urlparse(response.url).path)).name)


def download(
    session: requests.Session,
    candidate: Candidate,
    destination_dir: Path,
    extensions: set[str],
    timeout: int,
    max_bytes: int,
) -> tuple[Path, str, int]:
    with session.get(candidate.url, stream=True, timeout=timeout) as response:
        response.raise_for_status()
        filename = response_filename(response, candidate)
        if Path(filename).suffix.lower() not in extensions:
            raise ValueError(f"Server returned unsupported filename: {filename}")
        announced = int(response.headers.get("Content-Length", "0") or 0)
        if announced > max_bytes:
            raise ValueError(f"File exceeds configured maximum of {max_bytes} bytes")
        destination_dir.mkdir(parents=True, exist_ok=True)
        temporary = destination_dir / f".{filename}.part"
        digest = hashlib.sha256()
        total = 0
        try:
            with temporary.open("wb") as handle:
                for chunk in response.iter_content(CHUNK_SIZE):
                    if not chunk:
                        continue
                    total += len(chunk)
                    if total > max_bytes:
                        raise ValueError(
                            f"File exceeds configured maximum of {max_bytes} bytes"
                        )
                    digest.update(chunk)
                    handle.write(chunk)
            return temporary, digest.hexdigest(), total
        except Exception:
            temporary.unlink(missing_ok=True)
            raise


def final_path(directory: Path, filename: str) -> Path:
    target = directory / filename
    if not target.exists():
        return target
    counter = 2
    while True:
        candidate = directory / f"{target.stem} ({counter}){target.suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def process_course(
    course: dict[str, Any],
    defaults: dict[str, Any],
    state_dir: Path,
    root_dir: Path,
    baseline: bool,
    dry_run: bool,
    browser_context: BrowserContext | None = None,
    diagnose: bool = False,
) -> tuple[int, int, int]:
    name = safe_name(str(course.get("name", "")), "")
    sources = course.get("sources", [])
    if not name or not isinstance(sources, list) or not sources:
        raise ValueError("Each course needs a name and a non-empty sources list")
    extensions = {
        ext.lower() if ext.startswith(".") else f".{ext.lower()}"
        for ext in course.get("extensions", defaults["extensions"])
    }
    allowed_hosts = {
        str(host).lower() for host in course.get("allowed_hosts", [])
    }
    timeout = int(defaults["timeout_seconds"])
    max_bytes = int(defaults["max_file_size_mb"]) * 1024 * 1024
    session = make_session(course)
    state_path = state_dir / f"{safe_name(name).lower().replace(' ', '-')}.json"
    state = load_state(state_path)
    destination = root_dir / safe_name(course.get("folder", name))
    candidates: dict[str, Candidate] = {}
    for source in sources:
        source = str(source)
        if is_campuswire_url(source):
            if browser_context is None:
                raise ValueError("Campuswire requires browser-assisted mode")
            discovered = discover_browser(
                browser_context,
                source,
                extensions,
                allowed_hosts,
                timeout,
                [str(tab) for tab in course.get("tab_names", [])],
                state_dir / "debug" if diagnose else None,
                name,
            )
            sync_browser_cookies(browser_context, session)
        else:
            discovered = discover(
                session, source, extensions, allowed_hosts, timeout
            )
        for candidate in discovered:
            candidates.setdefault(candidate.url, candidate)

    new_items = [item for url, item in candidates.items() if url not in state["urls"]]
    if baseline:
        for item in new_items:
            state["urls"][item.url] = {"status": "baseline"}
        save_state(state_path, state)
        logging.info("%s: recorded %d existing file(s)", name, len(new_items))
        return 0, len(candidates) - len(new_items), 0
    if dry_run:
        for item in new_items:
            logging.info("%s: would download %s", name, item.url)
        return len(new_items), len(candidates) - len(new_items), 0

    downloaded = skipped = failed = 0
    for item in new_items:
        try:
            temporary, digest, size = download(
                session, item, destination, extensions, timeout, max_bytes
            )
            duplicate = state["hashes"].get(digest)
            if duplicate:
                temporary.unlink(missing_ok=True)
                state["urls"][item.url] = {
                    "status": "duplicate",
                    "same_as": duplicate,
                    "sha256": digest,
                }
                skipped += 1
                logging.info("%s: duplicate content skipped: %s", name, item.url)
            else:
                target = final_path(destination, temporary.name[1:-5])
                temporary.replace(target)
                state["urls"][item.url] = {
                    "status": "downloaded",
                    "path": str(target),
                    "sha256": digest,
                    "bytes": size,
                }
                state["hashes"][digest] = str(target)
                downloaded += 1
                logging.info("%s: downloaded %s", name, target)
            save_state(state_path, state)
        except Exception as exc:
            failed += 1
            logging.error("%s: failed %s: %s", name, item.url, exc)
    return downloaded, skipped + len(candidates) - len(new_items), failed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--course", help="Only process the named course")
    parser.add_argument("--baseline", action="store_true", help="Record current files only")
    parser.add_argument("--dry-run", action="store_true", help="Show new links only")
    parser.add_argument(
        "--login",
        action="store_true",
        help="Open Campuswire and save a private signed-in browser session",
    )
    parser.add_argument(
        "--visible",
        action="store_true",
        help="Show the browser while scanning Campuswire",
    )
    parser.add_argument(
        "--diagnose",
        action="store_true",
        help="Save a private Campuswire page snapshot for troubleshooting",
    )
    parser.add_argument("--verbose", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        config = load_json(args.config)
        state_dir = Path(config.get("state_dir", DEFAULT_STATE_DIR)).expanduser()
        root_dir = Path(config.get("download_dir", DEFAULT_DOWNLOAD_DIR)).expanduser()
        configure_logging(state_dir, args.verbose)
        defaults = {
            "extensions": config.get("extensions", DEFAULT_EXTENSIONS),
            "timeout_seconds": config.get("timeout_seconds", 30),
            "max_file_size_mb": config.get("max_file_size_mb", 100),
        }
        courses = config.get("courses", [])
        if not isinstance(courses, list) or not courses:
            raise ValueError("Configuration needs a non-empty 'courses' list")
        if args.course:
            courses = [
                course for course in courses if course.get("name") == args.course
            ]
            if not courses:
                raise ValueError(f"Course not found: {args.course}")
        if args.login:
            return campuswire_login(courses, state_dir)
        totals = [0, 0, 0]
        uses_browser = any(
            is_campuswire_url(str(source))
            for course in courses
            for source in course.get("sources", [])
        )
        if uses_browser:
            require_playwright()
            with sync_playwright() as playwright:
                context = make_browser_context(
                    playwright, state_dir, headless=not args.visible
                )
                try:
                    for course in courses:
                        result = process_course(
                            course,
                            defaults,
                            state_dir,
                            root_dir,
                            args.baseline,
                            args.dry_run,
                            context,
                            args.diagnose,
                        )
                        totals = [
                            left + right for left, right in zip(totals, result)
                        ]
                finally:
                    context.close()
        else:
            for course in courses:
                result = process_course(
                    course, defaults, state_dir, root_dir, args.baseline, args.dry_run
                )
                totals = [left + right for left, right in zip(totals, result)]
        logging.info(
            "Complete: %d downloaded/new, %d already seen/duplicates, %d failed",
            *totals,
        )
        return 1 if totals[2] else 0
    except (OSError, ValueError, requests.RequestException) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
