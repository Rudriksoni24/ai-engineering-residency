from graphrag.modeling.entity import Entity
from graphrag.modeling.graph import (
    KnowledgeGraph,
)
from graphrag.modeling.relationship import (
    Relationship,
)


def build_banking_graph() -> KnowledgeGraph:
    graph = KnowledgeGraph()

    entities = [
        Entity(
            entity_id="customer:001",
            entity_type="customer",
            name="Ravi Sharma",
            properties={
                "segment": "premium",
            },
        ),
        Entity(
            entity_id="account:001",
            entity_type="account",
            name="Savings Account",
            properties={
                "currency": "INR",
            },
        ),
        Entity(
            entity_id="transaction:001",
            entity_type="transaction",
            name="UPI Transaction",
            properties={
                "amount": 25000,
                "currency": "INR",
            },
        ),
        Entity(
            entity_id="payment_system:upi",
            entity_type="payment_system",
            name="UPI",
        ),
        Entity(
            entity_id="fraud_rule:high_value",
            entity_type="fraud_rule",
            name="High Value Transaction Rule",
        ),
    ]

    for entity in entities:
        graph.add_entity(entity)

    relationships = [
        Relationship(
            relationship_id="rel:001",
            source_id="customer:001",
            target_id="account:001",
            relationship_type="owns",
        ),
        Relationship(
            relationship_id="rel:002",
            source_id="account:001",
            target_id="transaction:001",
            relationship_type="initiated",
        ),
        Relationship(
            relationship_id="rel:003",
            source_id="transaction:001",
            target_id="payment_system:upi",
            relationship_type="processed_by",
        ),
        Relationship(
            relationship_id="rel:004",
            source_id="transaction:001",
            target_id="fraud_rule:high_value",
            relationship_type="flagged_by",
        ),
    ]

    for relationship in relationships:
        graph.add_relationship(
            relationship
        )

    return graph


def main() -> None:
    graph = build_banking_graph()

    print("=" * 60)
    print(
        "SPRINT 4 DAY 1 — "
        "BANKING KNOWLEDGE GRAPH"
    )
    print("=" * 60)

    print(
        f"\nEntities: "
        f"{len(graph.entities)}"
    )

    for entity in graph.entities:
        print(
            f"- {entity.entity_id}: "
            f"{entity.name} "
            f"[{entity.entity_type}]"
        )

    print(
        f"\nRelationships: "
        f"{len(graph.relationships)}"
    )

    for relationship in (
        graph.relationships
    ):
        print(
            f"- "
            f"{relationship.source_id} "
            f"--[{relationship.relationship_type}]--> "
            f"{relationship.target_id}"
        )

    print(
        "\nNeighbors of transaction:001:"
    )

    for entity in graph.neighbors(
        "transaction:001"
    ):
        print(
            f"- {entity.name} "
            f"[{entity.entity_type}]"
        )


if __name__ == "__main__":
    main()