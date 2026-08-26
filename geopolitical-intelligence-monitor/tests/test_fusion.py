"""Tests for CLIM multi-source intelligence fusion."""

from app.enums.source import (
    SourceAuthority,
    SourceReliability,
)
from app.intelligence.fusion import fuse_events
from app.models.normalized_event import NormalizedEvent


def make_event(
    title: str,
    *,
    source: str,
) -> NormalizedEvent:
    """Create a normalized event for fusion testing."""
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


def test_related_reports_become_one_fused_event() -> None:
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

    fused = fuse_events(events)

    assert len(fused) == 1
    assert fused[0].group.event_count == 2


def test_fused_event_tracks_independent_sources() -> None:
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

    fused = fuse_events(events)[0]

    assert fused.source_count == 2
    assert fused.is_corroborated is True


def test_unrelated_reports_remain_separate() -> None:
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

    fused = fuse_events(events)

    assert len(fused) == 2


def test_fused_event_includes_source_diversity() -> None:
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

    fused = fuse_events(events)[0]

    assert fused.source_diversity.unique_sources == 2


def test_duplicate_source_does_not_inflate_fused_diversity() -> None:
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

    fused = fuse_events(events)[0]

    assert fused.source_diversity.unique_sources == 1


def test_fusion_confidence_uses_corroborating_sources() -> None:
    single = fuse_events(
        [
            make_event(
                "China launches military exercises around Taiwan",
                source="Reuters",
            ),
        ]
    )[0]

    corroborated = fuse_events(
        [
            make_event(
                "China launches military exercises around Taiwan",
                source="Reuters",
            ),
            make_event(
                "China begins military drills near Taiwan",
                source="BBC",
            ),
        ]
    )[0]

    assert (
        corroborated.analysis.confidence.score
        > single.analysis.confidence.score
    )


def test_fused_event_contains_only_external_knowledge_neighbors() -> None:
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

    fused = fuse_events(events)[0]

    china = next(
        neighborhood
        for neighborhood in fused.knowledge_neighborhoods
        if neighborhood.entity_key == "china"
    )

    assert "russia" in china.neighbor_keys
    assert "taiwan" not in china.neighbor_keys


def test_knowledge_graph_does_not_invent_detected_entities() -> None:
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

    fused = fuse_events(events)[0]

    detected_entities = {
        entity.key
        for entity in fused.analysis.entities
    }

    china = next(
        neighborhood
        for neighborhood in fused.knowledge_neighborhoods
        if neighborhood.entity_key == "china"
    )

    assert "russia" in china.neighbor_keys
    assert "russia" not in detected_entities


def test_detected_entities_are_not_repeated_as_background_knowledge() -> None:
    events = [
        make_event(
            "China launches military exercises around Taiwan",
            source="Reuters",
        ),
    ]

    fused = fuse_events(events)[0]

    detected_keys = {
        entity.key
        for entity in fused.analysis.entities
    }

    background_keys = {
        neighbor_key
        for neighborhood in fused.knowledge_neighborhoods
        for neighbor_key in neighborhood.neighbor_keys
    }

    assert detected_keys.isdisjoint(
        background_keys
    )


def test_fused_event_has_deterministic_summary() -> None:
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

    fused = fuse_events(events)[0]

    assert fused.summary == (
        "2 reports from 2 independent sources describe "
        "Military Exercise involving China, Taiwan."
    )


def test_single_report_summary_uses_singular_language() -> None:
    fused = fuse_events(
        [
            make_event(
                "North Korea conducts ballistic missile launch",
                source="Reuters",
            ),
        ]
    )[0]

    assert fused.summary == (
        "1 report from 1 source describes "
        "Ballistic Missile Launch involving North Korea."
    )