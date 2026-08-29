from graphrag.modeling.entity import Entity
from graphrag.modeling.relationship import (
    Relationship,
)
from graphrag.retrieval.entity_resolver import (
    EntityResolver,
)
from graphrag.retrieval.retriever import (
    GraphRetriever,
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


def create_retriever(
    tmp_path,
) -> GraphRetriever:

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
    ]

    for relationship in relationships:
        store.add_relationship(
            relationship
        )

    service = GraphQueryService(
        store
    )

    return GraphRetriever(
        entity_resolver=(
            EntityResolver(service)
        ),
        traversal=(
            GraphTraversal(service)
        ),
    )


def test_retrieves_graph_from_query(
    tmp_path,
):
    retriever = create_retriever(
        tmp_path
    )

    result = retriever.retrieve(
        "What transactions are "
        "connected to ACC001?",
        max_depth=1,
    )

    assert len(result.seeds) == 1

    assert (
        result.seeds[0].entity_id
        == "account:acc001"
    )

    ids = {
        item.entity.entity_id
        for item in result.entities
    }

    assert ids == {
        "customer:ravi",
        "account:acc001",
        "transaction:txn001",
    }

    assert (
        result.relationship_count
        == 2
    )


def test_unknown_entity_returns_empty_result(
    tmp_path,
):
    retriever = create_retriever(
        tmp_path
    )

    result = retriever.retrieve(
        "Tell me about ACC999"
    )

    assert result.seeds == []
    assert result.entities == []
    assert result.relationships == []