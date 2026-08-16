"""Strategic context generation for CLIM."""

from __future__ import annotations

from dataclasses import dataclass

from app.ontology.entities import IntelligenceEntity
from app.ontology.links import get_link


@dataclass(frozen=True, slots=True)
class ContextResult:
    """Context derived from known relationships between detected entities."""

    statements: tuple[str, ...]


def build_context(
    entities: tuple[IntelligenceEntity, ...],
) -> ContextResult:
    """Build deterministic strategic context for detected entities."""
    statements: list[str] = []

    for index, first in enumerate(entities):
        for second in entities[index + 1 :]:
            link = get_link(
                first.key,
                second.key,
            )

            if link is None:
                continue

            statements.append(
                f"{first.display_name} and "
                f"{second.display_name} have a known "
                f"{link.relationship.replace('-', ' ')} relationship."
            )

    return ContextResult(
        statements=tuple(statements)
    )