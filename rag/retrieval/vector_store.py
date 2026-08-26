import math

from rag.retrieval.types import (
    RetrievalResult,
    VectorRecord,
)


class InMemoryVectorStore:

    def __init__(self):
        self._records: list[VectorRecord] = []
        self._dimension: int | None = None

    def add(
        self,
        records: list[VectorRecord],
    ) -> None:

        if not records:
            return

        for record in records:
            self._validate_dimension(
                record.embedding
            )

            self._records.append(record)

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> list[RetrievalResult]:

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero"
            )

        self._validate_query_dimension(
            query_embedding
        )

        scored_results = [
            (
                record,
                self._cosine_similarity(
                    query_embedding,
                    record.embedding,
                ),
            )
            for record in self._records
        ]

        scored_results.sort(
            key=lambda item: item[1],
            reverse=True,
        )

        return [
            RetrievalResult(
                id=record.id,
                content=record.content,
                source=record.source,
                score=score,
                metadata=record.metadata,
            )
            for record, score in scored_results[:top_k]
        ]

    def _validate_dimension(
        self,
        embedding: list[float],
    ) -> None:

        dimension = len(embedding)

        if dimension == 0:
            raise ValueError(
                "Embedding cannot be empty"
            )

        if self._dimension is None:
            self._dimension = dimension

            return

        if dimension != self._dimension:
            raise ValueError(
                "Embedding dimension mismatch"
            )

    def _validate_query_dimension(
        self,
        embedding: list[float],
    ) -> None:

        if self._dimension is None:
            return

        if len(embedding) != self._dimension:
            raise ValueError(
                "Query embedding dimension mismatch"
            )

    def add_embedded_chunks(
        self,
        chunks,
    ) -> None:

        records = [
            VectorRecord(
                id=chunk.chunk_id,
                embedding=chunk.embedding,
                content=chunk.content,
                source=chunk.source,
                metadata=chunk.metadata.copy(),
            )
            for chunk in chunks
        ]

        self.add(records)

    @staticmethod
    def _cosine_similarity(
        vector_a: list[float],
        vector_b: list[float],
    ) -> float:

        dot_product = sum(
            a * b
            for a, b in zip(
                vector_a,
                vector_b,
                strict=True,
            )
        )

        magnitude_a = math.sqrt(
            sum(
                value ** 2
                for value in vector_a
            )
        )

        magnitude_b = math.sqrt(
            sum(
                value ** 2
                for value in vector_b
            )
        )

        if magnitude_a == 0 or magnitude_b == 0:
            raise ValueError(
                "Zero vectors cannot be compared"
            )

        return dot_product / (
            magnitude_a * magnitude_b
        )