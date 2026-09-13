from __future__ import annotations

from pathlib import Path

from ml.data.synthetic import (
    generate_synthetic_transactions,
)
from ml.tracking.tracker import (
    MLflowTracker,
    MLflowTrackingConfig,
)
from ml.training.pipeline import (
    TrainingConfig,
)
from ml.training.tracked_experiments import (
    run_tracked_experiments,
)


def main() -> None:
    mlflow_root = Path(
        "artifacts/mlflow"
    ).resolve()

    mlflow_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    database_path = (
        mlflow_root / "mlflow.db"
    )

    artifact_path = (
        mlflow_root / "artifacts"
    )

    artifact_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    tracking_config = (
        MLflowTrackingConfig(
            tracking_uri=(
                f"sqlite:///{database_path}"
            ),
            artifact_root=(
                artifact_path.as_uri()
            ),
            experiment_name=(
                "Sprint08-Fraud-Experiments"
            ),
        )
    )

    tracker = MLflowTracker(
        tracking_config
    )

    training_config = TrainingConfig(
        random_seed=42,
        test_size=0.20,
    )

    dataframe = (
        generate_synthetic_transactions(
            n_samples=5_000,
            random_seed=(
                training_config.random_seed
            ),
        )
    )

    result = run_tracked_experiments(
        dataframe,
        tracker=tracker,
        config=training_config,
    )

    print(
        "=================================================="
    )
    print(
        "Sprint 8 — Day 4: "
        "Experiment Tracking with MLflow"
    )
    print(
        "Artifact: MLflow Tracking System"
    )
    print(
        "=================================================="
    )

    print(
        "\nTracking URI:"
    )
    print(
        tracking_config.tracking_uri
    )

    print(
        "\nExperiment:"
    )
    print(
        tracking_config.experiment_name
    )

    print(
        "\nDataset fingerprint:"
    )
    print(
        result.dataset_fingerprint
    )

    print(
        "\nParent comparison run:"
    )
    print(
        result.parent_run_id
    )

    print(
        "\nTracked model runs:"
    )

    for tracked in result.runs:
        print(
            f"\nModel: {tracked.model_name}"
        )
        print(
            f"Run ID: {tracked.run_id}"
        )
        print(
            f"Model URI: "
            f"{tracked.model_uri}"
        )
        print(
            f"Artifact URI: "
            f"{tracked.artifact_uri}"
        )

    print(
        "\nBest tracked run "
        "by Average Precision:"
    )
    print(
        f"Model: "
        f"{result.best_model_name}"
    )
    print(
        f"Run ID: "
        f"{result.best_run_id}"
    )

    print(
        "\nDay 4 MLflow tracking "
        "completed successfully."
    )


if __name__ == "__main__":
    main()

    # uv run python -m ml.scripts.run_day04