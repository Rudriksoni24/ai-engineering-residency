from __future__ import annotations

from pathlib import Path

from sklearn.metrics import (
    average_precision_score,
)
from sklearn.model_selection import (
    train_test_split,
)

from ml.data.synthetic import (
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    generate_synthetic_transactions,
)
from ml.models.baseline import (
    build_baseline_classifier,
)
from ml.registry.lifecycle import (
    ModelRegistryService,
)
from ml.training.pipeline import (
    TrainingConfig,
)
from ml.validation.data import (
    FraudDataValidator,
)
from ml.validation.model import (
    FraudModelValidator,
)

REGISTERED_MODEL_NAME = (
    "Sprint08FraudDetectionModel"
)


def print_validation_result(
    title: str,
    result,
) -> None:
    print(f"\n{title}")
    print("-" * len(title))

    print(
        "Status:",
        "PASS" if result.passed else "FAIL",
    )

    for check in result.checks:
        marker = (
            "PASS"
            if check.passed
            else "FAIL"
        )

        print(
            f"[{marker}] "
            f"{check.name}: "
            f"{check.message}"
        )

    if result.metrics:
        print("\nMetrics:")

        for name, value in (
            result.metrics.items()
        ):
            print(
                f"  {name}: "
                f"{value:.6f}"
            )


def main() -> None:
    config = TrainingConfig(
        random_seed=42,
        test_size=0.20,
    )

    dataframe = (
        generate_synthetic_transactions(
            n_samples=5_000,
            random_seed=(
                config.random_seed
            ),
        )
    )

    data_validator = (
        FraudDataValidator()
    )

    data_result = (
        data_validator.validate(
            dataframe
        )
    )

    print(
        "=================================================="
    )
    print(
        "Sprint 8 — Day 6: "
        "Data and Model Validation"
    )
    print(
        "Artifact: Validation Suite"
    )
    print(
        "=================================================="
    )

    print_validation_result(
        "Data validation",
        data_result,
    )

    if not data_result.passed:
        print(
            "\nSTOP: dataset failed validation."
        )
        return

    X = dataframe[
        FEATURE_COLUMNS
    ]

    y = dataframe[
        TARGET_COLUMN
    ]

    (
        X_train,
        X_test,
        y_train,
        y_test,
    ) = train_test_split(
        X,
        y,
        test_size=config.test_size,
        random_state=(
            config.random_seed
        ),
        stratify=y,
    )

    baseline = (
        build_baseline_classifier(
            random_seed=(
                config.random_seed
            )
        )
    )

    baseline.fit(
        X_train,
        y_train,
    )

    baseline_probabilities = (
        baseline.predict_proba(
            X_test
        )[:, 1]
    )

    baseline_metrics = {
        "average_precision": float(
            average_precision_score(
                y_test,
                baseline_probabilities,
            )
        )
    }

    mlflow_root = Path(
        "artifacts/mlflow"
    ).resolve()

    database_path = (
        mlflow_root / "mlflow.db"
    )

    if not database_path.exists():
        raise RuntimeError(
            "MLflow registry database not found. "
            "Run Days 4 and 5 first."
        )

    tracking_uri = (
        f"sqlite:///{database_path}"
    )

    registry = ModelRegistryService(
        tracking_uri=tracking_uri
    )

    candidate_info = (
        registry.get_version_by_alias(
            model_name=(
                REGISTERED_MODEL_NAME
            ),
            alias="candidate",
        )
    )

    candidate_model = (
        registry.load_by_alias(
            model_name=(
                REGISTERED_MODEL_NAME
            ),
            alias="candidate",
        )
    )

    model_validator = (
        FraudModelValidator()
    )

    model_result = (
        model_validator.validate(
            model=candidate_model,
            X=X_test,
            y=y_test,
            baseline_metrics=(
                baseline_metrics
            ),
            threshold=0.5,
        )
    )

    print(
        "\nCandidate"
    )
    print(
        "---------"
    )
    print(
        "Registered model:",
        candidate_info.model_name,
    )
    print(
        "Version:",
        candidate_info.version,
    )
    print(
        "Alias:",
        "candidate",
    )
    print(
        "Source run:",
        candidate_info.source_run_id,
    )

    print(
        "\nBaseline"
    )
    print(
        "--------"
    )
    print(
        "Average Precision:",
        f"{baseline_metrics['average_precision']:.6f}",
    )

    print_validation_result(
        "Model validation",
        model_result,
    )

    validation_status = (
        "passed"
        if model_result.passed
        else "failed"
    )

    registry.mark_validation_status(
        model_name=(
            REGISTERED_MODEL_NAME
        ),
        version=(
            candidate_info.version
        ),
        status=validation_status,
    )

    print(
        "\nLifecycle decision"
    )
    print(
        "------------------"
    )

    print(
        "validation_status="
        f"{validation_status}"
    )

    print(
        "promotion_eligible="
        f"{model_result.passed}"
    )

    if model_result.passed:
        print(
            "\nCandidate passed Day 6 "
            "validation."
        )
    else:
        print(
            "\nCandidate failed Day 6 "
            "validation."
        )

    print(
        "\nDay 6 validation suite "
        "completed."
    )


if __name__ == "__main__":
    main()

    # uv run python -m ml.scripts.run_day06