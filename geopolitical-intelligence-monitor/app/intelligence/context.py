"""Strategic context generation for CLIM."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from app.ontology.entities import IntelligenceEntity
from app.ontology.links import get_link


@dataclass(frozen=True, slots=True)
class ContextRelationship:
    """A known relationship between detected intelligence entities."""

    source_name: str
    target_name: str
    relationship: str
    description: str

    @property
    def statement(self) -> str:
        """Return human-readable strategic context."""
        return (
            f"{self.source_name} and "
            f"{self.target_name} have a known "
            f"{self.relationship.replace('-', ' ')} relationship."
        )


@dataclass(frozen=True, slots=True)
class ContextResult:
    """Strategic context derived from detected entities."""

    relationships: tuple[ContextRelationship, ...]

    @property
    def statements(self) -> tuple[str, ...]:
        """Return human-readable context statements."""
        return tuple(
            relationship.statement
            for relationship in self.relationships
        )


def build_context(
    entities: tuple[IntelligenceEntity, ...],
) -> ContextResult:
    """Build deterministic strategic context for detected entities."""
    entities_by_key = {
        entity.key: entity
        for entity in entities
    }

    relationships: list[ContextRelationship] = []

    for first, second in combinations(entities, 2):
        link = get_link(
            first.key,
            second.key,
        )

        if link is None:
            continue

        source = entities_by_key.get(
            link.source_key
        )

        target = entities_by_key.get(
            link.target_key
        )

        if source is None or target is None:
            continue

        relationships.append(
            ContextRelationship(
                source_name=source.display_name,
                target_name=target.display_name,
                relationship=link.relationship,
                description=link.description,
            )
        )

    return ContextResult(
        relationships=tuple(relationships)
    )