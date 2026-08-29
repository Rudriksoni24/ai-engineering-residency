from graphrag.application.contracts import (
    BankingAnswer,
    IngestionResult,
)
from graphrag.extraction.extractor import (
    BankingKnowledgeExtractor,
)
from graphrag.extraction.graph_builder import (
    ExtractionGraphBuilder,
)
from graphrag.pipeline.graphrag_pipeline import (
    GraphRAGPipeline,
)
from graphrag.retrieval.context_builder import (
    GraphContextBuilder,
)
from graphrag.retrieval.retriever import (
    GraphRetriever,
)
from graphrag.storage.contracts import (
    GraphStore,
)


class BankingGraphIntelligenceService:

    def __init__(
        self,
        extractor: BankingKnowledgeExtractor,
        graph_builder: ExtractionGraphBuilder,
        store: GraphStore,
        retriever: GraphRetriever,
        context_builder: GraphContextBuilder,
        pipeline: GraphRAGPipeline,
        max_depth: int = 2,
        max_entities: int = 20,
    ) -> None:

        self.extractor = extractor
        self.graph_builder = graph_builder
        self.store = store
        self.retriever = retriever
        self.context_builder = context_builder
        self.pipeline = pipeline
        self.max_depth = max_depth
        self.max_entities = max_entities

    def ingest(
        self,
        document: str,
    ) -> IngestionResult:

        if not document.strip():
            raise ValueError(
                "document cannot be empty"
            )

        extraction = (
            self.extractor.extract(
                document
            )
        )

        graph = (
            self.graph_builder.build(
                extraction
            )
        )

        for entity in graph.entities:
            self.store.add_entity(
                entity
            )

        for relationship in (
            graph.relationships
        ):
            self.store.add_relationship(
                relationship
            )

        return IngestionResult(
            entity_count=len(
                graph.entities
            ),
            relationship_count=len(
                graph.relationships
            ),
        )

    def retrieve_context(
        self,
        query: str,
    ) -> str:

        if not query.strip():
            raise ValueError(
                "query cannot be empty"
            )

        result = (
            self.retriever.retrieve(
                query=query,
                max_depth=(
                    self.max_depth
                ),
                max_entities=(
                    self.max_entities
                ),
            )
        )

        return (
            self.context_builder.build(
                result
            )
        )

    def answer(
        self,
        query: str,
    ) -> BankingAnswer:

        response = (
            self.pipeline.answer(
                query=query,
                max_depth=(
                    self.max_depth
                ),
                max_entities=(
                    self.max_entities
                ),
            )
        )

        return BankingAnswer(
            answer=response.answer,
            seed_entity_ids=(
                response.seed_entity_ids
            ),
            retrieved_entity_count=(
                response
                .retrieved_entity_count
            ),
            retrieved_relationship_count=(
                response
                .retrieved_relationship_count
            ),
            graph_context=(
                response.graph_context
            ),
        )

    def entity_count(
        self,
    ) -> int:

        return len(
            self.store.get_entities()
        )

    def relationship_count(
        self,
    ) -> int:

        return len(
            self.store
            .get_relationships()
        )