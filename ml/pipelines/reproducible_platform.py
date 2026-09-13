from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from sklearn.metrics import average_precision_score
from sklearn.model_selection import train_test_split

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
from ml.tracking.tracker import (
    MLflowTracker,
    MLflowTrackingConfig,
    TrackedRun,
)
from ml.training.pipeline import (
    TrainingConfig,
)
from ml.training.tracked_experiments import (
    run_tracked_experiments,
)
from ml.validation.contracts import (
    ValidationResult,
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


@dataclass(frozen=True)
class PlatformConfig:
    random_seed: int = 42
    dataset_size: int = 5_000
    test_size: float = 0.20
    experiment_name: str = (
        "Sprint08-Reproducible-Platform"
    )
    registered_model_name: str = (
        REGISTERED_MODEL_NAME
    )


@dataclass(frozen=True)
class PlatformResult:
    dataset_fingerprint: str
    random_seed: int
    selected_model: str
    selected_run_id: str
    selected_model_uri: str
    metrics: dict[str, float]
    parameters: dict[str, str]
    registered_model_name: str
    registered_version: str
    registered_model_uri: str
    validation_status: str
    promotion_eligible: bool
    data_validation: ValidationResult
    model_validation: ValidationResult


class ReproducibleMLPlatform:
    def __init__(
        self,
        *,
        tracking_root: Path,
        config: PlatformConfig | None = None,
    ) -> None:
        self.config = (
            config
            if config is not None
            else PlatformConfig()
        )

        tracking_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        database_path = (
            tracking_root / "mlflow.db"
        )

        artifact_root = (
            tracking_root / "artifacts"
        )

        artifact_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.tracking_uri = (
            f"sqlite:///{database_path}"
        )

        tracking_config = (
            MLflowTrackingConfig(
                tracking_uri=self.tracking_uri,
                artifact_root=(
                    artifact_root.as_uri()
                ),
                experiment_name=(
                    self.config.experiment_name
                ),
            )
        )

        self.tracker = MLflowTracker(
            tracking_config
        )

        self.registry = (
            ModelRegistryService(
                tracking_uri=self.tracking_uri
            )
        )

        self.data_validator = (
            FraudDataValidator()
        )

        self.model_validator = (
            FraudModelValidator()
        )

    def run(self) -> PlatformResult:
        dataframe = self._generate_data()

        data_validation = (
            self.data_validator.validate(
                dataframe
            )
        )

        if not data_validation.passed:
            raise RuntimeError(
                "Data validation failed: "
                + "; ".join(
                    failure.message
                    for failure
                    in data_validation.failures
                )
            )

        training_config = TrainingConfig(
            random_seed=(
                self.config.random_seed
            ),
            test_size=(
                self.config.test_size
            ),
        )

        tracked_result = (
            run_tracked_experiments(
                dataframe,
                tracker=self.tracker,
                config=training_config,
            )
        )

        selected_run = (
            self._find_selected_tracked_run(
                tracked_result.runs,
                tracked_result.best_run_id,
            )
        )

        run = self.tracker.client.get_run(
            selected_run.run_id
        )

        X_train, X_test, y_train, y_test = (
            self._split_data(
                dataframe
            )
        )

        baseline_metrics = (
            self._baseline_metrics(
                X_train=X_train,
                X_test=X_test,
                y_train=y_train,
                y_test=y_test,
            )
        )

        candidate_model = (
            self._load_candidate_model(
                selected_run
            )
        )

        model_validation = (
            self.model_validator.validate(
                model=candidate_model,
                X=X_test,
                y=y_test,
                baseline_metrics=(
                    baseline_metrics
                ),
                threshold=0.5,
            )
        )

        if not model_validation.passed:
            raise RuntimeError(
                "Candidate failed model validation: "
                + "; ".join(
                    failure.message
                    for failure
                    in model_validation.failures
                )
            )

        validation_status = "passed"

        registered = (
            self.registry.register_run_model(
                model_name=(
                    self.config
                    .registered_model_name
                ),
                run_id=(
                    selected_run.run_id
                ),
                model_uri=(
                    selected_run.model_uri
                ),
                description=(
                    "Sprint 8 Day 7 "
                    "integrated candidate"
                ),
            )
        )

        self.registry.assign_alias(
            model_name=(
                self.config
                .registered_model_name
            ),
            version=registered.version,
            alias="candidate",
        )

        self.registry.mark_validation_status(
            model_name=(
                self.config
                .registered_model_name
            ),
            version=registered.version,
            status=validation_status,
        )

        if model_validation.passed:
            self.registry.assign_alias(
                model_name=(
                    self.config
                    .registered_model_name
                ),
                version=registered.version,
                alias="validated",
            )

        return PlatformResult(
            dataset_fingerprint=(
                tracked_result
                .dataset_fingerprint
            ),
            random_seed=(
                self.config.random_seed
            ),
            selected_model=(
                selected_run.model_name
            ),
            selected_run_id=(
                selected_run.run_id
            ),
            selected_model_uri=(
                selected_run.model_uri
            ),
            metrics=dict(
                run.data.metrics
            ),
            parameters=dict(
                run.data.params
            ),
            registered_model_name=(
                self.config
                .registered_model_name
            ),
            registered_version=(
                registered.version
            ),
            registered_model_uri=(
                registered.version_uri
            ),
            validation_status=(
                validation_status
            ),
            promotion_eligible=(
                model_validation.passed
            ),
            data_validation=(
                data_validation
            ),
            model_validation=(
                model_validation
            ),
        )

    def _generate_data(
        self,
    ) -> pd.DataFrame:
        return generate_synthetic_transactions(
            n_samples=(
                self.config.dataset_size
            ),
            random_seed=(
                self.config.random_seed
            ),
        )

    def _split_data(
        self,
        dataframe: pd.DataFrame,
    ):
        X = dataframe[
            FEATURE_COLUMNS
        ]

        y = dataframe[
            TARGET_COLUMN
        ]

        return train_test_split(
            X,
            y,
            test_size=(
                self.config.test_size
            ),
            random_state=(
                self.config.random_seed
            ),
            stratify=y,
        )

    def _baseline_metrics(
        self,
        *,
        X_train,
        X_test,
        y_train,
        y_test,
    ) -> dict[str, float]:
        baseline = (
            build_baseline_classifier(
                random_seed=(
                    self.config
                    .random_seed
                )
            )
        )

        baseline.fit(
            X_train,
            y_train,
        )

        probabilities = (
            baseline.predict_proba(
                X_test
            )[:, 1]
        )

        return {
            "average_precision": float(
                average_precision_score(
                    y_test,
                    probabilities,
                )
            )
        }

    def _find_selected_tracked_run(
        self,
        runs: tuple[TrackedRun, ...],
        best_run_id: str,
    ) -> TrackedRun:
        for tracked in runs:
            if tracked.run_id == best_run_id:
                return tracked

        raise RuntimeError(
            "Selected MLflow run was not "
            "present in tracked run results"
        )

    def _load_candidate_model(
        self,
        tracked: TrackedRun,
    ):
        import mlflow.sklearn

        return mlflow.sklearn.load_model(
            tracked.model_uri
        )