from __future__ import annotations

from pathlib import Path

from ml.pipelines.reproducible_platform import (
    PlatformConfig,
    ReproducibleMLPlatform,
)


def main() -> None:
    config = PlatformConfig(
        random_seed=42,
        dataset_size=5_000,
        test_size=0.20,
        experiment_name=(
            "Sprint08-Reproducible-Platform"
        ),
        registered_model_name=(
            "Sprint08FraudDetectionModel"
        ),
    )

    platform = (
        ReproducibleMLPlatform(
            tracking_root=Path(
                "artifacts/mlflow"
            ).resolve(),
            config=config,
        )
    )

    result = platform.run()

    print(
        "=================================================="
    )
    print(
        "Sprint 8 — Day 7: Sprint Integration"
    )
    print(
        "Artifact: Reproducible ML Platform"
    )
    print(
        "=================================================="
    )

    print(
        "\nReproducibility"
    )
    print(
        "---------------"
    )
    print(
        f"Dataset fingerprint: "
        f"{result.dataset_fingerprint}"
    )
    print(
        f"Seed: "
        f"{result.random_seed}"
    )

    print(
        "\nSelected model"
    )
    print(
        "--------------"
    )
    print(
        f"Model: "
        f"{result.selected_model}"
    )
    print(
        f"MLflow run ID: "
        f"{result.selected_run_id}"
    )
    print(
        f"MLflow model URI: "
        f"{result.selected_model_uri}"
    )

    print(
        "\nParameters"
    )
    print(
        "----------"
    )

    for key in sorted(
        result.parameters
    ):
        print(
            f"{key}: "
            f"{result.parameters[key]}"
        )

    print(
        "\nMetrics"
    )
    print(
        "-------"
    )

    for key in sorted(
        result.metrics
    ):
        print(
            f"{key}: "
            f"{result.metrics[key]:.6f}"
        )

    print(
        "\nValidation"
    )
    print(
        "----------"
    )
    print(
        "Data validation: "
        f"{result.data_validation.passed}"
    )
    print(
        "Model validation: "
        f"{result.model_validation.passed}"
    )
    print(
        "Validation status: "
        f"{result.validation_status}"
    )
    print(
        "Promotion eligible: "
        f"{result.promotion_eligible}"
    )

    print(
        "\nRegistry"
    )
    print(
        "--------"
    )
    print(
        f"Registered model: "
        f"{result.registered_model_name}"
    )
    print(
        f"Version: "
        f"{result.registered_version}"
    )
    print(
        f"Registry URI: "
        f"{result.registered_model_uri}"
    )

    print(
        "\nSprint 8 integration completed."
    )


if __name__ == "__main__":
    main()

    # uv run python -m ml.scripts.run_day07