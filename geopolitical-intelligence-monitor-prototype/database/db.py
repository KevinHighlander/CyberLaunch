"""SQLite storage layer for CyberLaunch Intelligence Monitor."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


DATABASE_PATH = Path(__file__).resolve().parent / "clim.db"


def get_connection() -> sqlite3.Connection:
    """Return a configured SQLite connection."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    """Create CLIM database tables if they do not already exist."""
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                event_uid TEXT NOT NULL UNIQUE,

                title TEXT NOT NULL,
                summary TEXT,

                source_name TEXT NOT NULL,
                source_url TEXT NOT NULL,

                source_type TEXT NOT NULL DEFAULT 'unknown',
                source_country TEXT,
                source_authority TEXT NOT NULL DEFAULT 'unknown',
                source_reliability TEXT NOT NULL DEFAULT 'unknown',

                published_at TEXT,
                collected_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                region TEXT NOT NULL DEFAULT 'unclassified',
                category TEXT NOT NULL DEFAULT 'unclassified',

                significance INTEGER NOT NULL DEFAULT 0,
                confidence TEXT NOT NULL DEFAULT 'unrated'
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_events_region
            ON events(region)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_events_published_at
            ON events(published_at)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_events_significance
            ON events(significance)
            """
        )


def insert_event(event: dict[str, Any]) -> bool:
    """
    Insert an intelligence event.

    Returns True if a new event was stored.
    Returns False if the event already exists.
    """
    try:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO events (
                    event_uid,
                    title,
                    summary,

                    source_name,
                    source_url,
                    source_type,
                    source_country,
                    source_authority,
                    source_reliability,

                    published_at,

                    region,
                    category,
                    significance,
                    confidence
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event["event_uid"],
                    event["title"],
                    event.get("summary", ""),

                    event["source_name"],
                    event["source_url"],
                    event.get("source_type", "unknown"),
                    event.get("source_country"),
                    event.get("source_authority", "unknown"),
                    event.get("source_reliability", "unknown"),

                    event.get("published_at"),

                    event.get("region", "unclassified"),
                    event.get("category", "unclassified"),
                    event.get("significance", 0),
                    event.get("confidence", "unrated"),
                ),
            )

        return True

    except sqlite3.IntegrityError:
        return False


def get_recent_events(limit: int = 10) -> list[sqlite3.Row]:
    """Return the most recently stored events."""
    with get_connection() as connection:
        return connection.execute(
            """
            SELECT *
            FROM events
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()


def get_significant_events(
    limit: int = 10,
    minimum_score: int = 3,
) -> list[sqlite3.Row]:
    """Return recent events meeting the significance threshold."""
    with get_connection() as connection:
        return connection.execute(
            """
            SELECT *
            FROM events
            WHERE significance >= ?
            ORDER BY significance DESC, id DESC
            LIMIT ?
            """,
            (minimum_score, limit),
        ).fetchall()


def get_event_count() -> int:
    """Return the total number of stored intelligence events."""
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM events
            """
        ).fetchone()

    return int(row["count"])
