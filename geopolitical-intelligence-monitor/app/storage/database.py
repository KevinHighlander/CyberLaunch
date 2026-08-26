"""SQLite persistence for analyzed CLIM intelligence events."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from app.enums.source import (
    SourceAuthority,
    SourceReliability,
)
from app.models.analyzed_event import AnalyzedEvent
from app.models.normalized_event import NormalizedEvent


DEFAULT_DATABASE_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "clim.db"
)


def _row_to_normalized_event(
    row: sqlite3.Row,
) -> NormalizedEvent:
    """Reconstruct normalized evidence from a stored event row."""
    return NormalizedEvent(
        event_uid=row["event_uid"],
        title=row["title"],
        summary=row["summary"],
        source_name=row["source_name"],
        source_url=row["source_url"],
        source_type=row["source_type"],
        source_country=row["source_country"],
        source_authority=SourceAuthority(
            row["source_authority"]
        ),
        source_reliability=SourceReliability(
            row["source_reliability"]
        ),
        published_at=row["published_at"],
        region_hint=None,
    )


class EventRepository:
    """SQLite repository for analyzed intelligence events."""

    def __init__(
        self,
        database_path: Path = DEFAULT_DATABASE_PATH,
    ) -> None:
        self.database_path = database_path

    def _connect(self) -> sqlite3.Connection:
        """Return a configured SQLite connection."""
        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        connection = sqlite3.connect(
            self.database_path
        )

        connection.row_factory = sqlite3.Row

        return connection

    def initialize(self) -> None:
        """Create the event table and indexes."""
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
                """
                CREATE INDEX IF NOT EXISTS
                idx_events_significance
                ON events(significance)
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_events_region
                ON events(region)
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_events_published_at
                ON events(published_at)
                """
            )

    def insert(
        self,
        event: AnalyzedEvent,
    ) -> bool:
        """
        Persist an analyzed intelligence event.

        Returns True when the event is newly inserted.
        Returns False when its event UID already exists.
        """
        try:
            with self._connect() as connection:
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
                        collected_at,

                        region,
                        category,

                        significance,
                        confidence
                    )
                    VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?
                    )
                    """,
                    (
                        event.event_uid,
                        event.title,
                        event.summary,

                        event.source_name,
                        event.source_url,
                        event.source_type,
                        event.source_country,

                        event.source_authority.value,
                        event.source_reliability.value,

                        event.published_at,
                        event.collected_at.isoformat(),

                        event.region,
                        event.category,

                        event.significance,
                        event.confidence.value,
                    ),
                )

            return True

        except sqlite3.IntegrityError:
            return False

    def get_normalized(
        self,
        event_uid: str,
    ) -> NormalizedEvent | None:
        """Return stored evidence reconstructed as a normalized event."""
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM events
                WHERE event_uid = ?
                """,
                (
                    event_uid,
                ),
            ).fetchone()

        if row is None:
            return None

        return _row_to_normalized_event(
            row
        )

    def get_normalized_many(
        self,
        event_uids: tuple[str, ...],
    ) -> dict[str, NormalizedEvent]:
        """Return available normalized evidence indexed by event UID."""
        evidence: dict[
            str,
            NormalizedEvent,
        ] = {}

        if not event_uids:
            return evidence

        with self._connect() as connection:
            for event_uid in event_uids:
                row = connection.execute(
                    """
                    SELECT *
                    FROM events
                    WHERE event_uid = ?
                    """,
                    (
                        event_uid,
                    ),
                ).fetchone()

                if row is None:
                    continue

                normalized = _row_to_normalized_event(
                    row
                )

                evidence[
                    normalized.event_uid
                ] = normalized

        return evidence

    def count(self) -> int:
        """Return the total number of stored events."""
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT COUNT(*) AS count
                FROM events
                """
            ).fetchone()

        return int(
            row["count"]
        )

    def significant(
        self,
        minimum_score: int,
        limit: int,
    ) -> list[sqlite3.Row]:
        """Return highest-priority stored events."""
        with self._connect() as connection:
            return connection.execute(
                """
                SELECT *
                FROM events
                WHERE significance >= ?
                ORDER BY
                    significance DESC,
                    id DESC
                LIMIT ?
                """,
                (
                    minimum_score,
                    limit,
                ),
            ).fetchall()