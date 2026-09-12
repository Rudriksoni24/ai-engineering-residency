from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from ml.data.synthetic import (
    FEATURE_COLUMNS,
    TARGET_COLUMN,
)
from ml.models.baseline import build_baseline_classifier


@dataclass(frozen=True)
class TrainingConfig:
    """Inspectable configuration for a deterministic training run."""

    random_seed: int = 42
    test_size: float = 0.20


@dataclass(frozen=True)
class ClassificationMetrics:
    accuracy: float
    precision: float
    recall: float
    f1: float
    confusion_matrix: tuple[
        tuple[int, int],
        tuple[int, int],
    ]


@dataclass
class TrainingResult:
    model: Pipeline
    metrics: ClassificationMetrics
    predictions: np.ndarray
    y_test: pd.Series
    train_size: int
    test_size: int
    training_fraud_rate: float
    test_fraud_rate: float


def validate_raw_dataset(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Perform basic Day 1 dataset validation."""

    if dataframe.empty:
        raise ValueError("Dataset cannot be empty")

    required_columns = set(
        FEATURE_COLUMNS + [TARGET_COLUMN]
    )

    missing_columns = required_columns.difference(
        dataframe.columns
    )

    if missing_columns:
        raise ValueError(
            "Dataset is missing required columns: "
            f"{sorted(missing_columns)}"
        )

    labels = set(
        dataframe[TARGET_COLUMN]
        .dropna()
        .unique()
        .tolist()
    )

    if not labels:
        raise ValueError(
            "Target column contains no labels"
        )

    if not labels.issubset({0, 1}):
        raise ValueError(
            "fraud_label must contain only 0 or 1"
        )

    if dataframe[TARGET_COLUMN].isna().any():
        raise ValueError(
            "fraud_label cannot contain missing values"
        )

    if len(labels) < 2:
        raise ValueError(
            "Dataset must contain both target classes"
        )

    return dataframe.copy()


def evaluate_predictions(
    *,
    y_true: pd.Series,
    y_pred: np.ndarray,
) -> ClassificationMetrics:
    """Calculate baseline classification metrics."""

    matrix = confusion_matrix(
        y_true,
        y_pred,
        labels=[0, 1],
    )

    return ClassificationMetrics(
        accuracy=float(
            accuracy_score(y_true, y_pred)
        ),
        precision=float(
            precision_score(
                y_true,
                y_pred,
                zero_division=0,
            )
        ),
        recall=float(
            recall_score(
                y_true,
                y_pred,
                zero_division=0,
            )
        ),
        f1=float(
            f1_score(
                y_true,
                y_pred,
                zero_division=0,
            )
        ),
        confusion_matrix=(
            (
                int(matrix[0, 0]),
                int(matrix[0, 1]),
            ),
            (
                int(matrix[1, 0]),
                int(matrix[1, 1]),
            ),
        ),
    )


def run_training_pipeline(
    dataframe: pd.DataFrame,
    *,
    config: TrainingConfig | None = None,
) -> TrainingResult:
    """Run the complete Sprint 8 Day 1 ML pipeline."""

    effective_config = (
        config
        if config is not None
        else TrainingConfig()
    )

    validated = validate_raw_dataset(dataframe)

    X = validated[FEATURE_COLUMNS]
    y = validated[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=effective_config.test_size,
            random_state=(
                effective_config.random_seed
            ),
            stratify=y,
        )
    )

    model = build_baseline_classifier(
        random_seed=effective_config.random_seed
    )

    # Critical leakage boundary:
    # preprocessing and estimator are fitted only
    # after the train/test split.
    model.fit(
        X_train,
        y_train,
    )

    predictions = model.predict(X_test)

    metrics = evaluate_predictions(
        y_true=y_test,
        y_pred=predictions,
    )

    return TrainingResult(
        model=model,
        metrics=metrics,
        predictions=predictions,
        y_test=y_test,
        train_size=len(X_train),
        test_size=len(X_test),
        training_fraud_rate=float(
            y_train.mean()
        ),
        test_fraud_rate=float(
            y_test.mean()
        ),
    )