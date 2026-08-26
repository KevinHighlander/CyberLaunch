"""Tests for CLIM persistent incident storage."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from app.models.intelligence_incident import IntelligenceIncident
from app.storage.incident_repository import IncidentRepository


def make_incident(
    *,
    incident_uid: str = "incident-1",
    event_uid: str = "event-1",
    observed_at: datetime | None = None,
) -> IntelligenceIncident:
    """Create a deterministic incident for repository testing."""
    timestamp = (
        observed_at
        if observed_at is not None
        else datetime(
            2026,
            8,
            26,
            12,
            0,
            tzinfo=timezone.utc,
        )
    )

    return IntelligenceIncident.create(
        event_uid,
        incident_uid=incident_uid,
        observed_at=timestamp,
    )


def test_repository_saves_and_reloads_incident(
    tmp_path: Path,
) -> None:
    repository = IncidentRepository(
        tmp_path / "clim.db"
    )

    repository.initialize()

    incident = make_incident()

    repository.save(
        incident
    )

    loaded = repository.get(
        incident.incident_uid
    )

    assert loaded is not None
    assert loaded.incident_uid == incident.incident_uid
    assert loaded.created_at == incident.created_at
    assert loaded.updated_at == incident.updated_at
    assert loaded.event_uids == incident.event_uids


def test_repository_updates_incident_membership(
    tmp_path: Path,
) -> None:
    repository = IncidentRepository(
        tmp_path / "clim.db"
    )

    repository.initialize()

    incident = make_incident()

    repository.save(
        incident
    )

    updated = incident.attach_event(
        "event-2",
        observed_at=(
            incident.updated_at
            + timedelta(
                minutes=30
            )
        ),
    )

    repository.save(
        updated
    )

    loaded = repository.get(
        incident.incident_uid
    )

    assert loaded is not None

    assert loaded.event_uids == (
        "event-1",
        "event-2",
    )

    assert loaded.updated_at == updated.updated_at


def test_repository_preserves_member_order(
    tmp_path: Path,
) -> None:
    repository = IncidentRepository(
        tmp_path / "clim.db"
    )

    repository.initialize()

    incident = make_incident()

    second = incident.attach_event(
        "event-2",
        observed_at=(
            incident.updated_at
            + timedelta(
                minutes=10
            )
        ),
    )

    third = second.attach_event(
        "event-3",
        observed_at=(
            second.updated_at
            + timedelta(
                minutes=10
            )
        ),
    )

    repository.save(
        third
    )

    loaded = repository.get(
        third.incident_uid
    )

    assert loaded is not None

    assert loaded.event_uids == (
        "event-1",
        "event-2",
        "event-3",
    )


def test_find_by_event_returns_incident(
    tmp_path: Path,
) -> None:
    repository = IncidentRepository(
        tmp_path / "clim.db"
    )

    repository.initialize()

    incident = make_incident()

    repository.save(
        incident
    )

    loaded = repository.find_by_event(
        "event-1"
    )

    assert loaded is not None
    assert loaded.incident_uid == incident.incident_uid


def test_missing_incident_returns_none(
    tmp_path: Path,
) -> None:
    repository = IncidentRepository(
        tmp_path / "clim.db"
    )

    repository.initialize()

    assert repository.get(
        "missing-incident"
    ) is None

    assert repository.find_by_event(
        "missing-event"
    ) is None


def test_repository_counts_incidents(
    tmp_path: Path,
) -> None:
    repository = IncidentRepository(
        tmp_path / "clim.db"
    )

    repository.initialize()

    repository.save(
        make_incident(
            incident_uid="incident-1",
            event_uid="event-1",
        )
    )

    repository.save(
        make_incident(
            incident_uid="incident-2",
            event_uid="event-2",
        )
    )

    assert repository.count() == 2


def test_saving_same_incident_is_idempotent(
    tmp_path: Path,
) -> None:
    repository = IncidentRepository(
        tmp_path / "clim.db"
    )

    repository.initialize()

    incident = make_incident()

    repository.save(
        incident
    )

    repository.save(
        incident
    )

    loaded = repository.get(
        incident.incident_uid
    )

    assert loaded is not None
    assert loaded.event_count == 1
    assert repository.count() == 1


def test_event_cannot_belong_to_two_incidents(
    tmp_path: Path,
) -> None:
    repository = IncidentRepository(
        tmp_path / "clim.db"
    )

    repository.initialize()

    first = make_incident(
        incident_uid="incident-1",
        event_uid="event-1",
    )

    second = make_incident(
        incident_uid="incident-2",
        event_uid="event-1",
    )

    repository.save(
        first
    )

    with pytest.raises(
        ValueError,
        match="already belongs",
    ):
        repository.save(
            second
        )

    assert repository.count() == 1

    loaded = repository.find_by_event(
        "event-1"
    )

    assert loaded is not None
    assert loaded.incident_uid == "incident-1"