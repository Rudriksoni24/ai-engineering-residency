import os

from graphrag.comparison.adapters import (
    GraphRAGAdapter,
    VectorRAGAdapter,
)
from graphrag.comparison.cases import (
    BANKING_COMPARISON_CASES,
)
from graphrag.comparison.comparator import (
    RetrievalComparator,
)
from graphrag.scripts.run_graphrag import (
    build_pipeline as build_graph_pipeline,
)
from rag.scripts.run_rag import (
    build_pipeline as build_vector_pipeline,
)


def print_evaluation(
    name,
    evaluation,
) -> None:

    output = evaluation.output

    print(
        f"  Answer: {output.answer}"
    )

    print(
        "  Retrieval success: "
        f"{evaluation.retrieval_success}"
    )

    print(
        "  Keyword coverage: "
        f"{evaluation.keyword_coverage:.2f}"
    )

    print(
        "  Evidence count: "
        f"{output.retrieved_evidence_count}"
    )

    print(
        "  Relationships: "
        f"{output.relationship_count}"
    )

    print(
        "  Latency: "
        f"{output.latency_ms:.2f} ms"
    )


def main() -> None:

    model = os.getenv(
        "OLLAMA_MODEL"
    )

    if not model:
        raise RuntimeError(
            "OLLAMA_MODEL is not set."
        )

    vector_pipeline = (
        build_vector_pipeline()
    )

    graph_pipeline = (
        build_graph_pipeline(
            model=model
        )
    )

    comparator = (
        RetrievalComparator(
            vector_system=(
                VectorRAGAdapter(
                    vector_pipeline
                )
            ),
            graph_system=(
                GraphRAGAdapter(
                    graph_pipeline,
                    max_depth=2,
                    max_entities=10,
                )
            ),
        )
    )

    print("=" * 70)
    print(
        "SPRINT 4 DAY 6 — "
        "VECTOR RAG VS GRAPHRAG"
    )
    print("=" * 70)

    results = (
        comparator.compare_many(
            BANKING_COMPARISON_CASES
        )
    )

    for result in results:

        print(
            f"\nCASE: "
            f"{result.case.case_id}"
        )

        print(
            f"Type: "
            f"{result.case.query_type}"
        )

        print(
            f"Question: "
            f"{result.case.query}"
        )

        print(
            f"Expected: "
            f"{result.case.expected_answer}"
        )

        print("\nVector RAG:")

        print_evaluation(
            "Vector RAG",
            result.vector,
        )

        print("\nGraphRAG:")

        print_evaluation(
            "GraphRAG",
            result.graph,
        )

        print("-" * 70)


if __name__ == "__main__":
    main()