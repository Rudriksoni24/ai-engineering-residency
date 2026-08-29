from pathlib import Path

from graphrag.extraction.extractor import (
    BankingKnowledgeExtractor,
)
from graphrag.extraction.graph_builder import (
    ExtractionGraphBuilder,
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


def build_store(
    database_path: Path,
) -> SQLiteGraphStore:

    document = """
    Customer Ravi Sharma owns account ACC001.
    Account ACC001 initiated transaction TXN9001.
    TXN9001 was flagged by the high value fraud rule.
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

    return store


def main() -> None:

    database_path = Path(
        "data/graphrag/"
        "banking_knowledge.db"
    )

    database_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    store = build_store(
        database_path
    )

    query_service = GraphQueryService(
        store
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

    query = (
        "What information is connected "
        "to account TXN9001?"
    )

    print("=" * 60)
    print(
        "SPRINT 4 DAY 4 — "
        "GRAPH RETRIEVAL ENGINE"
    )
    print("=" * 60)

    print(f"\nQuery:\n{query}")

    result = retriever.retrieve(
        query=query,
        max_depth=3,
        max_entities=10,
    )

    print(
        f"\nSeeds: "
        f"{len(result.seeds)}"
    )

    for seed in result.seeds:
        print(
            f"- {seed.entity_id}: "
            f"{seed.name}"
        )

    print(
        f"\nRetrieved entities: "
        f"{result.entity_count}"
    )

    for item in result.entities:
        print(
            f"- depth={item.depth} "
            f"{item.entity.entity_id}: "
            f"{item.entity.name}"
        )

    print(
        f"\nRetrieved relationships: "
        f"{result.relationship_count}"
    )

    for relationship in (
        result.relationships
    ):
        print(
            f"- "
            f"{relationship.source_id} "
            f"--["
            f"{relationship.relationship_type}"
            f"]--> "
            f"{relationship.target_id}"
        )

    context = (
        context_builder.build(result)
    )

    print("\nGraph context:\n")

    print(
        context
        if context
        else "No graph context found."
    )

    print("\n" + "=" * 60)
    print(
        "Graph Retrieval Engine ready."
    )
    print("=" * 60)


if __name__ == "__main__":
    main()