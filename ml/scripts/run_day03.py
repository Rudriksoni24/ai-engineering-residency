from __future__ import annotations

from ml.data.synthetic import (
    generate_synthetic_transactions,
)
from ml.training.fraud_modeling import (
    run_fraud_modeling,
)
from ml.training.pipeline import (
    TrainingConfig,
)


def main() -> None:
    config = TrainingConfig(
        random_seed=42,
        test_size=0.20,
    )

    dataframe = generate_synthetic_transactions(
        n_samples=5_000,
        random_seed=config.random_seed,
    )

    result = run_fraud_modeling(
        dataframe,
        config=config,
        minimum_recall=0.80,
    )

    print(
        "=================================================="
    )
    print(
        "Sprint 8 — Day 3: Fraud Detection Modeling"
    )
    print(
        "Artifact: Fraud Detection Model"
    )
    print(
        "=================================================="
    )

    print("\nDataset")
    print(
        f"Rows: {len(dataframe)}"
    )
    print(
        f"Fraud rate: {result.fraud_rate:.4f}"
    )
    print(
        f"Train rows: {result.train_size}"
    )
    print(
        f"Test rows: {result.test_size}"
    )

    for name, evaluation in (
        result.evaluations.items()
    ):
        metrics = evaluation.metrics

        print(
            f"\nModel: {name}"
        )
        print(
            "-" * (7 + len(name))
        )

        print(
            f"Threshold:          "
            f"{metrics.threshold:.4f}"
        )
        print(
            f"Accuracy:           "
            f"{metrics.accuracy:.4f}"
        )
        print(
            f"Precision:          "
            f"{metrics.precision:.4f}"
        )
        print(
            f"Recall:             "
            f"{metrics.recall:.4f}"
        )
        print(
            f"F1:                 "
            f"{metrics.f1:.4f}"
        )
        print(
            f"ROC-AUC:            "
            f"{metrics.roc_auc:.4f}"
        )
        print(
            f"Average precision:  "
            f"{metrics.average_precision:.4f}"
        )
        print(
            "Confusion matrix:   "
            f"{metrics.confusion_matrix}"
        )

    print(
        "\nSelected candidate"
    )
    print(
        "------------------"
    )
    print(
        f"Model: "
        f"{result.selected_model_name}"
    )
    print(
        f"Selected threshold: "
        f"{result.selected_threshold:.4f}"
    )

    print(
        "\nSelection policy:"
    )
    print(
        "1. Highest average precision"
    )
    print(
        "2. Highest recall"
    )
    print(
        "3. Highest F1"
    )

    print(
        "\nDay 3 fraud-model comparison completed."
    )


if __name__ == "__main__":
    main()

    # uv run python -m ml.scripts.run_day03