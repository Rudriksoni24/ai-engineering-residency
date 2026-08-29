import os
from pathlib import Path

from graphrag.application.config import (
    BankingGraphConfig,
)
from graphrag.application.factory import (
    build_banking_graph_service,
)


BANKING_DOCUMENT = """
Customer Ravi Sharma owns account ACC001.
Account ACC001 initiated transaction TXN9001.
"""


QUESTIONS = [
    (
        "What transaction was "
        "initiated by ACC001?"
    ),
    (
        "Which account is owned "
        "by Ravi Sharma?"
    ),
    (
        "Tell me about ACC999."
    ),
]


def main() -> None:

    model = os.getenv(
        "OLLAMA_MODEL"
    )

    if not model:
        raise RuntimeError(
            "OLLAMA_MODEL is not set."
        )

    config = BankingGraphConfig(
        database_path=Path(
            "data/graphrag/"
            "banking_intelligence.db"
        ),
        model=model,
        max_depth=2,
        max_entities=10,
    )

    service = (
        build_banking_graph_service(
            config
        )
    )

    print("=" * 70)
    print(
        "SPRINT 4 DAY 7 — "
        "BANKING GRAPH "
        "INTELLIGENCE SYSTEM"
    )
    print("=" * 70)

    print("\nIngesting banking knowledge...")

    ingestion = service.ingest(
        BANKING_DOCUMENT
    )

    print(
        "Entities extracted: "
        f"{ingestion.entity_count}"
    )

    print(
        "Relationships extracted: "
        f"{ingestion.relationship_count}"
    )

    print(
        "\nPersistent graph totals:"
    )

    print(
        f"Entities: "
        f"{service.entity_count()}"
    )

    print(
        f"Relationships: "
        f"{service.relationship_count()}"
    )

    for index, question in enumerate(
        QUESTIONS,
        start=1,
    ):

        print("\n" + "-" * 70)

        print(
            f"Question {index}: "
            f"{question}"
        )

        response = service.answer(
            question
        )

        print("\nAnswer:")
        print(response.answer)

        print("\nSeeds:")

        if response.seed_entity_ids:
            for entity_id in (
                response.seed_entity_ids
            ):
                print(f"- {entity_id}")
        else:
            print("- none")

        print(
            "\nRetrieved entities: "
            f"{response.retrieved_entity_count}"
        )

        print(
            "Retrieved relationships: "
            f"{response.retrieved_relationship_count}"
        )

        if response.graph_context:

            print("\nGraph context:")
            print(
                response.graph_context
            )

    print("\n" + "=" * 70)
    print(
        "Banking Graph Intelligence "
        "System completed successfully."
    )
    print("=" * 70)


if __name__ == "__main__":
    main()