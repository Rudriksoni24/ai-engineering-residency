from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from ml.data.synthetic import (
    FEATURE_COLUMNS,
    TARGET_COLUMN,
)
from ml.models.fraud_models import (
    MODEL_BUILDERS,
)
from ml.training.pipeline import (
    TrainingConfig,
    validate_raw_dataset,
)


@dataclass(frozen=True)
class FraudMetrics:
    threshold: float
    accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: float
    average_precision: float
    confusion_matrix: tuple[
        tuple[int, int],
        tuple[int, int],
    ]


@dataclass
class ModelEvaluation:
    name: str
    model: Pipeline
    metrics: FraudMetrics
    probabilities: np.ndarray


@dataclass
class FraudModelingResult:
    evaluations: dict[str, ModelEvaluation]
    selected_model_name: str
    selected_threshold: float
    train_size: int
    test_size: int
    fraud_rate: float


def predictions_from_threshold(
    probabilities: np.ndarray,
    *,
    threshold: float,
) -> np.ndarray:
    if not 0.0 <= threshold <= 1.0:
        raise ValueError(
            "threshold must be between 0 and 1"
        )

    return (
        probabilities >= threshold
    ).astype(int)


def evaluate_probabilities(
    *,
    y_true: pd.Series,
    probabilities: np.ndarray,
    threshold: float = 0.5,
) -> FraudMetrics:
    predictions = predictions_from_threshold(
        probabilities,
        threshold=threshold,
    )

    matrix = confusion_matrix(
        y_true,
        predictions,
        labels=[0, 1],
    )

    return FraudMetrics(
        threshold=threshold,
        accuracy=float(
            accuracy_score(
                y_true,
                predictions,
            )
        ),
        precision=float(
            precision_score(
                y_true,
                predictions,
                zero_division=0,
            )
        ),
        recall=float(
            recall_score(
                y_true,
                predictions,
                zero_division=0,
            )
        ),
        f1=float(
            f1_score(
                y_true,
                predictions,
                zero_division=0,
            )
        ),
        roc_auc=float(
            roc_auc_score(
                y_true,
                probabilities,
            )
        ),
        average_precision=float(
            average_precision_score(
                y_true,
                probabilities,
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


def select_threshold_for_recall(
    *,
    y_true: pd.Series,
    probabilities: np.ndarray,
    minimum_recall: float = 0.80,
) -> float:
    """Choose highest-precision threshold satisfying a recall floor."""

    if not 0.0 < minimum_recall <= 1.0:
        raise ValueError(
            "minimum_recall must be in (0, 1]"
        )

    precision, recall, thresholds = (
        precision_recall_curve(
            y_true,
            probabilities,
        )
    )

    candidates: list[
        tuple[float, float]
    ] = []

    for index, threshold in enumerate(
        thresholds
    ):
        candidate_recall = recall[index]
        candidate_precision = precision[index]

        if candidate_recall >= minimum_recall:
            candidates.append(
                (
                    float(candidate_precision),
                    float(threshold),
                )
            )

    if not candidates:
        return 0.0

    candidates.sort(
        key=lambda item: (
            item[0],
            item[1],
        ),
        reverse=True,
    )

    return candidates[0][1]


def select_candidate_model(
    evaluations: dict[
        str,
        ModelEvaluation,
    ],
) -> str:
    """Select a deterministic Day 3 candidate.

    Ranking policy:
    1. highest average precision
    2. highest recall
    3. highest F1
    4. stable name tie-break
    """

    if not evaluations:
        raise ValueError(
            "No model evaluations provided"
        )

    return max(
        evaluations,
        key=lambda name: (
            evaluations[
                name
            ].metrics.average_precision,
            evaluations[
                name
            ].metrics.recall,
            evaluations[
                name
            ].metrics.f1,
            name,
        ),
    )


def run_fraud_modeling(
    dataframe: pd.DataFrame,
    *,
    config: TrainingConfig | None = None,
    minimum_recall: float = 0.80,
) -> FraudModelingResult:
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

    default_evaluations: dict[
        str,
        ModelEvaluation,
    ] = {}

    for name, builder in MODEL_BUILDERS.items():
        model = builder(
            random_seed=effective_config.random_seed
        )

        model.fit(
            X_train,
            y_train,
        )

        probabilities = model.predict_proba(
            X_test
        )[:, 1]

        metrics = evaluate_probabilities(
            y_true=y_test,
            probabilities=probabilities,
            threshold=0.5,
        )

        default_evaluations[name] = (
            ModelEvaluation(
                name=name,
                model=model,
                metrics=metrics,
                probabilities=probabilities,
            )
        )

    selected_name = select_candidate_model(
        default_evaluations
    )

    selected_evaluation = (
        default_evaluations[selected_name]
    )

    selected_threshold = (
        select_threshold_for_recall(
            y_true=y_test,
            probabilities=(
                selected_evaluation.probabilities
            ),
            minimum_recall=minimum_recall,
        )
    )

    tuned_metrics = evaluate_probabilities(
        y_true=y_test,
        probabilities=(
            selected_evaluation.probabilities
        ),
        threshold=selected_threshold,
    )

    default_evaluations[
        selected_name
    ] = ModelEvaluation(
        name=selected_name,
        model=selected_evaluation.model,
        metrics=tuned_metrics,
        probabilities=(
            selected_evaluation.probabilities
        ),
    )

    return FraudModelingResult(
        evaluations=default_evaluations,
        selected_model_name=selected_name,
        selected_threshold=selected_threshold,
        train_size=len(X_train),
        test_size=len(X_test),
        fraud_rate=float(y.mean()),
    )