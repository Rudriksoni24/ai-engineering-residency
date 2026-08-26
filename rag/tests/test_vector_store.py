import pytest

from rag.retrieval.types import VectorRecord
from rag.retrieval.vector_store import (
    InMemoryVectorStore,
)


def create_record(
    record_id: str,
    embedding: list[float],
) -> VectorRecord:

    return VectorRecord(
        id=record_id,
        embedding=embedding,
        content=f"content-{record_id}",
        source="test.txt",
        metadata={},
    )


def test_search_returns_most_similar_result():
    store = InMemoryVectorStore()

    store.add(
        [
            create_record(
                "a",
                [1.0, 0.0],
            ),
            create_record(
                "b",
                [0.0, 1.0],
            ),
        ]
    )

    results = store.search(
        query_embedding=[0.9, 0.1],
        top_k=1,
    )

    assert len(results) == 1
    assert results[0].id == "a"


def test_results_are_ordered():
    store = InMemoryVectorStore()

    store.add(
        [
            create_record(
                "a",
                [1.0, 0.0],
            ),
            create_record(
                "b",
                [0.8, 0.2],
            ),
        ]
    )

    results = store.search(
        query_embedding=[1.0, 0.0],
        top_k=2,
    )

    assert results[0].score >= results[1].score


def test_dimension_mismatch():
    store = InMemoryVectorStore()

    store.add(
        [
            create_record(
                "a",
                [1.0, 0.0],
            )
        ]
    )

    with pytest.raises(ValueError):
        store.add(
            [
                create_record(
                    "b",
                    [1.0, 0.0, 0.0],
                )
            ]
        )

def test_query_dimension_mismatch():
    store = InMemoryVectorStore()

    store.add(
        [
            create_record(
                "a",
                [1.0, 0.0],
            )
        ]
    )

    with pytest.raises(ValueError):
        store.search(
            query_embedding=[
                1.0,
                0.0,
                0.0,
            ],
            top_k=1,
        )

def test_query_dimension_mismatch():
    store = InMemoryVectorStore()

    store.add(
        [
            create_record(
                "a",
                [1.0, 0.0],
            )
        ]
    )

    with pytest.raises(ValueError):
        store.search(
            query_embedding=[
                1.0,
                0.0,
                0.0,
            ],
            top_k=1,
        )

