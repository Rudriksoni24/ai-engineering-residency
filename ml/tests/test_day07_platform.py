from __future__ import annotations

from pathlib import Path

from ml.pipelines.reproducible_platform import (
    PlatformConfig,
    ReproducibleMLPlatform,
)


def build_platform(
    tmp_path: Path,
) -> ReproducibleMLPlatform:
    return ReproducibleMLPlatform(
        tracking_root=(
            tmp_path / "mlflow"
        ),
        config=PlatformConfig(
            random_seed=42,
            dataset_size=1_000,
            test_size=0.20,
            experiment_name=(
                "test-day07-platform"
            ),
            registered_model_name=(
                "TestDay07FraudModel"
            ),
        ),
    )


def test_platform_runs_end_to_end(
    tmp_path: Path,
) -> None:
    result = (
        build_platform(
            tmp_path
        ).run()
    )

    assert result.dataset_fingerprint
    assert result.selected_model
    assert result.selected_run_id
    assert result.selected_model_uri

    assert result.registered_model_name
    assert result.registered_version
    assert result.registered_model_uri


def test_data_validation_passes(
    tmp_path: Path,
) -> None:
    result = (
        build_platform(
            tmp_path
        ).run()
    )

    assert (
        result.data_validation.passed
    )


def test_model_metrics_are_recorded(
    tmp_path: Path,
) -> None:
    result = (
        build_platform(
            tmp_path
        ).run()
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
        result.metrics
    )


def test_model_parameters_are_recorded(
    tmp_path: Path,
) -> None:
    result = (
        build_platform(
            tmp_path
        ).run()
    )

    assert (
        "model_type"
        in result.parameters
    )

    assert (
        "random_seed"
        in result.parameters
    )

    assert (
        "dataset_fingerprint"
        in result.parameters
    )


def test_registered_version_exists(
    tmp_path: Path,
) -> None:
    platform = build_platform(
        tmp_path
    )

    result = platform.run()

    versions = (
        platform.registry.list_versions(
            model_name=(
                result.registered_model_name
            )
        )
    )

    assert versions

    assert any(
        version.version
        == result.registered_version
        for version in versions
    )


def test_candidate_alias_points_to_version(
    tmp_path: Path,
) -> None:
    platform = build_platform(
        tmp_path
    )

    result = platform.run()

    candidate = (
        platform.registry
        .get_version_by_alias(
            model_name=(
                result.registered_model_name
            ),
            alias="candidate",
        )
    )

    assert (
        candidate.version
        == result.registered_version
    )


def test_validated_alias_exists_on_pass(
    tmp_path: Path,
) -> None:
    platform = build_platform(
        tmp_path
    )

    result = platform.run()

    if result.model_validation.passed:
        validated = (
            platform.registry
            .get_version_by_alias(
                model_name=(
                    result
                    .registered_model_name
                ),
                alias="validated",
            )
        )

        assert (
            validated.version
            == result.registered_version
        )


def test_same_configuration_reproduces_dataset_identity(
    tmp_path: Path,
) -> None:
    first = ReproducibleMLPlatform(
        tracking_root=(
            tmp_path / "first"
        ),
        config=PlatformConfig(
            random_seed=42,
            dataset_size=1_000,
            test_size=0.20,
            experiment_name="first",
            registered_model_name=(
                "FirstModel"
            ),
        ),
    ).run()

    second = ReproducibleMLPlatform(
        tracking_root=(
            tmp_path / "second"
        ),
        config=PlatformConfig(
            random_seed=42,
            dataset_size=1_000,
            test_size=0.20,
            experiment_name="second",
            registered_model_name=(
                "SecondModel"
            ),
        ),
    ).run()

    assert (
        first.dataset_fingerprint
        == second.dataset_fingerprint
    )


def test_same_configuration_reproduces_selected_model(
    tmp_path: Path,
) -> None:
    first = ReproducibleMLPlatform(
        tracking_root=(
            tmp_path / "first"
        ),
        config=PlatformConfig(
            random_seed=42,
            dataset_size=1_000,
            experiment_name="first",
            registered_model_name=(
                "FirstModel"
            ),
        ),
    ).run()

    second = ReproducibleMLPlatform(
        tracking_root=(
            tmp_path / "second"
        ),
        config=PlatformConfig(
            random_seed=42,
            dataset_size=1_000,
            experiment_name="second",
            registered_model_name=(
                "SecondModel"
            ),
        ),
    ).run()

    assert (
        first.selected_model
        == second.selected_model
    )


def test_same_configuration_reproduces_metrics(
    tmp_path: Path,
) -> None:
    first = ReproducibleMLPlatform(
        tracking_root=(
            tmp_path / "first"
        ),
        config=PlatformConfig(
            random_seed=42,
            dataset_size=1_000,
            experiment_name="first",
            registered_model_name=(
                "FirstModel"
            ),
        ),
    ).run()

    second = ReproducibleMLPlatform(
        tracking_root=(
            tmp_path / "second"
        ),
        config=PlatformConfig(
            random_seed=42,
            dataset_size=1_000,
            experiment_name="second",
            registered_model_name=(
                "SecondModel"
            ),
        ),
    ).run()

    metric_names = {
        "accuracy",
        "precision",
        "recall",
        "f1",
        "roc_auc",
        "average_precision",
    }

    for metric in metric_names:
        assert (
            first.metrics[metric]
            == second.metrics[metric]
        )


def test_run_ids_are_not_reproducibility_targets(
    tmp_path: Path,
) -> None:
    first = ReproducibleMLPlatform(
        tracking_root=(
            tmp_path / "first"
        ),
        config=PlatformConfig(
            random_seed=42,
            dataset_size=1_000,
            experiment_name="first",
            registered_model_name=(
                "FirstModel"
            ),
        ),
    ).run()

    second = ReproducibleMLPlatform(
        tracking_root=(
            tmp_path / "second"
        ),
        config=PlatformConfig(
            random_seed=42,
            dataset_size=1_000,
            experiment_name="second",
            registered_model_name=(
                "SecondModel"
            ),
        ),
    ).run()

    assert (
        first.selected_run_id
        != second.selected_run_id
    )