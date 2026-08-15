"""Tests for CLIM strategic entities."""

from app.ontology.entities import (
    find_entities,
    get_child_entities,
    get_entity,
)


def test_russia_entity_exists() -> None:
    entity = get_entity("russia")

    assert entity is not None
    assert entity.display_name == "Russia"
    assert "russia" in entity.theater_keys


def test_alias_finds_russia() -> None:
    matches = find_entities(
        "The Russian Federation announced new military activity."
    )

    assert any(
        entity.key == "russia"
        for entity in matches
    )


def test_dprk_alias_finds_north_korea() -> None:
    matches = find_entities(
        "The DPRK conducted another missile launch."
    )

    assert any(
        entity.key == "north-korea"
        for entity in matches
    )


def test_pacific_fleet_links_to_russia() -> None:
    fleet = get_entity("russian-pacific-fleet")

    assert fleet is not None
    assert fleet.parent_key == "russia"


def test_russia_has_child_entities() -> None:
    children = get_child_entities("russia")

    assert any(
        entity.key == "russian-pacific-fleet"
        for entity in children
    )


def test_unknown_entity_returns_none() -> None:
    assert get_entity("definitely-not-real") is None


def test_partial_alias_does_not_match() -> None:
    matches = find_entities(
        "A teenager announced plans to debut in a K-pop group."
    )

    assert all(
        entity.key not in {"pla", "pla-navy"}
        for entity in matches
    )


def test_us_alias_does_not_match_inside_other_words() -> None:
    matches = find_entities(
        "The business announced a new product."
    )

    assert all(
        entity.key != "united-states"
        for entity in matches
    )