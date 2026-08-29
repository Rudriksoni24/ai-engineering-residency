import pytest

from graphrag.modeling.entity import Entity
from graphrag.modeling.graph import KnowledgeGraph
from graphrag.modeling.relationship import (
    Relationship,
)


def create_graph() -> KnowledgeGraph:
    graph = KnowledgeGraph()

    graph.add_entity(
        Entity(
            entity_id="customer:001",
            entity_type="customer",
            name="Ravi Sharma",
        )
    )

    graph.add_entity(
        Entity(
            entity_id="account:001",
            entity_type="account",
            name="Savings Account",
        )
    )

    graph.add_entity(
        Entity(
            entity_id="transaction:001",
            entity_type="transaction",
            name="Payment Transaction",
        )
    )

    return graph


def test_graph_adds_entities():
    graph = create_graph()

    assert len(graph.entities) == 3


def test_graph_retrieves_entity():
    graph = create_graph()

    entity = graph.get_entity(
        "customer:001"
    )

    assert entity is not None
    assert entity.name == "Ravi Sharma"


def test_duplicate_entity_is_rejected():
    graph = create_graph()

    with pytest.raises(
        ValueError,
        match="Entity already exists",
    ):
        graph.add_entity(
            Entity(
                entity_id="customer:001",
                entity_type="customer",
                name="Duplicate",
            )
        )


def test_graph_adds_relationship():
    graph = create_graph()

    graph.add_relationship(
        Relationship(
            relationship_id="rel:001",
            source_id="customer:001",
            target_id="account:001",
            relationship_type="owns",
        )
    )

    assert len(
        graph.relationships
    ) == 1


def test_relationship_requires_existing_source():
    graph = create_graph()

    with pytest.raises(
        ValueError,
        match="Unknown source entity",
    ):
        graph.add_relationship(
            Relationship(
                relationship_id="rel:001",
                source_id="customer:999",
                target_id="account:001",
                relationship_type="owns",
            )
        )


def test_neighbors_returns_connected_entities():
    graph = create_graph()

    graph.add_relationship(
        Relationship(
            relationship_id="rel:001",
            source_id="customer:001",
            target_id="account:001",
            relationship_type="owns",
        )
    )

    neighbors = graph.neighbors(
        "customer:001"
    )

    assert len(neighbors) == 1
    assert (
        neighbors[0].entity_id
        == "account:001"
    )


def test_outgoing_relationships():
    graph = create_graph()

    graph.add_relationship(
        Relationship(
            relationship_id="rel:001",
            source_id="customer:001",
            target_id="account:001",
            relationship_type="owns",
        )
    )

    relationships = (
        graph.outgoing_relationships(
            "customer:001"
        )
    )

    assert len(relationships) == 1
    assert (
        relationships[0].relationship_type
        == "owns"
    )