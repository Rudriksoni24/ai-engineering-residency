from __future__ import annotations

from ml.data.synthetic import (
    TARGET_COLUMN,
    generate_synthetic_transactions,
)
from ml.training.pipeline import (
    TrainingConfig,
    run_training_pipeline,
)


def main() -> None:
    config = TrainingConfig(
        random_seed=42,
        test_size=0.20,
    )

    dataframe = generate_synthetic_transactions(
        n_samples=3_000,
        random_seed=config.random_seed,
    )

    result = run_training_pipeline(
        dataframe,
        config=config,
    )

    metrics = result.metrics

    print(
        "============================================="
    )
    print(
        "Sprint 8 — Day 1: Classical ML Pipeline"
    )
    print("Artifact: ML Pipeline")
    print(
        "============================================="
    )

    print("\nDataset")
    print(f"Rows: {len(dataframe)}")
    print(
        "Fraud rows: "
        f"{int(dataframe[TARGET_COLUMN].sum())}"
    )
    print(
        "Overall fraud rate: "
        f"{dataframe[TARGET_COLUMN].mean():.4f}"
    )

    print("\nConfiguration")
    print(
        f"Random seed: {config.random_seed}"
    )
    print(
        f"Test size: {config.test_size}"
    )

    print("\nSplit")
    print(
        f"Training rows: {result.train_size}"
    )
    print(
        f"Test rows: {result.test_size}"
    )
    print(
        "Training fraud rate: "
        f"{result.training_fraud_rate:.4f}"
    )
    print(
        "Test fraud rate: "
        f"{result.test_fraud_rate:.4f}"
    )

    print("\nMetrics")
    print(
        f"Accuracy:  {metrics.accuracy:.4f}"
    )
    print(
        f"Precision: {metrics.precision:.4f}"
    )
    print(
        f"Recall:    {metrics.recall:.4f}"
    )
    print(
        f"F1:        {metrics.f1:.4f}"
    )

    print("\nConfusion matrix")
    print("[[TN, FP],")
    print(" [FN, TP]]")
    print(metrics.confusion_matrix)

    print("\nPipeline")
    print(result.model)

    print(
        "\nDay 1 pipeline completed successfully."
    )


if __name__ == "__main__":
    main()