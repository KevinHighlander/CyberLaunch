"""SQLite persistence for CLIM intelligence events."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from app.models.event import IntelligenceEvent


DEFAULT_DATABASE_PATH = Path(__file__).resolve().parents[2] / "data" / "clim.db"


class EventRepository:
    """SQLite repository for normalized intelligence events."""

    def __init__(self, database_path: Path = DEFAULT_DATABASE_PATH) -> None:
        self.database_path = database_path

    def _connect(self) -> sqlite3.Connection:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_uid TEXT NOT NULL UNIQUE,
                    title TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    source_name TEXT NOT NULL,
                    source_url TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    source_country TEXT,
                    source_authority TEXT NOT NULL,
                    source_reliability TEXT NOT NULL,
                    published_at TEXT,
                    collected_at TEXT NOT NULL,
                    region TEXT NOT NULL,
                    category TEXT NOT NULL,
                    significance INTEGER NOT NULL,
                    confidence TEXT NOT NULL
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_events_significance ON events(significance)"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_events_region ON events(region)"
            )

    def insert(self, event: IntelligenceEvent) -> bool:
        try:
            with self._connect() as connection:
                connection.execute(
                    """
                    INSERT INTO events (
                        event_uid, title, summary, source_name, source_url,
                        source_type, source_country, source_authority,
                        source_reliability, published_at, collected_at,
                        region, category, significance, confidence
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        event.event_uid,
                        event.title,
                        event.summary,
                        event.source_name,
                        event.source_url,
                        event.source_type,
                        event.source_country,
                        event.source_authority,
                        event.source_reliability,
                        event.published_at,
                        event.collected_at.isoformat() if event.collected_at else "",
                        event.region,
                        event.category,
                        event.significance,
                        event.confidence,
                    ),
                )
            return True
        except sqlite3.IntegrityError:
            return False

    def count(self) -> int:
        with self._connect() as connection:
            row = connection.execute("SELECT COUNT(*) AS count FROM events").fetchone()
        return int(row["count"])

    def significant(self, minimum_score: int, limit: int) -> list[sqlite3.Row]:
        with self._connect() as connection:
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
