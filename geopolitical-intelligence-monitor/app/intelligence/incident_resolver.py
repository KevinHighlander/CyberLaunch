"""Cross-run incident resolution for CLIM."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone

from app.intelligence.correlation import correlate
from app.models.intelligence_incident import IntelligenceIncident
from app.models.normalized_event import NormalizedEvent


@dataclass(frozen=True, slots=True)
class IncidentResolution:
    """Result of resolving one report against known incidents."""

    incident: IntelligenceIncident
    matched_existing: bool
    correlation_score: float
    matched_event_uid: str | None


def _utc_now() -> datetime:
    """Return the current UTC time."""
    return datetime.now(
        timezone.utc
    )


def _best_incident_match(
    event: NormalizedEvent,
    incidents: tuple[IntelligenceIncident, ...],
    evidence_by_uid: Mapping[str, NormalizedEvent],
    *,
    threshold: float,
) -> tuple[
    IntelligenceIncident,
    float,
    str,
] | None:
    """Return the strongest deterministic incident match."""
    candidates: list[
        tuple[
            float,
            str,
            str,
            IntelligenceIncident,
        ]
    ] = []

    for incident in incidents:
        best_score = 0.0
        best_event_uid: str | None = None

        for event_uid in incident.event_uids:
            existing_event = evidence_by_uid.get(
                event_uid
            )

            if existing_event is None:
                continue

            result = correlate(
                event,
                existing_event,
            )

            if result.score > best_score:
                best_score = result.score
                best_event_uid = event_uid

        if (
            best_event_uid is not None
            and best_score >= threshold
        ):
            candidates.append(
                (
                    best_score,
                    incident.incident_uid,
                    best_event_uid,
                    incident,
                )
            )

    if not candidates:
        return None

    candidates.sort(
        key=lambda candidate: (
            -candidate[0],
            candidate[1],
            candidate[2],
        )
    )

    (
        score,
        _,
        matched_event_uid,
        incident,
    ) = candidates[0]

    return (
        incident,
        score,
        matched_event_uid,
    )


def resolve_incident(
    event: NormalizedEvent,
    *,
    incidents: tuple[IntelligenceIncident, ...],
    evidence_by_uid: Mapping[str, NormalizedEvent],
    observed_at: datetime | None = None,
    threshold: float = 0.40,
) -> IncidentResolution:
    """
    Resolve a new report into an existing or new incident.

    Existing incidents are matched against their known evidence reports.
    The strongest qualifying correlation wins deterministically.
    """
    timestamp = (
        observed_at
        if observed_at is not None
        else _utc_now()
    )

    for incident in incidents:
        if incident.contains_event(
            event.event_uid
        ):
            return IncidentResolution(
                incident=incident,
                matched_existing=True,
                correlation_score=1.0,
                matched_event_uid=event.event_uid,
            )

    match = _best_incident_match(
        event,
        incidents,
        evidence_by_uid,
        threshold=threshold,
    )

    if match is None:
        incident = IntelligenceIncident.create(
            event.event_uid,
            observed_at=timestamp,
        )

        return IncidentResolution(
            incident=incident,
            matched_existing=False,
            correlation_score=0.0,
            matched_event_uid=None,
        )

    (
        existing_incident,
        score,
        matched_event_uid,
    ) = match

    updated_incident = existing_incident.attach_event(
        event.event_uid,
        observed_at=timestamp,
    )

    return IncidentResolution(
        incident=updated_incident,
        matched_existing=True,
        correlation_score=score,
        matched_event_uid=matched_event_uid,
    )