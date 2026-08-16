from app.intelligence.knowledge_graph import KnowledgeGraph


def test_neighbors_returns_connected_entities() -> None:
    graph = KnowledgeGraph()

    neighbors = graph.neighbors(
        "russia"
    )

    assert "china" in neighbors
    assert "iran" in neighbors
    assert "north-korea" in neighbors
    assert "japan" in neighbors


def test_bidirectional_neighbors_exist() -> None:
    graph = KnowledgeGraph()

    neighbors = graph.neighbors(
        "china"
    )

    assert "russia" in neighbors


def test_relationship_lookup() -> None:
    graph = KnowledgeGraph()

    relationships = graph.relationships(
        "russia"
    )

    assert len(relationships) >= 4


def test_unknown_entity_has_no_neighbors() -> None:
    graph = KnowledgeGraph()

    assert (
        graph.neighbors(
            "moon"
        )
        == ()
    )