"""Tests for CLIM strategic entity relationships."""

from app.ontology.links import (
    get_link,
    get_links_for_entity,
)


def test_russia_china_relationship_exists() -> None:
    link = get_link(
        "russia",
        "china",
    )

    assert link is not None
    assert link.relationship == "strategic-partnership"


def test_relationship_lookup_is_bidirectional() -> None:
    link = get_link(
        "china",
        "russia",
    )

    assert link is not None
    assert link.relationship == "strategic-partnership"


def test_russia_has_multiple_relationships() -> None:
    links = get_links_for_entity(
        "russia"
    )

    assert len(links) >= 4


def test_china_taiwan_relationship_exists() -> None:
    link = get_link(
        "china",
        "taiwan",
    )

    assert link is not None
    assert link.relationship == "sovereignty-dispute"


def test_unknown_relationship_returns_none() -> None:
    assert (
        get_link(
            "iaea",
            "russian-pacific-fleet",
        )
        is None
    )