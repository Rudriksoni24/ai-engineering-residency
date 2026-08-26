from rag.retrieval.retriever import Retriever
from rag.retrieval.types import VectorRecord
from rag.retrieval.vector_store import (
    InMemoryVectorStore,
)


class FakeEmbedder:

    def embed_text(
        self,
        text: str,
    ) -> list[float]:

        if "payment" in text.lower():
            return [1.0, 0.0]

        return [0.0, 1.0]


def test_retriever():
    store = InMemoryVectorStore()

    store.add(
        [
            VectorRecord(
                id="payment",
                embedding=[1.0, 0.0],
                content="Payment reconciliation policy",
                source="policy.txt",
                metadata={},
            ),
            VectorRecord(
                id="weather",
                embedding=[0.0, 1.0],
                content="Weather information",
                source="weather.txt",
                metadata={},
            ),
        ]
    )

    retriever = Retriever(
        embedder=FakeEmbedder(),
        vector_store=store,
    )

    results = retriever.retrieve(
        "payment mismatch",
        top_k=1,
    )

    assert results[0].id == "payment"