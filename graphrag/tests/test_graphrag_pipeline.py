from graphrag.generation.prompt_builder import (
    GraphRAGPromptBuilder,
)
from graphrag.modeling.entity import Entity
from graphrag.modeling.relationship import (
    Relationship,
)
from graphrag.pipeline.graphrag_pipeline import (
    GraphRAGPipeline,
)
from graphrag.retrieval.context_builder import (
    GraphContextBuilder,
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


class FakeGenerator:

    def __init__(self) -> None:
        self.last_prompt: str | None = None
        self.call_count = 0

    def generate(
        self,
        prompt: str,
    ) -> str:

        self.call_count += 1
        self.last_prompt = prompt

        return (
            "ACC001 initiated TXN001."
        )


def create_pipeline(
    tmp_path,
):
    store = SQLiteGraphStore(
        tmp_path / "graph.db"
    )

    entities = [
        Entity(
            entity_id=(
                "customer:ravi"
            ),
            entity_type="customer",
            name="Ravi Sharma",
        ),
        Entity(
            entity_id=(
                "account:acc001"
            ),
            entity_type="account",
            name="ACC001",
        ),
        Entity(
            entity_id=(
                "transaction:txn001"
            ),
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
            target_id=(
                "transaction:txn001"
            ),
            relationship_type=(
                "initiated"
            ),
        ),
    ]

    for relationship in relationships:
        store.add_relationship(
            relationship
        )

    query_service = (
        GraphQueryService(store)
    )

    retriever = GraphRetriever(
        entity_resolver=(
            EntityResolver(
                query_service
            )
        ),
        traversal=(
            GraphTraversal(
                query_service
            )
        ),
    )

    generator = FakeGenerator()

    pipeline = GraphRAGPipeline(
        retriever=retriever,
        context_builder=(
            GraphContextBuilder()
        ),
        prompt_builder=(
            GraphRAGPromptBuilder()
        ),
        generator=generator,
    )

    return pipeline, generator


def test_pipeline_generates_grounded_answer(
    tmp_path,
):
    pipeline, generator = (
        create_pipeline(tmp_path)
    )

    response = pipeline.answer(
        (
            "What transaction is "
            "connected to ACC001?"
        ),
        max_depth=1,
    )

    assert (
        response.answer
        == "ACC001 initiated TXN001."
    )

    assert response.seed_entity_ids == [
        "account:acc001"
    ]

    assert (
        response.retrieved_entity_count
        == 3
    )

    assert (
        response
        .retrieved_relationship_count
        == 2
    )

    assert (
        "ACC001 [account]"
        in response.graph_context
    )

    assert (
        "--[initiated]-->"
        in response.graph_context
    )

    assert generator.call_count == 1

    assert (
        generator.last_prompt
        is not None
    )

    assert (
        "TXN001 [transaction]"
        in generator.last_prompt
    )


def test_unknown_entity_does_not_call_llm(
    tmp_path,
):
    pipeline, generator = (
        create_pipeline(tmp_path)
    )

    response = pipeline.answer(
        "Tell me about ACC999"
    )

    assert response.seed_entity_ids == []

    assert (
        response.retrieved_entity_count
        == 0
    )

    assert (
        response.answer
        == (
            "I don't know based on the "
            "available graph knowledge."
        )
    )

    assert generator.call_count == 0


def test_pipeline_rejects_empty_query(
    tmp_path,
):
    import pytest

    pipeline, _ = create_pipeline(
        tmp_path
    )

    with pytest.raises(
        ValueError,
        match="query cannot be empty",
    ):
        pipeline.answer("")