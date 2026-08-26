"""Knowledge graph service for CLIM."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from app.ontology.links import LINKS, EntityLink


@dataclass(frozen=True, slots=True)
class KnowledgeNeighborhood:
    """A deterministic one-hop knowledge graph snapshot."""

    entity_key: str
    neighbor_keys: tuple[str, ...]


class KnowledgeGraph:
    """Simple in-memory relationship graph."""

    def __init__(self) -> None:
        self._graph: dict[str, list[EntityLink]] = defaultdict(list)

        for link in LINKS:
            self._graph[link.source_key].append(link)

            if link.bidirectional:
                reverse = EntityLink(
                    source_key=link.target_key,
                    target_key=link.source_key,
                    relationship=link.relationship,
                    description=link.description,
                    bidirectional=True,
                )

                self._graph[link.target_key].append(reverse)

    def neighbors(
        self,
        entity_key: str,
    ) -> tuple[str, ...]:
        """Return connected entity keys."""
        return tuple(
            sorted(
                link.target_key
                for link in self._graph.get(
                    entity_key,
                    [],
                )
            )
        )

    def relationships(
        self,
        entity_key: str,
    ) -> tuple[EntityLink, ...]:
        """Return relationships for an entity."""
        return tuple(
            self._graph.get(
                entity_key,
                [],
            )
        )

    def snapshot(
        self,
        entity_keys: tuple[str, ...],
    ) -> tuple[KnowledgeNeighborhood, ...]:
        """Return deterministic one-hop neighborhoods for entity keys."""
        return tuple(
            KnowledgeNeighborhood(
                entity_key=entity_key,
                neighbor_keys=self.neighbors(
                    entity_key
                ),
            )
            for entity_key in sorted(
                set(entity_keys)
            )
        )