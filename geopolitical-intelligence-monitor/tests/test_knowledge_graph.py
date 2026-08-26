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

def test_snapshot_returns_entity_neighborhoods() -> None:
    graph = KnowledgeGraph()

    snapshot = graph.snapshot(
        (
            "russia",
            "china",
            "russia",
        )
    )

    assert tuple(
        neighborhood.entity_key
        for neighborhood in snapshot
    ) == (
        "china",
        "russia",
    )

    russia = next(
        neighborhood
        for neighborhood in snapshot
        if neighborhood.entity_key == "russia"
    )

    assert "china" in russia.neighbor_keys
    assert "iran" in russia.neighbor_keys
    assert "north-korea" in russia.neighbor_keys


def test_snapshot_preserves_unknown_entity() -> None:
    graph = KnowledgeGraph()

    snapshot = graph.snapshot(
        ("moon",)
    )

    assert len(snapshot) == 1
    assert snapshot[0].entity_key == "moon"
    assert snapshot[0].neighbor_keys == ()