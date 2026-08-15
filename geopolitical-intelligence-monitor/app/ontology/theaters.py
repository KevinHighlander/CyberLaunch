"""Geopolitical theaters for CLIM."""

from __future__ import annotations

from dataclasses import dataclass

from app.ontology.domains import get_domain


@dataclass(frozen=True, slots=True)
class IntelligenceTheater:
    """A geographic or strategic theater within an intelligence domain."""

    key: str
    display_name: str
    domain_key: str
    description: str


THEATERS: dict[str, IntelligenceTheater] = {
    "indo-pacific": IntelligenceTheater(
        key="indo-pacific",
        display_name="Indo-Pacific",
        domain_key="geopolitics",
        description=(
            "Strategic competition and security developments involving East Asia, "
            "Southeast Asia, the western Pacific, and adjacent maritime regions."
        ),
    ),
    "russia": IntelligenceTheater(
        key="russia",
        display_name="Russia",
        domain_key="geopolitics",
        description=(
            "Russian political, military, diplomatic, economic, and strategic "
            "activity with regional or global security implications."
        ),
    ),
    "middle-east": IntelligenceTheater(
        key="middle-east",
        display_name="Middle East",
        domain_key="geopolitics",
        description=(
            "Regional conflict, military posture, diplomacy, energy security, "
            "and strategic competition across the Middle East."
        ),
    ),
    "europe": IntelligenceTheater(
        key="europe",
        display_name="Europe",
        domain_key="geopolitics",
        description=(
            "European security, NATO activity, territorial disputes, military "
            "deployments, and interstate political developments."
        ),
    ),
    "arctic": IntelligenceTheater(
        key="arctic",
        display_name="Arctic",
        domain_key="geopolitics",
        description=(
            "Military access, shipping routes, resource competition, sovereignty, "
            "and strategic activity across the Arctic region."
        ),
    ),
    "americas": IntelligenceTheater(
        key="americas",
        display_name="Americas",
        domain_key="geopolitics",
        description=(
            "Strategic, military, diplomatic, and security developments across "
            "North America, Central America, South America, and the Caribbean."
        ),
    ),
    "africa": IntelligenceTheater(
        key="africa",
        display_name="Africa",
        domain_key="geopolitics",
        description=(
            "Conflict, state instability, military activity, foreign influence, "
            "and strategic competition across the African continent."
        ),
    ),
}


def get_theater(key: str) -> IntelligenceTheater | None:
    """Return a theater by key."""
    return THEATERS.get(key)


def get_all_theaters() -> tuple[IntelligenceTheater, ...]:
    """Return all registered theaters."""
    return tuple(THEATERS.values())


def get_theaters_for_domain(
    domain_key: str,
) -> tuple[IntelligenceTheater, ...]:
    """Return theaters belonging to a registered domain."""
    if get_domain(domain_key) is None:
        return ()

    return tuple(
        theater
        for theater in THEATERS.values()
        if theater.domain_key == domain_key
    )