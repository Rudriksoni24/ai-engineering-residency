from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sklearn.model_selection import train_test_split

from ml.data.synthetic import (
    FEATURE_COLUMNS,
    TARGET_COLUMN,
)
from ml.models.baseline import (
    build_baseline_classifier,
)
from ml.models.engineered import (
    build_engineered_classifier,
)
from ml.training.pipeline import (
    ClassificationMetrics,
    TrainingConfig,
    evaluate_predictions,
    validate_raw_dataset,
)


@dataclass(frozen=True)
class ModelComparisonResult:
    baseline_metrics: ClassificationMetrics
    engineered_metrics: ClassificationMetrics
    train_size: int
    test_size: int


def compare_feature_pipelines(
    dataframe: pd.DataFrame,
    *,
    config: TrainingConfig | None = None,
) -> ModelComparisonResult:
    """Compare raw and engineered features on an identical split."""

    effective_config = (
        config
        if config is not None
        else TrainingConfig()
    )

    validated = validate_raw_dataset(
        dataframe
    )

    X = validated[FEATURE_COLUMNS]
    y = validated[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=effective_config.test_size,
            random_state=effective_config.random_seed,
            stratify=y,
        )
    )

    baseline = build_baseline_classifier(
        random_seed=effective_config.random_seed
    )

    engineered = build_engineered_classifier(
        random_seed=effective_config.random_seed
    )

    baseline.fit(
        X_train,
        y_train,
    )

    engineered.fit(
        X_train,
        y_train,
    )

    baseline_predictions = baseline.predict(
        X_test
    )

    engineered_predictions = (
        engineered.predict(X_test)
    )

    baseline_metrics = evaluate_predictions(
        y_true=y_test,
        y_pred=baseline_predictions,
    )

    engineered_metrics = evaluate_predictions(
        y_true=y_test,
        y_pred=engineered_predictions,
    )

    return ModelComparisonResult(
        baseline_metrics=baseline_metrics,
        engineered_metrics=engineered_metrics,
        train_size=len(X_train),
        test_size=len(X_test),
    )