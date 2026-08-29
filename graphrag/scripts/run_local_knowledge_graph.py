from pathlib import Path

from graphrag.extraction.extractor import (
    BankingKnowledgeExtractor,
)
from graphrag.extraction.graph_builder import (
    ExtractionGraphBuilder,
)
from graphrag.storage.query_service import (
    GraphQueryService,
)
from graphrag.storage.sqlite_store import (
    SQLiteGraphStore,
)


def main() -> None:

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

    print("=" * 60)
    print(
        "SPRINT 4 DAY 3 — "
        "LOCAL KNOWLEDGE GRAPH"
    )
    print("=" * 60)

    extractor = (
        BankingKnowledgeExtractor()
    )

    extraction = extractor.extract(
        document
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

    print(
        f"\nDatabase: "
        f"{database_path}"
    )

    print(
        f"Entities stored: "
        f"{len(store.get_entities())}"
    )

    print(
        f"Relationships stored: "
        f"{len(store.get_relationships())}"
    )

    query_service = (
        GraphQueryService(store)
    )

    print("\nCustomers:")

    for entity in (
        query_service
        .find_entities_by_type(
            "customer"
        )
    ):
        print(
            f"- {entity.entity_id}: "
            f"{entity.name}"
        )

    account_id = "account:acc001"

    print(
        f"\nNeighbors of "
        f"{account_id}:"
    )

    for entity in (
        query_service.neighbors(
            account_id
        )
    ):
        print(
            f"- {entity.entity_id}: "
            f"{entity.name}"
        )

    print(
        "\nOutgoing relationships "
        "from account:"
    )

    for relationship in (
        query_service
        .outgoing_relationships(
            account_id
        )
    ):
        print(
            f"- "
            f"{relationship.source_id} "
            f"--["
            f"{relationship.relationship_type}"
            f"]--> "
            f"{relationship.target_id}"
        )

    print("\n" + "=" * 60)
    print(
        "Local Knowledge Graph "
        "ready."
    )
    print("=" * 60)


if __name__ == "__main__":
    main()