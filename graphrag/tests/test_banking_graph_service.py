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


class FakeGenerator:

    def generate(
        self,
        prompt: str,
    ) -> str:

        if (
            "TXN9001"
            in prompt
        ):
            return (
                "ACC001 initiated "
                "TXN9001."
            )

        return (
            "I don't know based on "
            "the available graph "
            "knowledge."
        )


def create_service(
    tmp_path,
) -> BankingGraphIntelligenceService:

    store = SQLiteGraphStore(
        tmp_path / "banking.db"
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
            FakeGenerator()
        ),
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
        )
    )


def test_ingests_document(
    tmp_path,
):
    service = create_service(
        tmp_path
    )

    result = service.ingest(
        """
        Customer Ravi Sharma owns
        account ACC001.
        Account ACC001 initiated
        transaction TXN9001.
        """
    )

    assert result.entity_count == 3
    assert (
        result.relationship_count
        == 2
    )

    assert (
        service.entity_count()
        == 3
    )

    assert (
        service.relationship_count()
        == 2
    )


def test_retrieves_context(
    tmp_path,
):
    service = create_service(
        tmp_path
    )

    service.ingest(
        """
        Customer Ravi Sharma owns
        account ACC001.
        Account ACC001 initiated
        transaction TXN9001.
        """
    )

    context = (
        service.retrieve_context(
            "What transaction was "
            "initiated by ACC001?"
        )
    )

    assert (
        "ACC001 [account]"
        in context
    )

    assert (
        "TXN9001 [transaction]"
        in context
    )

    assert (
        "--[initiated]-->"
        in context
    )


def test_answers_from_graph(
    tmp_path,
):
    service = create_service(
        tmp_path
    )

    service.ingest(
        """
        Customer Ravi Sharma owns
        account ACC001.
        Account ACC001 initiated
        transaction TXN9001.
        """
    )

    response = service.answer(
        "What transaction was "
        "initiated by ACC001?"
    )

    assert (
        response.answer
        == (
            "ACC001 initiated "
            "TXN9001."
        )
    )

    assert (
        "account:acc001"
        in response.seed_entity_ids
    )


def test_unknown_entity_returns_fallback(
    tmp_path,
):
    service = create_service(
        tmp_path
    )

    service.ingest(
        """
        Customer Ravi Sharma owns
        account ACC001.
        """
    )

    response = service.answer(
        "Tell me about ACC999"
    )

    assert (
        response.answer
        == (
            "I don't know based on "
            "the available graph "
            "knowledge."
        )
    )