from graphrag.application.banking_service import (
    BankingGraphIntelligenceService,
)
from graphrag.extraction.extractor import (
    BankingKnowledgeExtractor,
)
from graphrag.extraction.graph_builder import (
    ExtractionGraphBuilder,
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


class IntegrationGenerator:

    def generate(
        self,
        prompt: str,
    ) -> str:

        assert (
            "Ravi Sharma [customer]"
            in prompt
        )

        assert (
            "ACC001 [account]"
            in prompt
        )

        assert (
            "TXN9001 [transaction]"
            in prompt
        )

        assert (
            "--[owns]-->"
            in prompt
        )

        assert (
            "--[initiated]-->"
            in prompt
        )

        return (
            "Ravi Sharma owns "
            "ACC001, which initiated "
            "TXN9001."
        )


def test_document_to_graphrag_answer(
    tmp_path,
):
    database_path = (
        tmp_path / "banking.db"
    )

    store = SQLiteGraphStore(
        database_path
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

    context_builder = (
        GraphContextBuilder()
    )

    pipeline = GraphRAGPipeline(
        retriever=retriever,
        context_builder=(
            context_builder
        ),
        prompt_builder=(
            GraphRAGPromptBuilder()
        ),
        generator=(
            IntegrationGenerator()
        ),
    )

    service = (
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
            max_depth=2,
            max_entities=10,
        )
    )

    ingestion = service.ingest(
        """
        Customer Ravi Sharma owns
        account ACC001.
        Account ACC001 initiated
        transaction TXN9001.
        """
    )

    assert ingestion.entity_count == 3
    assert (
        ingestion.relationship_count
        == 2
    )

    response = service.answer(
        (
            "What transaction is "
            "connected to ACC001?"
        )
    )

    assert (
        response.answer
        == (
            "Ravi Sharma owns "
            "ACC001, which initiated "
            "TXN9001."
        )
    )

    assert (
        response.retrieved_entity_count
        == 3
    )

    assert (
        response
        .retrieved_relationship_count
        == 2
    )