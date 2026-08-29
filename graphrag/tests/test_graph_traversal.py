import pytest

from graphrag.modeling.entity import Entity
from graphrag.modeling.relationship import (
    Relationship,
)
from graphrag.retrieval.traversal import (
    GraphTraversal,
)
from graphrag.storage.query_service import (
    GraphQueryService,
)
from graphrag.storage.sqlite_store import (
    SQLiteGraphStore,
)


@pytest.fixture
def traversal_setup(
    tmp_path,
):
    store = SQLiteGraphStore(
        tmp_path / "graph.db"
    )

    entities = [
        Entity(
            entity_id="customer:ravi",
            entity_type="customer",
            name="Ravi Sharma",
        ),
        Entity(
            entity_id="account:acc001",
            entity_type="account",
            name="ACC001",
        ),
        Entity(
            entity_id="transaction:txn001",
            entity_type="transaction",
            name="TXN001",
        ),
        Entity(
            entity_id="fraud_rule:high_value",
            entity_type="fraud_rule",
            name="High Value Rule",
        ),
    ]

    for entity in entities:
        store.add_entity(entity)

    relationships = [
        Relationship(
            relationship_id="rel:001",
            source_id="customer:ravi",
            target_id="account:acc001",
            relationship_type="owns",
        ),
        Relationship(
            relationship_id="rel:002",
            source_id="account:acc001",
            target_id="transaction:txn001",
            relationship_type="initiated",
        ),
        Relationship(
            relationship_id="rel:003",
            source_id="transaction:txn001",
            target_id="fraud_rule:high_value",
            relationship_type="flagged_by",
        ),
    ]

    for relationship in relationships:
        store.add_relationship(
            relationship
        )

    service = GraphQueryService(
        store
    )

    traversal = GraphTraversal(
        service
    )

    seed = service.find_entity(
        "customer:ravi"
    )

    assert seed is not None

    return traversal, seed


def test_depth_zero_returns_seed_only(
    traversal_setup,
):
    traversal, seed = (
        traversal_setup
    )

    result = traversal.traverse(
        seed,
        max_depth=0,
    )

    assert result.entity_count == 1

    assert (
        result.entities[0]
        .entity.entity_id
        == "customer:ravi"
    )

    assert (
        result.entities[0].depth
        == 0
    )


def test_traverses_one_hop(
    traversal_setup,
):
    traversal, seed = (
        traversal_setup
    )

    result = traversal.traverse(
        seed,
        max_depth=1,
    )

    ids = {
        item.entity.entity_id
        for item in result.entities
    }

    assert ids == {
        "customer:ravi",
        "account:acc001",
    }


def test_traverses_multiple_hops(
    traversal_setup,
):
    traversal, seed = (
        traversal_setup
    )

    result = traversal.traverse(
        seed,
        max_depth=3,
    )

    ids = {
        item.entity.entity_id
        for item in result.entities
    }

    assert ids == {
        "customer:ravi",
        "account:acc001",
        "transaction:txn001",
        "fraud_rule:high_value",
    }


def test_tracks_depth(
    traversal_setup,
):
    traversal, seed = (
        traversal_setup
    )

    result = traversal.traverse(
        seed,
        max_depth=3,
    )

    depths = {
        item.entity.entity_id:
        item.depth
        for item in result.entities
    }

    assert depths == {
        "customer:ravi": 0,
        "account:acc001": 1,
        "transaction:txn001": 2,
        "fraud_rule:high_value": 3,
    }


def test_respects_max_entities(
    traversal_setup,
):
    traversal, seed = (
        traversal_setup
    )

    result = traversal.traverse(
        seed,
        max_depth=3,
        max_entities=2,
    )

    assert result.entity_count == 2


def test_rejects_negative_depth(
    traversal_setup,
):
    traversal, seed = (
        traversal_setup
    )

    with pytest.raises(
        ValueError,
        match=(
            "max_depth cannot be negative"
        ),
    ):
        traversal.traverse(
            seed,
            max_depth=-1,
        )