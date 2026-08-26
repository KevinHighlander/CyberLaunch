"""Persistent incident orchestration for CLIM."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.intelligence.incident_resolver import (
    IncidentResolution,
    resolve_incident,
)
from app.models.intelligence_incident import IntelligenceIncident
from app.models.normalized_event import NormalizedEvent
from app.storage.database import EventRepository
from app.storage.incident_repository import IncidentRepository


@dataclass(frozen=True, slots=True)
class IncidentUpdate:
    """Result of persistently resolving one intelligence report."""

    resolution: IncidentResolution

    @property
    def incident(
        self,
    ) -> IntelligenceIncident:
        """Return the resolved persistent incident."""
        return self.resolution.incident

    @property
    def matched_existing(
        self,
    ) -> bool:
        """Return whether the report joined an existing incident."""
        return self.resolution.matched_existing

    @property
    def correlation_score(
        self,
    ) -> float:
        """Return the strongest matching correlation score."""
        return self.resolution.correlation_score


def _collect_event_uids(
    incidents: tuple[IntelligenceIncident, ...],
) -> tuple[str, ...]:
    """Return unique evidence UIDs from known incidents."""
    event_uids: list[str] = []
    seen: set[str] = set()

    for incident in incidents:
        for event_uid in incident.event_uids:
            if event_uid in seen:
                continue

            seen.add(
                event_uid
            )

            event_uids.append(
                event_uid
            )

    return tuple(
        event_uids
    )


def resolve_and_persist_incident(
    event: NormalizedEvent,
    *,
    event_repository: EventRepository,
    incident_repository: IncidentRepository,
    observed_at: datetime | None = None,
    threshold: float = 0.40,
) -> IncidentUpdate:
    """
    Resolve one report against persisted incidents and save the result.

    Historical evidence is reconstructed from the event repository.
    Incident identity and membership are persisted separately.
    """
    incidents = (
        incident_repository.list_incidents()
    )

    event_uids = _collect_event_uids(
        incidents
    )

    evidence_by_uid = (
        event_repository.get_normalized_many(
            event_uids
        )
    )

    resolution = resolve_incident(
        event,
        incidents=incidents,
        evidence_by_uid=evidence_by_uid,
        observed_at=observed_at,
        threshold=threshold,
    )

    incident_repository.save(
        resolution.incident
    )

    return IncidentUpdate(
        resolution=resolution
    )