from __future__ import annotations

from pathlib import Path

from ml.registry.lifecycle import (
    ModelRegistryService,
)
from ml.tracking.tracker import (
    MLflowTracker,
    MLflowTrackingConfig,
)

REGISTERED_MODEL_NAME = (
    "Sprint08FraudDetectionModel"
)


def main() -> None:
    mlflow_root = Path(
        "artifacts/mlflow"
    ).resolve()

    database_path = (
        mlflow_root / "mlflow.db"
    )

    artifact_path = (
        mlflow_root / "artifacts"
    )

    if not database_path.exists():
        raise RuntimeError(
            "Day 4 MLflow database was not found. "
            "Run Day 4 first:\n"
            "uv run python -m "
            "ml.scripts.run_day04"
        )

    tracking_uri = (
        f"sqlite:///{database_path}"
    )

    tracking_config = (
        MLflowTrackingConfig(
            tracking_uri=tracking_uri,
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

    best_run = tracker.best_run(
        metric_name="average_precision"
    )

    best_run_id = (
        best_run.info.run_id
    )

    model_type = (
        best_run.data.params[
            "model_type"
        ]
    )

    average_precision = (
        best_run.data.metrics[
            "average_precision"
        ]
    )

    registry = ModelRegistryService(
        tracking_uri=tracking_uri
    )

    registered = (
        registry.register_run_model(
            model_name=(
                REGISTERED_MODEL_NAME
            ),
            run_id=best_run_id,
            artifact_path="model",
            description=(
                "Sprint 8 Day 5 candidate "
                "selected from Day 4 "
                "tracked experiments"
            ),
        )
    )

    candidate = registry.assign_alias(
        model_name=(
            REGISTERED_MODEL_NAME
        ),
        version=registered.version,
        alias="candidate",
    )

    registry.mark_validation_status(
        model_name=(
            REGISTERED_MODEL_NAME
        ),
        version=registered.version,
        status="pending",
    )

    lineage = registry.inspect_lineage(
        model_name=(
            REGISTERED_MODEL_NAME
        ),
        version=registered.version,
    )

    candidate_model = (
        registry.load_by_alias(
            model_name=(
                REGISTERED_MODEL_NAME
            ),
            alias="candidate",
        )
    )

    versions = registry.list_versions(
        model_name=(
            REGISTERED_MODEL_NAME
        )
    )

    print(
        "=================================================="
    )
    print(
        "Sprint 8 — Day 5: Model Registry"
    )
    print(
        "Artifact: Model Lifecycle Pipeline"
    )
    print(
        "=================================================="
    )

    print(
        "\nSelected Day 4 run"
    )
    print(
        "------------------"
    )
    print(
        f"Run ID: {best_run_id}"
    )
    print(
        f"Model type: {model_type}"
    )
    print(
        "Average Precision: "
        f"{average_precision:.4f}"
    )

    print(
        "\nRegistered model"
    )
    print(
        "----------------"
    )
    print(
        f"Name: "
        f"{candidate.model_name}"
    )
    print(
        f"Version: "
        f"{candidate.version}"
    )
    print(
        f"Version URI: "
        f"{candidate.version_uri}"
    )
    print(
        f"Alias URI: "
        f"{candidate.alias_uri}"
    )
    print(
        f"Aliases: "
        f"{candidate.aliases}"
    )

    print(
        "\nLineage"
    )
    print(
        "-------"
    )

    for key, value in lineage.items():
        print(
            f"{key}: {value}"
        )

    print(
        "\nRegistered versions"
    )
    print(
        "-------------------"
    )

    for version in versions:
        print(
            f"Version "
            f"{version.version}: "
            f"run={version.source_run_id} "
            f"aliases={version.aliases}"
        )

    print(
        "\nRegistry load check"
    )
    print(
        "-------------------"
    )
    print(
        "Loaded candidate object: "
        f"{type(candidate_model).__name__}"
    )

    print(
        "\nLifecycle status"
    )
    print(
        "----------------"
    )
    print(
        "candidate alias assigned"
    )
    print(
        "validation_status=pending"
    )

    print(
        "\nDay 5 model lifecycle "
        "completed successfully."
    )


if __name__ == "__main__":
    main()

#rm -rf artifacts/mlflow
# uv run python -m ml.scripts.run_day04
# uv run python -m ml.scripts.run_day05