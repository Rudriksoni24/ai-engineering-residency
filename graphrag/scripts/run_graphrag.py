import os
from pathlib import Path

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


def build_pipeline(
    model: str,
) -> GraphRAGPipeline:

    database_path = Path(
        "data/graphrag/"
        "banking_knowledge.db"
    )

    database_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    document = """
    Customer Ravi Sharma owns account ACC001.
    Account ACC001 initiated transaction TXN9001.
    """

    extraction = (
        BankingKnowledgeExtractor()
        .extract(document)
    )

    graph = (
        ExtractionGraphBuilder()
        .build(extraction)
    )

    store = SQLiteGraphStore(
        database_path
    )

    for entity in graph.entities:
        store.add_entity(entity)

    for relationship in (
        graph.relationships
    ):
        store.add_relationship(
            relationship
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

    return GraphRAGPipeline(
        retriever=retriever,
        context_builder=(
            GraphContextBuilder()
        ),
        prompt_builder=(
            GraphRAGPromptBuilder()
        ),
        generator=(
            OllamaGenerator(
                model=model
            )
        ),
    )


def main() -> None:

    model = os.getenv(
        "OLLAMA_MODEL"
    )

    if not model:
        raise RuntimeError(
            "OLLAMA_MODEL is not set. "
            "Set it to an installed "
            "Ollama model."
        )

    query = (
        "What transaction was "
        "initiated by ACC001?"
    )

    pipeline = build_pipeline(
        model=model
    )

    print("=" * 60)
    print(
        "SPRINT 4 DAY 5 — "
        "GRAPHRAG PIPELINE"
    )
    print("=" * 60)

    print(f"\nModel: {model}")
    print(f"\nQuestion:\n{query}")

    response = pipeline.answer(
        query=query,
        max_depth=2,
        max_entities=10,
    )

    print("\nAnswer:")
    print(response.answer)

    print("\nSeed entities:")

    for entity_id in (
        response.seed_entity_ids
    ):
        print(f"- {entity_id}")

    print(
        "\nRetrieved entities: "
        f"{response.retrieved_entity_count}"
    )

    print(
        "Retrieved relationships: "
        f"{response.retrieved_relationship_count}"
    )

    print("\nGraph context:\n")

    print(
        response.graph_context
        if response.graph_context
        else "No graph context found."
    )

    print("\n" + "=" * 60)
    print(
        "GraphRAG Pipeline completed."
    )
    print("=" * 60)


if __name__ == "__main__":
    main()