from dataclasses import dataclass

from graphrag.comparison.adapters import (
    GraphRAGAdapter,
    VectorRAGAdapter,
)


@dataclass(frozen=True)
class FakeVectorResponse:
    answer: str
    retrieved_count: int


class FakeVectorPipeline:

    def answer(
        self,
        query: str,
        top_k: int = 3,
    ) -> FakeVectorResponse:

        return FakeVectorResponse(
            answer=(
                "ACC001 initiated "
                "TXN9001."
            ),
            retrieved_count=2,
        )


@dataclass(frozen=True)
class FakeGraphResponse:
    answer: str
    retrieved_entity_count: int
    retrieved_relationship_count: int


class FakeGraphPipeline:

    def answer(
        self,
        query: str,
        max_depth: int = 2,
        max_entities: int = 20,
    ) -> FakeGraphResponse:

        return FakeGraphResponse(
            answer=(
                "ACC001 initiated "
                "TXN9001."
            ),
            retrieved_entity_count=3,
            retrieved_relationship_count=2,
        )


def test_vector_adapter():

    adapter = VectorRAGAdapter(
        FakeVectorPipeline()
    )

    result = adapter.answer(
        "What transaction was "
        "initiated by ACC001?"
    )

    assert (
        result.system_name
        == "vector_rag"
    )

    assert (
        result.retrieved_evidence_count
        == 2
    )

    assert (
        result.relationship_count
        == 0
    )


def test_graph_adapter():

    adapter = GraphRAGAdapter(
        FakeGraphPipeline()
    )

    result = adapter.answer(
        "What transaction was "
        "initiated by ACC001?"
    )

    assert (
        result.system_name
        == "graph_rag"
    )

    assert (
        result.retrieved_evidence_count
        == 3
    )

    assert (
        result.relationship_count
        == 2
    )