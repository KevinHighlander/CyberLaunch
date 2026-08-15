"""Strategic entities tracked by CLIM."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class IntelligenceEntity:
    """A country, organization, military force, or strategic actor."""

    key: str
    display_name: str
    entity_type: str
    theater_keys: tuple[str, ...]
    aliases: tuple[str, ...]
    parent_key: str | None = None


ENTITIES: dict[str, IntelligenceEntity] = {
    "russia": IntelligenceEntity(
        key="russia",
        display_name="Russia",
        entity_type="state",
        theater_keys=("russia", "europe", "arctic", "indo-pacific"),
        aliases=(
            "russia",
            "russian federation",
            "russian",
            "moscow",
        ),
    ),
    "china": IntelligenceEntity(
        key="china",
        display_name="China",
        entity_type="state",
        theater_keys=("indo-pacific",),
        aliases=(
            "china",
            "prc",
            "people's republic of china",
            "beijing",
            "chinese",
        ),
    ),
    "taiwan": IntelligenceEntity(
        key="taiwan",
        display_name="Taiwan",
        entity_type="state",
        theater_keys=("indo-pacific",),
        aliases=(
            "taiwan",
            "republic of china",
            "roc",
            "taipei",
            "taiwanese",
        ),
    ),
    "north-korea": IntelligenceEntity(
        key="north-korea",
        display_name="North Korea",
        entity_type="state",
        theater_keys=("indo-pacific",),
        aliases=(
            "north korea",
            "dprk",
            "democratic people's republic of korea",
            "pyongyang",
            "north korean",
        ),
    ),
    "south-korea": IntelligenceEntity(
        key="south-korea",
        display_name="South Korea",
        entity_type="state",
        theater_keys=("indo-pacific",),
        aliases=(
            "south korea",
            "republic of korea",
            "rok",
            "seoul",
            "south korean",
        ),
    ),
    "japan": IntelligenceEntity(
        key="japan",
        display_name="Japan",
        entity_type="state",
        theater_keys=("indo-pacific",),
        aliases=(
            "japan",
            "japanese",
            "tokyo",
        ),
    ),
    "united-states": IntelligenceEntity(
        key="united-states",
        display_name="United States",
        entity_type="state",
        theater_keys=("americas", "indo-pacific", "europe", "middle-east", "arctic"),
        aliases=(
            "united states",
            "united states of america",
            "usa",
            "u.s.",
            "us",
            "washington",
            "american",
        ),
    ),
    "iran": IntelligenceEntity(
        key="iran",
        display_name="Iran",
        entity_type="state",
        theater_keys=("middle-east",),
        aliases=(
            "iran",
            "iranian",
            "tehran",
            "islamic republic of iran",
        ),
    ),
    "nato": IntelligenceEntity(
        key="nato",
        display_name="NATO",
        entity_type="international-organization",
        theater_keys=("europe", "arctic"),
        aliases=(
            "nato",
            "north atlantic treaty organization",
        ),
    ),
    "iaea": IntelligenceEntity(
        key="iaea",
        display_name="International Atomic Energy Agency",
        entity_type="international-organization",
        theater_keys=("middle-east", "europe"),
        aliases=(
            "iaea",
            "international atomic energy agency",
        ),
    ),
    "pla": IntelligenceEntity(
        key="pla",
        display_name="People's Liberation Army",
        entity_type="military",
        theater_keys=("indo-pacific",),
        aliases=(
            "pla",
            "people's liberation army",
            "chinese military",
        ),
        parent_key="china",
    ),
    "pla-navy": IntelligenceEntity(
        key="pla-navy",
        display_name="People's Liberation Army Navy",
        entity_type="military",
        theater_keys=("indo-pacific",),
        aliases=(
            "plan",
            "pla navy",
            "people's liberation army navy",
            "chinese navy",
        ),
        parent_key="china",
    ),
    "russian-pacific-fleet": IntelligenceEntity(
        key="russian-pacific-fleet",
        display_name="Russian Pacific Fleet",
        entity_type="military",
        theater_keys=("russia", "indo-pacific"),
        aliases=(
            "pacific fleet",
            "russian pacific fleet",
        ),
        parent_key="russia",
    ),
    "irgc": IntelligenceEntity(
        key="irgc",
        display_name="Islamic Revolutionary Guard Corps",
        entity_type="military",
        theater_keys=("middle-east",),
        aliases=(
            "irgc",
            "islamic revolutionary guard corps",
            "revolutionary guards",
        ),
        parent_key="iran",
    ),
}


def get_entity(key: str) -> IntelligenceEntity | None:
    """Return an entity by key."""
    return ENTITIES.get(key)


def get_all_entities() -> tuple[IntelligenceEntity, ...]:
    """Return all registered entities."""
    return tuple(ENTITIES.values())


def find_entities(text: str) -> tuple[IntelligenceEntity, ...]:
    """Return entities whose aliases appear in the supplied text."""
    normalized = text.lower()

    matches = [
        entity
        for entity in ENTITIES.values()
        if any(alias in normalized for alias in entity.aliases)
    ]

    return tuple(matches)


def get_child_entities(parent_key: str) -> tuple[IntelligenceEntity, ...]:
    """Return entities directly associated with a parent entity."""
    return tuple(
        entity
        for entity in ENTITIES.values()
        if entity.parent_key == parent_key
    )