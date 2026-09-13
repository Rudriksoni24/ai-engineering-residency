from __future__ import annotations

from pathlib import Path

import numpy as np

from ml.data.synthetic import (
    FEATURE_COLUMNS,
    generate_synthetic_transactions,
)
from ml.registry.lifecycle import (
    ModelRegistryService,
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

MODEL_NAME = "TestFraudDetectionModel"


def build_tracking_stack(
    tmp_path: Path,
) -> tuple[
    MLflowTracker,
    ModelRegistryService,
]:
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

    tracking_uri = (
        f"sqlite:///{database_path}"
    )

    tracker = MLflowTracker(
        MLflowTrackingConfig(
            tracking_uri=tracking_uri,
            artifact_root=(
                artifact_path.as_uri()
            ),
            experiment_name=(
                "test-day05-registry"
            ),
        )
    )

    registry = ModelRegistryService(
        tracking_uri=tracking_uri
    )

    return tracker, registry


def create_tracked_model(
    tmp_path: Path,
):
    tracker, registry = (
        build_tracking_stack(
            tmp_path
        )
    )

    dataframe = (
        generate_synthetic_transactions(
            n_samples=800,
            random_seed=42,
        )
    )

    tracked = (
        run_tracked_experiments(
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
    )

    return (
        dataframe,
        tracker,
        registry,
        tracked.runs[0],
    )


def test_registered_model_is_created(
    tmp_path: Path,
) -> None:
    (
        _,
        _,
        registry,
        tracked,
    ) = create_tracked_model(
        tmp_path
    )

    info = registry.register_run_model(
        model_name=MODEL_NAME,
        run_id=tracked.run_id,
    )

    registered = (
        registry.client.get_registered_model(
            MODEL_NAME
        )
    )

    assert registered.name == MODEL_NAME
    assert info.version == "1"


def test_registration_preserves_source_run(
    tmp_path: Path,
) -> None:
    (
        _,
        _,
        registry,
        tracked,
    ) = create_tracked_model(
        tmp_path
    )

    info = registry.register_run_model(
        model_name=MODEL_NAME,
        run_id=tracked.run_id,
    )

    assert (
        info.source_run_id
        == tracked.run_id
    )


def test_registering_again_creates_new_version(
    tmp_path: Path,
) -> None:
    (
        _,
        _,
        registry,
        tracked,
    ) = create_tracked_model(
        tmp_path
    )

    first = registry.register_run_model(
        model_name=MODEL_NAME,
        run_id=tracked.run_id,
    )

    second = registry.register_run_model(
        model_name=MODEL_NAME,
        run_id=tracked.run_id,
    )

    assert first.version == "1"
    assert second.version == "2"


def test_versions_can_be_listed(
    tmp_path: Path,
) -> None:
    (
        _,
        _,
        registry,
        tracked,
    ) = create_tracked_model(
        tmp_path
    )

    registry.register_run_model(
        model_name=MODEL_NAME,
        run_id=tracked.run_id,
    )

    registry.register_run_model(
        model_name=MODEL_NAME,
        run_id=tracked.run_id,
    )

    versions = registry.list_versions(
        model_name=MODEL_NAME
    )

    assert [
        version.version
        for version in versions
    ] == [
        "1",
        "2",
    ]


def test_candidate_alias_can_be_assigned(
    tmp_path: Path,
) -> None:
    (
        _,
        _,
        registry,
        tracked,
    ) = create_tracked_model(
        tmp_path
    )

    registered = (
        registry.register_run_model(
            model_name=MODEL_NAME,
            run_id=tracked.run_id,
        )
    )

    aliased = registry.assign_alias(
        model_name=MODEL_NAME,
        version=registered.version,
        alias="candidate",
    )

    assert (
        "candidate"
        in aliased.aliases
    )


def test_candidate_alias_resolves_version(
    tmp_path: Path,
) -> None:
    (
        _,
        _,
        registry,
        tracked,
    ) = create_tracked_model(
        tmp_path
    )

    registered = (
        registry.register_run_model(
            model_name=MODEL_NAME,
            run_id=tracked.run_id,
        )
    )

    registry.assign_alias(
        model_name=MODEL_NAME,
        version=registered.version,
        alias="candidate",
    )

    resolved = (
        registry.get_version_by_alias(
            model_name=MODEL_NAME,
            alias="candidate",
        )
    )

    assert (
        resolved.version
        == registered.version
    )


def test_alias_can_move_between_versions(
    tmp_path: Path,
) -> None:
    (
        _,
        _,
        registry,
        tracked,
    ) = create_tracked_model(
        tmp_path
    )

    first = registry.register_run_model(
        model_name=MODEL_NAME,
        run_id=tracked.run_id,
    )

    second = registry.register_run_model(
        model_name=MODEL_NAME,
        run_id=tracked.run_id,
    )

    registry.assign_alias(
        model_name=MODEL_NAME,
        version=first.version,
        alias="candidate",
    )

    registry.assign_alias(
        model_name=MODEL_NAME,
        version=second.version,
        alias="candidate",
    )

    resolved = (
        registry.get_version_by_alias(
            model_name=MODEL_NAME,
            alias="candidate",
        )
    )

    assert (
        resolved.version
        == second.version
    )


def test_model_can_load_by_version(
    tmp_path: Path,
) -> None:
    (
        dataframe,
        _,
        registry,
        tracked,
    ) = create_tracked_model(
        tmp_path
    )

    registered = (
        registry.register_run_model(
            model_name=MODEL_NAME,
            run_id=tracked.run_id,
        )
    )

    model = registry.load_by_version(
        model_name=MODEL_NAME,
        version=registered.version,
    )

    X = dataframe[
        FEATURE_COLUMNS
    ].iloc[:5]

    predictions = model.predict(X)

    assert predictions.shape == (5,)

    assert set(
        np.unique(predictions)
    ).issubset({0, 1})


def test_model_can_load_by_alias(
    tmp_path: Path,
) -> None:
    (
        dataframe,
        _,
        registry,
        tracked,
    ) = create_tracked_model(
        tmp_path
    )

    registered = (
        registry.register_run_model(
            model_name=MODEL_NAME,
            run_id=tracked.run_id,
        )
    )

    registry.assign_alias(
        model_name=MODEL_NAME,
        version=registered.version,
        alias="candidate",
    )

    model = registry.load_by_alias(
        model_name=MODEL_NAME,
        alias="candidate",
    )

    predictions = model.predict(
        dataframe[
            FEATURE_COLUMNS
        ].iloc[:5]
    )

    assert predictions.shape == (5,)


def test_lineage_contains_source_metadata(
    tmp_path: Path,
) -> None:
    (
        _,
        tracker,
        registry,
        tracked,
    ) = create_tracked_model(
        tmp_path
    )

    registered = (
        registry.register_run_model(
            model_name=MODEL_NAME,
            run_id=tracked.run_id,
        )
    )

    lineage = registry.inspect_lineage(
        model_name=MODEL_NAME,
        version=registered.version,
    )

    run = tracker.client.get_run(
        tracked.run_id
    )

    assert (
        lineage["source_run_id"]
        == tracked.run_id
    )

    assert (
        lineage[
            "dataset_fingerprint"
        ]
        == run.data.params[
            "dataset_fingerprint"
        ]
    )

    assert (
        lineage["model_type"]
        == "logistic_regression"
    )


def test_validation_status_tag_is_stored(
    tmp_path: Path,
) -> None:
    (
        _,
        _,
        registry,
        tracked,
    ) = create_tracked_model(
        tmp_path
    )

    registered = (
        registry.register_run_model(
            model_name=MODEL_NAME,
            run_id=tracked.run_id,
        )
    )

    registry.mark_validation_status(
        model_name=MODEL_NAME,
        version=registered.version,
        status="pending",
    )

    version = (
        registry.client.get_model_version(
            name=MODEL_NAME,
            version=registered.version,
        )
    )

    assert (
        version.tags[
            "validation_status"
        ]
        == "pending"
    )