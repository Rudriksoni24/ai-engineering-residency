from pathlib import Path

from rag.evaluation.dataset import EvaluationDataset


def main() -> None:
    dataset_path = Path(
        "rag/evaluation_data/banking_cases.json"
    )

    dataset = EvaluationDataset.from_json(
        dataset_path
    )

    print("=" * 60)
    print("SPRINT 3 DAY 7 — RAG EVALUATION DATASET")
    print("=" * 60)

    print(
        f"\nLoaded {len(dataset.cases)} evaluation cases"
    )

    for index, case in enumerate(
        dataset.cases,
        start=1,
    ):
        print("\n" + "-" * 60)
        print(f"CASE {index}")
        print(f"Query: {case.query}")
        print(
            f"Expected answer: "
            f"{case.expected_answer}"
        )

    print("\n" + "=" * 60)
    print("Evaluation dataset loaded successfully.")
    print("=" * 60)


if __name__ == "__main__":
    main()