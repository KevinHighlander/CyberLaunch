from app.intelligence.correlation import correlate
from app.models.normalized_event import NormalizedEvent
from app.enums.source import (
    SourceAuthority,
    SourceReliability,
)


def make_event(title: str) -> NormalizedEvent:
    return NormalizedEvent(
        event_uid=title,
        title=title,
        summary="",
        source_name="Test",
        source_url="https://example.com",
        source_type="media",
        source_country="United States",
        source_authority=SourceAuthority.SECONDARY,
        source_reliability=SourceReliability.HIGH,
    )


def test_same_story_matches() -> None:
    left = make_event(
        "China launches military exercises around Taiwan"
    )

    right = make_event(
        "China begins military drills near Taiwan"
    )

    result = correlate(
        left,
        right,
    )

    assert result.is_match
    assert result.score > 0.40


def test_unrelated_story_does_not_match() -> None:
    left = make_event(
        "China launches military exercises around Taiwan"
    )

    right = make_event(
        "Baby Shark Boy set to make K-pop debut"
    )

    result = correlate(
        left,
        right,
    )

    assert not result.is_match


def test_shared_terms_are_reported() -> None:
    left = make_event(
        "North Korea missile launch"
    )

    right = make_event(
        "North Korea conducts missile test"
    )

    result = correlate(
        left,
        right,
    )

    assert "north" in result.shared_terms
    assert "korea" in result.shared_terms
    assert "missile" in result.shared_terms