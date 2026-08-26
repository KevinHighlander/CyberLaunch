"""Tests for persistent CLIM intelligence incident identity."""

from datetime import datetime, timedelta, timezone

import pytest

from app.models.intelligence_incident import IntelligenceIncident


def test_create_incident_from_first_event() -> None:
    observed_at = datetime(
        2026,
        8,
        26,
        12,
        0,
        tzinfo=timezone.utc,
    )

    incident = IntelligenceIncident.create(
        "event-1",
        incident_uid="incident-test",
        observed_at=observed_at,
    )

    assert incident.incident_uid == "incident-test"
    assert incident.event_uids == ("event-1",)
    assert incident.event_count == 1
    assert incident.created_at == observed_at
    assert incident.updated_at == observed_at


def test_attach_event_preserves_incident_identity() -> None:
    created_at = datetime(
        2026,
        8,
        26,
        12,
        0,
        tzinfo=timezone.utc,
    )

    updated_at = created_at + timedelta(
        minutes=30
    )

    incident = IntelligenceIncident.create(
        "event-1",
        incident_uid="incident-test",
        observed_at=created_at,
    )

    updated = incident.attach_event(
        "event-2",
        observed_at=updated_at,
    )

    assert updated.incident_uid == incident.incident_uid
    assert updated.created_at == incident.created_at
    assert updated.updated_at == updated_at
    assert updated.event_uids == (
        "event-1",
        "event-2",
    )


def test_duplicate_event_is_not_attached_twice() -> None:
    observed_at = datetime(
        2026,
        8,
        26,
        12,
        0,
        tzinfo=timezone.utc,
    )

    incident = IntelligenceIncident.create(
        "event-1",
        incident_uid="incident-test",
        observed_at=observed_at,
    )

    duplicate = incident.attach_event(
        "event-1",
        observed_at=observed_at,
    )

    assert duplicate is incident
    assert duplicate.event_count == 1


def test_contains_event_reports_membership() -> None:
    incident = IntelligenceIncident.create(
        "event-1",
        incident_uid="incident-test",
    )

    assert incident.contains_event(
        "event-1"
    ) is True

    assert incident.contains_event(
        "event-2"
    ) is False


def test_attach_event_cannot_move_update_time_backward() -> None:
    created_at = datetime(
        2026,
        8,
        26,
        12,
        0,
        tzinfo=timezone.utc,
    )

    incident = IntelligenceIncident.create(
        "event-1",
        incident_uid="incident-test",
        observed_at=created_at,
    )

    earlier = created_at - timedelta(
        minutes=1
    )

    with pytest.raises(
        ValueError,
        match="cannot move backward",
    ):
        incident.attach_event(
            "event-2",
            observed_at=earlier,
        )


def test_incident_requires_timezone_aware_timestamp() -> None:
    naive_timestamp = datetime(
        2026,
        8,
        26,
        12,
        0,
    )

    with pytest.raises(
        ValueError,
        match="timezone-aware",
    ):
        IntelligenceIncident.create(
            "event-1",
            observed_at=naive_timestamp,
        )


def test_incident_rejects_empty_event_uid() -> None:
    with pytest.raises(
        ValueError,
        match="Event UID cannot be empty",
    ):
        IntelligenceIncident.create(
            "   "
        )


def test_incident_rejects_empty_incident_uid() -> None:
    with pytest.raises(
        ValueError,
        match="Incident UID cannot be empty",
    ):
        IntelligenceIncident.create(
            "event-1",
            incident_uid="   ",
        )