"""Strategic relationships between CLIM entities."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EntityLink:
    """A known strategic relationship between two intelligence entities."""

    source_key: str
    target_key: str
    relationship: str
    description: str
    bidirectional: bool = True


LINKS: tuple[EntityLink, ...] = (
    EntityLink(
        source_key="russia",
        target_key="china",
        relationship="strategic-partnership",
        description=(
            "Strategic political, economic, and military cooperation "
            "between Russia and China."
        ),
    ),
    EntityLink(
        source_key="russia",
        target_key="north-korea",
        relationship="military-cooperation",
        description=(
            "Military and strategic cooperation between Russia "
            "and North Korea."
        ),
    ),
    EntityLink(
        source_key="russia",
        target_key="iran",
        relationship="defense-cooperation",
        description=(
            "Defense and strategic cooperation between Russia and Iran."
        ),
    ),
    EntityLink(
        source_key="russia",
        target_key="japan",
        relationship="territorial-dispute",
        description=(
            "Long-running territorial dispute involving the Kuril Islands "
            "and Japan's Northern Territories claim."
        ),
    ),
    EntityLink(
        source_key="china",
        target_key="taiwan",
        relationship="sovereignty-dispute",
        description=(
            "Cross-strait sovereignty dispute and associated military "
            "and political tensions."
        ),
    ),
    EntityLink(
        source_key="united-states",
        target_key="japan",
        relationship="security-alliance",
        description=(
            "Formal bilateral security alliance between the United States "
            "and Japan."
        ),
    ),
    EntityLink(
        source_key="united-states",
        target_key="south-korea",
        relationship="security-alliance",
        description=(
            "Formal bilateral security alliance between the United States "
            "and South Korea."
        ),
    ),
)


def get_links_for_entity(
    entity_key: str,
) -> tuple[EntityLink, ...]:
    """Return relationships involving an entity."""
    return tuple(
        link
        for link in LINKS
        if (
            link.source_key == entity_key
            or (
                link.bidirectional
                and link.target_key == entity_key
            )
        )
    )


def get_link(
    first_key: str,
    second_key: str,
) -> EntityLink | None:
    """Return the relationship between two entities when known."""
    for link in LINKS:
        if (
            link.source_key == first_key
            and link.target_key == second_key
        ):
            return link

        if (
            link.bidirectional
            and link.source_key == second_key
            and link.target_key == first_key
        ):
            return link

    return None