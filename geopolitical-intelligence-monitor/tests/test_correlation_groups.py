"""Tests for CLIM correlation groups."""

from app.enums.source import (
    SourceAuthority,
    SourceReliability,
)
from app.intelligence.correlation_groups import group_events
from app.models.normalized_event import NormalizedEvent


def make_event(
    title: str,
    *,
    source: str,
) -> NormalizedEvent:
    """Create a normalized report for correlation testing."""
    return NormalizedEvent(
        event_uid=f"{source}-{title}",
        title=title,
        summary="",
        source_name=source,
        source_url=f"https://example.com/{source}",
        source_type="media",
        source_country=None,
        source_authority=SourceAuthority.SECONDARY,
        source_reliability=SourceReliability.HIGH,
    )


def test_related_reports_form_one_group() -> None:
    events = [
        make_event(
            "China launches military exercises around Taiwan",
            source="Reuters",
        ),
        make_event(
            "China begins military drills near Taiwan",
            source="BBC",
        ),
    ]

    groups = group_events(events)

    assert len(groups) == 1
    assert groups[0].event_count == 2


def test_unrelated_reports_form_separate_groups() -> None:
    events = [
        make_event(
            "China launches military exercises around Taiwan",
            source="Reuters",
        ),
        make_event(
            "North Korea conducts ballistic missile launch",
            source="BBC",
        ),
    ]

    groups = group_events(events)

    assert len(groups) == 2


def test_multiple_sources_create_corroboration() -> None:
    events = [
        make_event(
            "China launches military exercises around Taiwan",
            source="Reuters",
        ),
        make_event(
            "China begins military drills near Taiwan",
            source="BBC",
        ),
    ]

    group = group_events(events)[0]

    assert group.source_count == 2
    assert group.is_corroborated is True


def test_duplicate_source_does_not_increase_source_count() -> None:
    events = [
        make_event(
            "China launches military exercises around Taiwan",
            source="Reuters",
        ),
        make_event(
            "China begins military drills near Taiwan",
            source="Reuters",
        ),
    ]

    group = group_events(events)[0]

    assert group.event_count == 2
    assert group.source_count == 1
    assert group.is_corroborated is False


def test_empty_event_list_returns_no_groups() -> None:
    assert group_events([]) == ()