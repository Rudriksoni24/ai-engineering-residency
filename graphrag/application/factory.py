from graphrag.application.banking_service import (
    BankingGraphIntelligenceService,
)
from graphrag.application.config import (
    BankingGraphConfig,
)
from graphrag.extraction.extractor import (
    BankingKnowledgeExtractor,
)
from graphrag.extraction.graph_builder import (
    ExtractionGraphBuilder,
)
from graphrag.generation.ollama_generator import (
    OllamaGenerator,
)
from graphrag.generation.prompt_builder import (
    GraphRAGPromptBuilder,
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


def build_banking_graph_service(
    config: BankingGraphConfig,
) -> BankingGraphIntelligenceService:

    config.database_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    store = SQLiteGraphStore(
        config.database_path
    )

    query_service = (
        GraphQueryService(
            store
        )
    )

    resolver = EntityResolver(
        query_service
    )

    traversal = GraphTraversal(
        query_service
    )

    retriever = GraphRetriever(
        entity_resolver=resolver,
        traversal=traversal,
    )

    context_builder = (
        GraphContextBuilder()
    )

    generator = OllamaGenerator(
        model=config.model
    )

    pipeline = GraphRAGPipeline(
        retriever=retriever,
        context_builder=(
            context_builder
        ),
        prompt_builder=(
            GraphRAGPromptBuilder()
        ),
        generator=generator,
    )

    return (
        BankingGraphIntelligenceService(
            extractor=(
                BankingKnowledgeExtractor()
            ),
            graph_builder=(
                ExtractionGraphBuilder()
            ),
            store=store,
            retriever=retriever,
            context_builder=(
                context_builder
            ),
            pipeline=pipeline,
            max_depth=(
                config.max_depth
            ),
            max_entities=(
                config.max_entities
            ),
        )
    )