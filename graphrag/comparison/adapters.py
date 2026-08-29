from time import perf_counter
from typing import Protocol

from graphrag.comparison.contracts import (
    RetrievalOutput,
)


class VectorRAGResponseLike(Protocol):

    answer: str
    retrieved_count: int


class VectorRAGPipelineLike(Protocol):

    def answer(
        self,
        query: str,
        top_k: int = 3,
    ) -> VectorRAGResponseLike:
        ...


class GraphRAGResponseLike(Protocol):

    answer: str
    retrieved_entity_count: int
    retrieved_relationship_count: int


class GraphRAGPipelineLike(Protocol):

    def answer(
        self,
        query: str,
        max_depth: int = 2,
        max_entities: int = 20,
    ) -> GraphRAGResponseLike:
        ...


class VectorRAGAdapter:

    def __init__(
        self,
        pipeline: VectorRAGPipelineLike,
        top_k: int = 3,
    ) -> None:
        self.pipeline = pipeline
        self.top_k = top_k

    @property
    def system_name(
        self,
    ) -> str:
        return "vector_rag"

    def answer(
        self,
        query: str,
    ) -> RetrievalOutput:

        start = perf_counter()

        response = (
            self.pipeline.answer(
                query=query,
                top_k=self.top_k,
            )
        )

        latency_ms = (
            perf_counter() - start
        ) * 1000

        return RetrievalOutput(
            system_name=(
                self.system_name
            ),
            answer=response.answer,
            retrieved_evidence_count=(
                response.retrieved_count
            ),
            relationship_count=0,
            latency_ms=latency_ms,
        )


class GraphRAGAdapter:

    def __init__(
        self,
        pipeline: GraphRAGPipelineLike,
        max_depth: int = 2,
        max_entities: int = 20,
    ) -> None:
        self.pipeline = pipeline
        self.max_depth = max_depth
        self.max_entities = max_entities

    @property
    def system_name(
        self,
    ) -> str:
        return "graph_rag"

    def answer(
        self,
        query: str,
    ) -> RetrievalOutput:

        start = perf_counter()

        response = (
            self.pipeline.answer(
                query=query,
                max_depth=self.max_depth,
                max_entities=(
                    self.max_entities
                ),
            )
        )

        latency_ms = (
            perf_counter() - start
        ) * 1000

        return RetrievalOutput(
            system_name=(
                self.system_name
            ),
            answer=response.answer,
            retrieved_evidence_count=(
                response
                .retrieved_entity_count
            ),
            relationship_count=(
                response
                .retrieved_relationship_count
            ),
            latency_ms=latency_ms,
        )