from __future__ import annotations

from pathlib import Path

import mlflow.sklearn

from ml.data.synthetic import (
    FEATURE_COLUMNS,
    generate_synthetic_transactions,
)
from ml.tracking.fingerprint import (
    dataset_fingerprint,
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


def build_test_tracker(
    tmp_path: Path,
) -> MLflowTracker:
    database_path = (
        tmp_path / "mlflow.db"
    )

    artifact_path = (
        tmp_path / "artifacts"
    )

    artifact_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    return MLflowTracker(
        MLflowTrackingConfig(
            tracking_uri=(
                f"sqlite:///{database_path}"
            ),
            artifact_root=(
                artifact_path.as_uri()
            ),
            experiment_name=(
                "test-sprint08-day04"
            ),
        )
    )


def test_dataset_fingerprint_is_deterministic() -> None:
    first = (
        generate_synthetic_transactions(
            n_samples=500,
            random_seed=42,
        )
    )

    second = (
        generate_synthetic_transactions(
            n_samples=500,
            random_seed=42,
        )
    )

    assert (
        dataset_fingerprint(first)
        == dataset_fingerprint(second)
    )


def test_dataset_fingerprint_changes_with_data() -> None:
    dataframe = (
        generate_synthetic_transactions(
            n_samples=500,
            random_seed=42,
        )
    )

    modified = dataframe.copy()

    modified.loc[
        modified.index[0],
        "transaction_amount",
    ] += 1.0

    assert (
        dataset_fingerprint(dataframe)
        != dataset_fingerprint(modified)
    )


def test_tracking_creates_multiple_runs(
    tmp_path: Path,
) -> None:
    tracker = build_test_tracker(
        tmp_path
    )

    dataframe = (
        generate_synthetic_transactions(
            n_samples=800,
            random_seed=42,
        )
    )

    result = run_tracked_experiments(
        dataframe,
        tracker=tracker,
        config=TrainingConfig(
            random_seed=42,
            test_size=0.20,
        ),
        model_names=(
            "logistic_regression",
            "random_forest",
        ),
    )

    assert len(
        result.runs
    ) == 2

    assert result.parent_run_id

    assert result.best_run_id


def test_run_logs_required_parameters(
    tmp_path: Path,
) -> None:
    tracker = build_test_tracker(
        tmp_path
    )

    dataframe = (
        generate_synthetic_transactions(
            n_samples=800,
            random_seed=42,
        )
    )

    result = run_tracked_experiments(
        dataframe,
        tracker=tracker,
        config=TrainingConfig(
            random_seed=42,
            test_size=0.20,
        ),
        model_names=(
            "logistic_regression",
        ),
    )

    run = tracker.client.get_run(
        result.runs[0].run_id
    )

    assert (
        run.data.params[
            "model_type"
        ]
        == "logistic_regression"
    )

    assert (
        run.data.params[
            "random_seed"
        ]
        == "42"
    )

    assert (
        run.data.params[
            "dataset_fingerprint"
        ]
        == result.dataset_fingerprint
    )


def test_run_logs_required_metrics(
    tmp_path: Path,
) -> None:
    tracker = build_test_tracker(
        tmp_path
    )

    dataframe = (
        generate_synthetic_transactions(
            n_samples=800,
            random_seed=42,
        )
    )

    result = run_tracked_experiments(
        dataframe,
        tracker=tracker,
        model_names=(
            "logistic_regression",
        ),
    )

    run = tracker.client.get_run(
        result.runs[0].run_id
    )

    required = {
        "accuracy",
        "precision",
        "recall",
        "f1",
        "roc_auc",
        "average_precision",
    }

    assert required.issubset(
        run.data.metrics
    )


def test_run_logs_tags(
    tmp_path: Path,
) -> None:
    tracker = build_test_tracker(
        tmp_path
    )

    dataframe = (
        generate_synthetic_transactions(
            n_samples=800,
            random_seed=42,
        )
    )

    result = run_tracked_experiments(
        dataframe,
        tracker=tracker,
        model_names=(
            "logistic_regression",
        ),
    )

    run = tracker.client.get_run(
        result.runs[0].run_id
    )

    assert (
        run.data.tags["sprint"]
        == "8"
    )

    assert (
        run.data.tags["day"]
        == "4"
    )


def test_confusion_matrix_artifact_exists(
    tmp_path: Path,
) -> None:
    tracker = build_test_tracker(
        tmp_path
    )

    dataframe = (
        generate_synthetic_transactions(
            n_samples=800,
            random_seed=42,
        )
    )

    result = run_tracked_experiments(
        dataframe,
        tracker=tracker,
        model_names=(
            "logistic_regression",
        ),
    )

    artifacts = (
        tracker.client.list_artifacts(
            result.runs[0].run_id,
            path="evaluation",
        )
    )

    names = {
        artifact.path
        for artifact in artifacts
    }

    assert (
        "evaluation/confusion_matrix.json"
        in names
    )


def test_reproducibility_artifact_exists(
    tmp_path: Path,
) -> None:
    tracker = build_test_tracker(
        tmp_path
    )

    dataframe = (
        generate_synthetic_transactions(
            n_samples=800,
            random_seed=42,
        )
    )

    result = run_tracked_experiments(
        dataframe,
        tracker=tracker,
        model_names=(
            "logistic_regression",
        ),
    )

    artifacts = (
        tracker.client.list_artifacts(
            result.runs[0].run_id,
            path="metadata",
        )
    )

    names = {
        artifact.path
        for artifact in artifacts
    }

    assert (
        "metadata/reproducibility.json"
        in names
    )


def test_model_uri_is_recorded(
    tmp_path: Path,
) -> None:
    tracker = build_test_tracker(
        tmp_path
    )

    dataframe = (
        generate_synthetic_transactions(
            n_samples=800,
            random_seed=42,
        )
    )

    result = run_tracked_experiments(
        dataframe,
        tracker=tracker,
        model_names=(
            "logistic_regression",
        ),
    )

    tracked = result.runs[0]

    assert tracked.model_uri
    assert tracked.model_uri.startswith(
        "models:/"
    )

    loaded_model = mlflow.sklearn.load_model(
        tracked.model_uri
    )

    predictions = loaded_model.predict(
        dataframe[
            FEATURE_COLUMNS
        ].iloc[:5]
    )

    assert predictions.shape == (5,)


def test_parent_child_relationship_exists(
    tmp_path: Path,
) -> None:
    tracker = build_test_tracker(
        tmp_path
    )

    dataframe = (
        generate_synthetic_transactions(
            n_samples=800,
            random_seed=42,
        )
    )

    result = run_tracked_experiments(
        dataframe,
        tracker=tracker,
        model_names=(
            "logistic_regression",
            "random_forest",
        ),
    )

    children = (
        tracker.search_child_runs(
            parent_run_id=(
                result.parent_run_id
            )
        )
    )

    assert len(children) == 2


def test_same_dataset_produces_same_fingerprint(
    tmp_path: Path,
) -> None:
    first_tracker = build_test_tracker(
        tmp_path / "first"
    )

    second_tracker = build_test_tracker(
        tmp_path / "second"
    )

    dataframe = (
        generate_synthetic_transactions(
            n_samples=800,
            random_seed=42,
        )
    )

    first = run_tracked_experiments(
        dataframe,
        tracker=first_tracker,
        model_names=(
            "logistic_regression",
        ),
    )

    second = run_tracked_experiments(
        dataframe,
        tracker=second_tracker,
        model_names=(
            "logistic_regression",
        ),
    )

    assert (
        first.dataset_fingerprint
        == second.dataset_fingerprint
    )