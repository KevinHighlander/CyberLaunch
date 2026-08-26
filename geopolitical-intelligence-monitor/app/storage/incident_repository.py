"""SQLite persistence for durable CLIM intelligence incidents."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

from app.models.intelligence_incident import IntelligenceIncident
from app.storage.database import DEFAULT_DATABASE_PATH


class IncidentRepository:
    """SQLite repository for persistent intelligence incidents."""

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

        connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        return connection

    def initialize(self) -> None:
        """Create incident persistence tables and indexes."""
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS incidents (
                    incident_uid TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS incident_members (
                    incident_uid TEXT NOT NULL,
                    event_uid TEXT NOT NULL UNIQUE,
                    position INTEGER NOT NULL,

                    PRIMARY KEY (
                        incident_uid,
                        event_uid
                    ),

                    FOREIGN KEY (
                        incident_uid
                    )
                    REFERENCES incidents (
                        incident_uid
                    )
                    ON DELETE CASCADE
                )
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_incident_members_incident
                ON incident_members(
                    incident_uid,
                    position
                )
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_incident_members_event
                ON incident_members(
                    event_uid
                )
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_incidents_updated_at
                ON incidents(
                    updated_at
                )
                """
            )

    def _validate_membership(
        self,
        connection: sqlite3.Connection,
        incident: IntelligenceIncident,
    ) -> None:
        """Reject evidence already assigned to another incident."""
        for event_uid in incident.event_uids:
            row = connection.execute(
                """
                SELECT incident_uid
                FROM incident_members
                WHERE event_uid = ?
                """,
                (
                    event_uid,
                ),
            ).fetchone()

            if row is None:
                continue

            existing_incident_uid = row[
                "incident_uid"
            ]

            if (
                existing_incident_uid
                != incident.incident_uid
            ):
                raise ValueError(
                    f"Event {event_uid} already belongs "
                    f"to incident "
                    f"{existing_incident_uid}."
                )

    def save(
        self,
        incident: IntelligenceIncident,
    ) -> None:
        """Persist a new or updated intelligence incident."""
        with self._connect() as connection:
            self._validate_membership(
                connection,
                incident,
            )

            connection.execute(
                """
                INSERT INTO incidents (
                    incident_uid,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?)

                ON CONFLICT(incident_uid)
                DO UPDATE SET
                    updated_at = excluded.updated_at
                """,
                (
                    incident.incident_uid,
                    incident.created_at.isoformat(),
                    incident.updated_at.isoformat(),
                ),
            )

            for position, event_uid in enumerate(
                incident.event_uids
            ):
                connection.execute(
                    """
                    INSERT OR IGNORE INTO incident_members (
                        incident_uid,
                        event_uid,
                        position
                    )
                    VALUES (?, ?, ?)
                    """,
                    (
                        incident.incident_uid,
                        event_uid,
                        position,
                    ),
                )

    def get(
        self,
        incident_uid: str,
    ) -> IntelligenceIncident | None:
        """Return an incident by UID when it exists."""
        with self._connect() as connection:
            incident_row = connection.execute(
                """
                SELECT
                    incident_uid,
                    created_at,
                    updated_at
                FROM incidents
                WHERE incident_uid = ?
                """,
                (
                    incident_uid,
                ),
            ).fetchone()

            if incident_row is None:
                return None

            member_rows = connection.execute(
                """
                SELECT event_uid
                FROM incident_members
                WHERE incident_uid = ?
                ORDER BY position ASC
                """,
                (
                    incident_uid,
                ),
            ).fetchall()

        return IntelligenceIncident(
            incident_uid=incident_row[
                "incident_uid"
            ],
            created_at=datetime.fromisoformat(
                incident_row[
                    "created_at"
                ]
            ),
            updated_at=datetime.fromisoformat(
                incident_row[
                    "updated_at"
                ]
            ),
            event_uids=tuple(
                row["event_uid"]
                for row in member_rows
            ),
        )

    def list_incidents(
        self,
    ) -> tuple[IntelligenceIncident, ...]:
        """Return all persisted incidents in deterministic order."""
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT incident_uid
                FROM incidents
                ORDER BY
                    updated_at DESC,
                    incident_uid ASC
                """
            ).fetchall()

        incidents: list[
            IntelligenceIncident
        ] = []

        for row in rows:
            incident = self.get(
                row["incident_uid"]
            )

            if incident is not None:
                incidents.append(
                    incident
                )

        return tuple(
            incidents
        )

    def find_by_event(
        self,
        event_uid: str,
    ) -> IntelligenceIncident | None:
        """Return the incident containing an evidence report."""
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT incident_uid
                FROM incident_members
                WHERE event_uid = ?
                """,
                (
                    event_uid,
                ),
            ).fetchone()

        if row is None:
            return None

        return self.get(
            row["incident_uid"]
        )

    def count(self) -> int:
        """Return the number of persisted incidents."""
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT COUNT(*) AS count
                FROM incidents
                """
            ).fetchone()

        return int(
            row["count"]
        )