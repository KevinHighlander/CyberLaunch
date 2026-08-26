"""Persistent real-world intelligence incident model for CLIM."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4


def _utc_now() -> datetime:
    """Return the current UTC time."""
    return datetime.now(
        timezone.utc
    )


def _validate_event_uid(
    event_uid: str,
) -> str:
    """Return a valid normalized event UID."""
    normalized = event_uid.strip()

    if not normalized:
        raise ValueError(
            "Event UID cannot be empty."
        )

    return normalized


def _validate_timestamp(
    timestamp: datetime,
) -> datetime:
    """Require a timezone-aware timestamp."""
    if timestamp.tzinfo is None:
        raise ValueError(
            "Incident timestamps must be timezone-aware."
        )

    return timestamp


@dataclass(frozen=True, slots=True)
class IntelligenceIncident:
    """Persistent identity for one real-world intelligence incident."""

    incident_uid: str
    created_at: datetime
    updated_at: datetime
    event_uids: tuple[str, ...]

    @classmethod
    def create(
        cls,
        event_uid: str,
        *,
        incident_uid: str | None = None,
        observed_at: datetime | None = None,
    ) -> IntelligenceIncident:
        """Create an incident from its first evidence report."""
        normalized_event_uid = _validate_event_uid(
            event_uid
        )

        timestamp = _validate_timestamp(
            observed_at
            if observed_at is not None
            else _utc_now()
        )

        resolved_incident_uid = (
            incident_uid.strip()
            if incident_uid is not None
            else f"incident-{uuid4().hex}"
        )

        if not resolved_incident_uid:
            raise ValueError(
                "Incident UID cannot be empty."
            )

        return cls(
            incident_uid=resolved_incident_uid,
            created_at=timestamp,
            updated_at=timestamp,
            event_uids=(
                normalized_event_uid,
            ),
        )

    @property
    def event_count(self) -> int:
        """Return the number of evidence reports attached to the incident."""
        return len(
            self.event_uids
        )

    def contains_event(
        self,
        event_uid: str,
    ) -> bool:
        """Return whether an evidence report belongs to this incident."""
        return event_uid in self.event_uids

    def attach_event(
        self,
        event_uid: str,
        *,
        observed_at: datetime | None = None,
    ) -> IntelligenceIncident:
        """Return the incident with an additional evidence report."""
        normalized_event_uid = _validate_event_uid(
            event_uid
        )

        if normalized_event_uid in self.event_uids:
            return self

        timestamp = _validate_timestamp(
            observed_at
            if observed_at is not None
            else _utc_now()
        )

        if timestamp < self.updated_at:
            raise ValueError(
                "Incident update time cannot move backward."
            )

        return IntelligenceIncident(
            incident_uid=self.incident_uid,
            created_at=self.created_at,
            updated_at=timestamp,
            event_uids=(
                *self.event_uids,
                normalized_event_uid,
            ),
        )