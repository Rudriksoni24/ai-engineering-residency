from __future__ import annotations

from ml.data.synthetic import (
    generate_synthetic_transactions,
)
from ml.training.comparison import (
    compare_feature_pipelines,
)
from ml.training.pipeline import (
    TrainingConfig,
)


def _print_metrics(
    name: str,
    metrics: object,
) -> None:
    print(f"\n{name}")
    print("-" * len(name))

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

    print(
        "Confusion matrix:",
        metrics.confusion_matrix,
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

    result = compare_feature_pipelines(
        dataframe,
        config=config,
    )

    print(
        "============================================="
    )
    print(
        "Sprint 8 — Day 2: Feature Engineering"
    )
    print(
        "Artifact: Feature Engineering Lab"
    )
    print(
        "============================================="
    )

    print("\nDataset")
    print(f"Rows: {len(dataframe)}")
    print(
        f"Training rows: {result.train_size}"
    )
    print(
        f"Test rows: {result.test_size}"
    )

    _print_metrics(
        "Baseline raw features",
        result.baseline_metrics,
    )

    _print_metrics(
        "Engineered features",
        result.engineered_metrics,
    )

    baseline = result.baseline_metrics
    engineered = result.engineered_metrics

    print("\nMetric deltas")
    print(
        "Accuracy:  "
        f"{engineered.accuracy - baseline.accuracy:+.4f}"
    )
    print(
        "Precision: "
        f"{engineered.precision - baseline.precision:+.4f}"
    )
    print(
        "Recall:    "
        f"{engineered.recall - baseline.recall:+.4f}"
    )
    print(
        "F1:        "
        f"{engineered.f1 - baseline.f1:+.4f}"
    )

    print(
        "\nInterpretation rule:"
    )
    print(
        "Do not claim feature engineering improved the model "
        "unless the observed metrics support that claim."
    )


if __name__ == "__main__":
    main()

    #uv run python -m ml.scripts.run_day02