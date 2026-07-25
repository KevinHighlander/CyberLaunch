#!/usr/bin/env python3
"""Watch an export folder and organize supported iPad note files as PDFs."""

from __future__ import annotations

import argparse
import json
import logging
import re
import shutil
import sys
import textwrap
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SUPPORTED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".txt", ".md"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff"}
TEXT_EXTENSIONS = {".txt", ".md"}
TEMP_SUFFIXES = {".download", ".icloud", ".part", ".tmp", ".crdownload"}


@dataclass(frozen=True)
class Settings:
    inbox: Path
    destination: Path
    default_subject: str
    poll_interval_seconds: float
    settle_seconds: float
    keep_originals: bool
    log_file: Path
    subjects: dict[str, dict[str, Any]]


def expand_path(value: str, base_dir: Path) -> Path:
    path = Path(value).expanduser()
    return path if path.is_absolute() else (base_dir / path).resolve()


def load_settings(config_path: Path) -> Settings:
    """Load and validate settings from a JSON configuration file."""
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Configuration file not found: {config_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {config_path}: {exc}") from exc

    required = {"inbox", "destination", "subjects"}
    missing = sorted(required - data.keys())
    if missing:
        raise ValueError(f"Missing configuration field(s): {', '.join(missing)}")
    if not isinstance(data["subjects"], dict):
        raise ValueError("'subjects' must be a JSON object")

    base = config_path.parent.resolve()
    inbox = expand_path(str(data["inbox"]), base)
    destination = expand_path(str(data["destination"]), base)
    if inbox == destination:
        raise ValueError("'inbox' and 'destination' must be different folders")
    if inbox in destination.parents or destination in inbox.parents:
        raise ValueError("'inbox' and 'destination' must not contain one another")

    poll = float(data.get("poll_interval_seconds", 10))
    settle = float(data.get("settle_seconds", 2))
    if poll <= 0 or settle < 0:
        raise ValueError("Polling must be positive and settle time cannot be negative")

    return Settings(
        inbox=inbox,
        destination=destination,
        default_subject=str(data.get("default_subject", "_Unsorted")).strip() or "_Unsorted",
        poll_interval_seconds=poll,
        settle_seconds=settle,
        keep_originals=bool(data.get("keep_originals", False)),
        log_file=expand_path(str(data.get("log_file", "./logs/ipad-notes-converter.log")), base),
        subjects=data["subjects"],
    )


def setup_logging(log_file: Path, dry_run: bool) -> logging.Logger:
    logger = logging.getLogger("ipad_notes_converter")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    stream = logging.StreamHandler()
    stream.setFormatter(formatter)
    logger.addHandler(stream)
    if not dry_run:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    return logger


def safe_component(value: str) -> str:
    """Return a filesystem-safe name without path traversal."""
    cleaned = re.sub(r"[\x00-\x1f/:\\]", "-", value).strip(" .")
    return cleaned or "Untitled"


def subject_for(filename: str, settings: Settings) -> tuple[str, str]:
    """Return the destination folder and cleaned output stem."""
    stem = Path(filename).stem
    prefix, separator, remainder = stem.partition(" - ")
    if separator:
        for label, rule in settings.subjects.items():
            if prefix.casefold() == label.casefold():
                folder = safe_component(str(rule.get("folder", label)))
                return folder, safe_component(remainder)

    lowered = stem.casefold()
    for label, rule in settings.subjects.items():
        keywords = rule.get("keywords", [])
        if any(str(keyword).casefold() in lowered for keyword in keywords):
            folder = safe_component(str(rule.get("folder", label)))
            return folder, safe_component(stem)
    return safe_component(settings.default_subject), safe_component(stem)


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    counter = 2
    while True:
        candidate = path.with_name(f"{path.stem} ({counter}){path.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def image_to_pdf(source: Path, target: Path) -> None:
    try:
        from PIL import Image, ImageOps, ImageSequence
    except ImportError as exc:
        raise RuntimeError("Image conversion requires Pillow; install requirements.txt") from exc

    pages = []
    with Image.open(source) as image:
        for frame in ImageSequence.Iterator(image):
            page = ImageOps.exif_transpose(frame).convert("RGB")
            pages.append(page.copy())
    if not pages:
        raise RuntimeError(f"No image frames found in {source.name}")
    pages[0].save(target, "PDF", resolution=150, save_all=True, append_images=pages[1:])


def text_to_pdf(source: Path, target: Path) -> None:
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except ImportError as exc:
        raise RuntimeError("Text conversion requires ReportLab; install requirements.txt") from exc

    page_width, page_height = letter
    margin = 54
    font_size = 10
    line_height = 14
    usable_chars = 95
    pdf = canvas.Canvas(str(target), pagesize=letter)
    pdf.setTitle(source.stem)
    y = page_height - margin
    for raw_line in source.read_text(encoding="utf-8", errors="replace").splitlines() or [""]:
        wrapped = textwrap.wrap(
            raw_line.expandtabs(4),
            width=usable_chars,
            replace_whitespace=False,
            drop_whitespace=False,
        ) or [""]
        for line in wrapped:
            if y < margin:
                pdf.showPage()
                y = page_height - margin
            pdf.setFont("Courier", font_size)
            pdf.drawString(margin, y, line)
            y -= line_height
    pdf.save()


def wait_until_stable(path: Path, settle_seconds: float) -> bool:
    """Return once a file's size and modification time stop changing."""
    if settle_seconds == 0:
        return path.is_file()
    try:
        first = (path.stat().st_size, path.stat().st_mtime_ns)
        time.sleep(settle_seconds)
        second = (path.stat().st_size, path.stat().st_mtime_ns)
        return first == second and path.is_file()
    except FileNotFoundError:
        return False


def process_file(source: Path, settings: Settings, logger: logging.Logger, dry_run: bool = False) -> Path | None:
    """Convert and route one source file. Return the intended/final destination."""
    source = source.resolve()
    if not source.is_file() or source.name.startswith(".") or source.suffix.lower() in TEMP_SUFFIXES:
        return None
    try:
        source.relative_to(settings.inbox.resolve())
    except ValueError:
        logger.error("Refusing file outside configured inbox: %s", source)
        return None

    extension = source.suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        unsupported = unique_path(settings.destination / "_Unsorted" / "Unsupported" / source.name)
        logger.warning("Unsupported file %s -> %s", source.name, unsupported)
        if not dry_run:
            unsupported.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(unsupported))
        return unsupported

    folder, stem = subject_for(source.name, settings)
    target = unique_path(settings.destination / folder / f"{stem}.pdf")
    logger.info("%s -> %s%s", source.name, target, " (dry run)" if dry_run else "")
    if dry_run:
        return target

    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(".pdf.tmp")
    try:
        if extension == ".pdf":
            shutil.copy2(source, temporary)
        elif extension in IMAGE_EXTENSIONS:
            image_to_pdf(source, temporary)
        else:
            text_to_pdf(source, temporary)
        temporary.replace(target)
        if not settings.keep_originals:
            source.unlink()
        logger.info("Completed %s", target)
        return target
    except Exception:
        temporary.unlink(missing_ok=True)
        logger.exception("Failed to process %s", source)
        return None


def scan_inbox(settings: Settings, logger: logging.Logger, dry_run: bool = False) -> int:
    processed = 0
    for path in sorted(settings.inbox.iterdir(), key=lambda item: item.name.casefold()):
        if path.is_file() and wait_until_stable(path, settings.settle_seconds):
            if process_file(path, settings, logger, dry_run) is not None:
                processed += 1
    return processed


def watch(settings: Settings, logger: logging.Logger, dry_run: bool = False) -> None:
    try:
        from watchdog.events import FileSystemEventHandler
        from watchdog.observers import Observer
    except ImportError as exc:
        raise RuntimeError("Watch mode requires watchdog; install requirements.txt") from exc

    class Handler(FileSystemEventHandler):
        def on_created(self, event: Any) -> None:
            if not event.is_directory:
                path = Path(event.src_path)
                if wait_until_stable(path, settings.settle_seconds):
                    process_file(path, settings, logger, dry_run)

        def on_moved(self, event: Any) -> None:
            if not event.is_directory:
                path = Path(event.dest_path)
                if wait_until_stable(path, settings.settle_seconds):
                    process_file(path, settings, logger, dry_run)

    scan_inbox(settings, logger, dry_run)
    observer = Observer()
    observer.schedule(Handler(), str(settings.inbox), recursive=False)
    observer.start()
    logger.info("Watching %s (press Control+C to stop)", settings.inbox)
    try:
        while True:
            time.sleep(settings.poll_interval_seconds)
            scan_inbox(settings, logger, dry_run)
    except KeyboardInterrupt:
        logger.info("Stopping watcher")
    finally:
        observer.stop()
        observer.join()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("config.json"))
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--once", action="store_true", help="scan the inbox once and exit")
    mode.add_argument("--file", type=Path, help="process one file from the configured inbox")
    mode.add_argument("--check", action="store_true", help="validate configuration and exit")
    parser.add_argument("--dry-run", action="store_true", help="preview actions without writing files")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        settings = load_settings(args.config.resolve())
        logger = setup_logging(settings.log_file, args.dry_run or args.check)
        if args.check:
            print(f"Configuration is valid.\nInbox: {settings.inbox}\nDestination: {settings.destination}")
            return 0
        if not args.dry_run:
            settings.inbox.mkdir(parents=True, exist_ok=True)
            settings.destination.mkdir(parents=True, exist_ok=True)
        elif not settings.inbox.is_dir():
            raise ValueError(f"Dry-run inbox does not exist: {settings.inbox}")
        if args.file:
            return 0 if process_file(args.file, settings, logger, args.dry_run) else 1
        if args.once:
            count = scan_inbox(settings, logger, args.dry_run)
            logger.info("Processed %d file(s)", count)
            return 0
        watch(settings, logger, args.dry_run)
        return 0
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
