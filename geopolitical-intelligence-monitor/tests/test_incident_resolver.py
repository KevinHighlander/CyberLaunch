"""Tests for CLIM cross-run incident resolution."""

from datetime import datetime, timedelta, timezone

from app.enums.source import (
    SourceAuthority,
    SourceReliability,
)
from app.intelligence.incident_resolver import resolve_incident
from app.models.intelligence_incident import IntelligenceIncident
from app.models.normalized_event import NormalizedEvent


_BASE_TIME = datetime(
    2026,
    8,
    26,
    12,
    0,
    tzinfo=timezone.utc,
)


def make_event(
    event_uid: str,
    title: str,
    *,
    summary: str = "",
    source_name: str = "Test Source",
) -> NormalizedEvent:
    """Create deterministic normalized evidence for resolver tests."""
    return NormalizedEvent(
        event_uid=event_uid,
        title=title,
        summary=summary,
        source_name=source_name,
        source_url=(
            f"https://example.com/{event_uid}"
        ),
        source_type="media",
        source_country="United States",
        source_authority=(
            SourceAuthority.SECONDARY
        ),
        source_reliability=(
            SourceReliability.HIGH
        ),
        published_at=None,
        region_hint=None,
    )


def test_unrelated_report_creates_new_incident() -> None:
    existing_event = make_event(
        "event-1",
        "North Korea conducts ballistic missile launch",
    )

    existing_incident = IntelligenceIncident.create(
        existing_event.event_uid,
        incident_uid="incident-existing",
        observed_at=_BASE_TIME,
    )

    new_event = make_event(
        "event-2",
        "China launches military exercises around Taiwan",
    )

    resolution = resolve_incident(
        new_event,
        incidents=(
            existing_incident,
        ),
        evidence_by_uid={
            existing_event.event_uid: existing_event,
        },
        observed_at=(
            _BASE_TIME
            + timedelta(
                minutes=30
            )
        ),
    )

    assert resolution.matched_existing is False
    assert resolution.correlation_score == 0.0
    assert resolution.matched_event_uid is None

    assert resolution.incident.incident_uid != (
        existing_incident.incident_uid
    )

    assert resolution.incident.event_uids == (
        "event-2",
    )


def test_related_report_joins_existing_incident() -> None:
    reuters = make_event(
        "reuters-1",
        "China launches military exercises around Taiwan",
        source_name="Reuters",
    )

    incident = IntelligenceIncident.create(
        reuters.event_uid,
        incident_uid="incident-china-taiwan",
        observed_at=_BASE_TIME,
    )

    bbc = make_event(
        "bbc-1",
        "China begins military exercises around Taiwan",
        source_name="BBC",
    )

    resolution = resolve_incident(
        bbc,
        incidents=(
            incident,
        ),
        evidence_by_uid={
            reuters.event_uid: reuters,
        },
        observed_at=(
            _BASE_TIME
            + timedelta(
                hours=1
            )
        ),
    )

    assert resolution.matched_existing is True

    assert resolution.incident.incident_uid == (
        "incident-china-taiwan"
    )

    assert resolution.incident.event_uids == (
        "reuters-1",
        "bbc-1",
    )

    assert resolution.matched_event_uid == "reuters-1"

    assert resolution.correlation_score >= 0.40


def test_existing_member_returns_same_incident() -> None:
    event = make_event(
        "event-1",
        "China launches military exercises around Taiwan",
    )

    incident = IntelligenceIncident.create(
        event.event_uid,
        incident_uid="incident-1",
        observed_at=_BASE_TIME,
    )

    resolution = resolve_incident(
        event,
        incidents=(
            incident,
        ),
        evidence_by_uid={
            event.event_uid: event,
        },
        observed_at=(
            _BASE_TIME
            + timedelta(
                hours=1
            )
        ),
    )

    assert resolution.matched_existing is True
    assert resolution.correlation_score == 1.0

    assert resolution.matched_event_uid == (
        event.event_uid
    )

    assert resolution.incident is incident


def test_strongest_incident_match_wins() -> None:
    korea_event = make_event(
        "korea-1",
        "North Korea conducts ballistic missile launch",
    )

    taiwan_event = make_event(
        "taiwan-1",
        "China launches military exercises around Taiwan",
    )

    korea_incident = IntelligenceIncident.create(
        korea_event.event_uid,
        incident_uid="incident-korea",
        observed_at=_BASE_TIME,
    )

    taiwan_incident = IntelligenceIncident.create(
        taiwan_event.event_uid,
        incident_uid="incident-taiwan",
        observed_at=_BASE_TIME,
    )

    new_event = make_event(
        "taiwan-2",
        "China begins military exercises around Taiwan",
    )

    resolution = resolve_incident(
        new_event,
        incidents=(
            korea_incident,
            taiwan_incident,
        ),
        evidence_by_uid={
            korea_event.event_uid: korea_event,
            taiwan_event.event_uid: taiwan_event,
        },
        observed_at=(
            _BASE_TIME
            + timedelta(
                hours=1
            )
        ),
    )

    assert resolution.matched_existing is True

    assert resolution.incident.incident_uid == (
        "incident-taiwan"
    )

    assert resolution.matched_event_uid == (
        "taiwan-1"
    )


def test_missing_historical_evidence_is_ignored() -> None:
    incident = IntelligenceIncident.create(
        "missing-event",
        incident_uid="incident-missing",
        observed_at=_BASE_TIME,
    )

    new_event = make_event(
        "event-new",
        "China launches military exercises around Taiwan",
    )

    resolution = resolve_incident(
        new_event,
        incidents=(
            incident,
        ),
        evidence_by_uid={},
        observed_at=(
            _BASE_TIME
            + timedelta(
                hours=1
            )
        ),
    )

    assert resolution.matched_existing is False

    assert resolution.incident.incident_uid != (
        incident.incident_uid
    )

    assert resolution.incident.event_uids == (
        "event-new",
    )


def test_custom_threshold_can_reject_match() -> None:
    existing_event = make_event(
        "event-1",
        "China launches military exercises around Taiwan",
    )

    incident = IntelligenceIncident.create(
        existing_event.event_uid,
        incident_uid="incident-1",
        observed_at=_BASE_TIME,
    )

    new_event = make_event(
        "event-2",
        "China begins military exercises around Taiwan",
    )

    resolution = resolve_incident(
        new_event,
        incidents=(
            incident,
        ),
        evidence_by_uid={
            existing_event.event_uid: existing_event,
        },
        observed_at=(
            _BASE_TIME
            + timedelta(
                hours=1
            )
        ),
        threshold=0.90,
    )

    assert resolution.matched_existing is False

    assert resolution.incident.incident_uid != (
        incident.incident_uid
    )


def test_attaching_report_advances_incident_update_time() -> None:
    existing_event = make_event(
        "event-1",
        "China launches military exercises around Taiwan",
    )

    incident = IntelligenceIncident.create(
        existing_event.event_uid,
        incident_uid="incident-1",
        observed_at=_BASE_TIME,
    )

    new_event = make_event(
        "event-2",
        "China begins military exercises around Taiwan",
    )

    observed_at = (
        _BASE_TIME
        + timedelta(
            hours=2
        )
    )

    resolution = resolve_incident(
        new_event,
        incidents=(
            incident,
        ),
        evidence_by_uid={
            existing_event.event_uid: existing_event,
        },
        observed_at=observed_at,
    )

    assert resolution.matched_existing is True

    assert (
        resolution.incident.created_at
        == _BASE_TIME
    )

    assert (
        resolution.incident.updated_at
        == observed_at
    )


def test_equal_matches_use_deterministic_incident_uid_order() -> None:
    first_evidence = make_event(
        "evidence-a",
        "China launches military exercises around Taiwan",
    )

    second_evidence = make_event(
        "evidence-b",
        "China launches military exercises around Taiwan",
    )

    incident_b = IntelligenceIncident.create(
        second_evidence.event_uid,
        incident_uid="incident-b",
        observed_at=_BASE_TIME,
    )

    incident_a = IntelligenceIncident.create(
        first_evidence.event_uid,
        incident_uid="incident-a",
        observed_at=_BASE_TIME,
    )

    new_event = make_event(
        "event-new",
        "China launches military exercises around Taiwan",
    )

    resolution = resolve_incident(
        new_event,
        incidents=(
            incident_b,
            incident_a,
        ),
        evidence_by_uid={
            first_evidence.event_uid: first_evidence,
            second_evidence.event_uid: second_evidence,
        },
        observed_at=(
            _BASE_TIME
            + timedelta(
                hours=1
            )
        ),
    )

    assert resolution.matched_existing is True

    assert resolution.incident.incident_uid == (
        "incident-a"
    )

    assert resolution.matched_event_uid == (
        "evidence-a"
    )