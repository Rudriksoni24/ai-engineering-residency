from dataclasses import dataclass

from graphrag.generation.contracts import (
    TextGenerator,
)
from graphrag.generation.prompt_builder import (
    GraphRAGPromptBuilder,
)
from graphrag.retrieval.context_builder import (
    GraphContextBuilder,
)
from graphrag.retrieval.retriever import (
    GraphRetriever,
)


@dataclass(frozen=True)
class GraphRAGResponse:
    answer: str
    seed_entity_ids: list[str]
    retrieved_entity_count: int
    retrieved_relationship_count: int
    graph_context: str


class GraphRAGPipeline:

    def __init__(
        self,
        retriever: GraphRetriever,
        context_builder: GraphContextBuilder,
        prompt_builder: GraphRAGPromptBuilder,
        generator: TextGenerator,
    ) -> None:

        self.retriever = retriever
        self.context_builder = (
            context_builder
        )
        self.prompt_builder = (
            prompt_builder
        )
        self.generator = generator

    def answer(
        self,
        query: str,
        max_depth: int = 2,
        max_entities: int = 20,
    ) -> GraphRAGResponse:

        if not query.strip():
            raise ValueError(
                "query cannot be empty"
            )

        retrieval = (
            self.retriever.retrieve(
                query=query,
                max_depth=max_depth,
                max_entities=max_entities,
            )
        )

        if not retrieval.seeds:
            return GraphRAGResponse(
                answer=(
                    "I don't know based on the "
                    "available graph knowledge."
                ),
                seed_entity_ids=[],
                retrieved_entity_count=0,
                retrieved_relationship_count=0,
                graph_context="",
            )

        graph_context = (
            self.context_builder.build(
                retrieval
            )
        )

        if not graph_context:
            return GraphRAGResponse(
                answer=(
                    "I don't know based on the "
                    "available graph knowledge."
                ),
                seed_entity_ids=[
                    seed.entity_id
                    for seed
                    in retrieval.seeds
                ],
                retrieved_entity_count=(
                    retrieval.entity_count
                ),
                retrieved_relationship_count=(
                    retrieval
                    .relationship_count
                ),
                graph_context="",
            )

        prompt = (
            self.prompt_builder.build(
                query=query,
                graph_context=(
                    graph_context
                ),
            )
        )

        answer = (
            self.generator.generate(
                prompt
            )
        )

        return GraphRAGResponse(
            answer=answer,
            seed_entity_ids=[
                seed.entity_id
                for seed
                in retrieval.seeds
            ],
            retrieved_entity_count=(
                retrieval.entity_count
            ),
            retrieved_relationship_count=(
                retrieval.relationship_count
            ),
            graph_context=graph_context,
        )