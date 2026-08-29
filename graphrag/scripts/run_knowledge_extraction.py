from graphrag.extraction.extractor import (
    BankingKnowledgeExtractor,
)
from graphrag.extraction.graph_builder import (
    ExtractionGraphBuilder,
)


def main() -> None:

    document = """
    Customer Ravi Sharma owns account ACC001.
    Account ACC001 initiated transaction TXN9001.
    """

    print("=" * 60)
    print(
        "SPRINT 4 DAY 2 — "
        "KNOWLEDGE EXTRACTION PIPELINE"
    )
    print("=" * 60)

    print("\nSource document:")
    print(document.strip())

    extractor = (
        BankingKnowledgeExtractor()
    )

    extraction = extractor.extract(
        document
    )

    print(
        f"\nExtracted entities: "
        f"{extraction.entity_count}"
    )

    for entity in (
        extraction.entities
    ):
        print(
            f"- {entity.name} "
            f"[{entity.entity_type}]"
        )

    print(
        f"\nExtracted relationships: "
        f"{extraction.relationship_count}"
    )

    for relationship in (
        extraction.relationships
    ):
        print(
            f"- "
            f"{relationship.source_name} "
            f"--["
            f"{relationship.relationship_type}"
            f"]--> "
            f"{relationship.target_name}"
        )

    builder = (
        ExtractionGraphBuilder()
    )

    graph = builder.build(
        extraction
    )

    print(
        f"\nKnowledge graph entities: "
        f"{len(graph.entities)}"
    )

    for entity in graph.entities:
        print(
            f"- {entity.entity_id}: "
            f"{entity.name}"
        )

    print(
        "\nKnowledge graph "
        "relationships:"
    )

    for relationship in (
        graph.relationships
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
        "Knowledge extraction "
        "completed successfully."
    )
    print("=" * 60)


if __name__ == "__main__":
    main()