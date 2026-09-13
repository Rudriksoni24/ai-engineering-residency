from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sklearn.model_selection import train_test_split

from ml.data.synthetic import (
    FEATURE_COLUMNS,
    TARGET_COLUMN,
)
from ml.models.fraud_models import (
    MODEL_BUILDERS,
)
from ml.tracking.fingerprint import (
    dataset_fingerprint,
)
from ml.tracking.tracker import (
    MLflowTracker,
    TrackedRun,
)
from ml.training.fraud_modeling import (
    evaluate_probabilities,
)
from ml.training.pipeline import (
    TrainingConfig,
    validate_raw_dataset,
)


@dataclass(frozen=True)
class TrackedExperimentResult:
    dataset_fingerprint: str
    parent_run_id: str
    runs: tuple[TrackedRun, ...]
    best_run_id: str
    best_model_name: str


def _classifier_parameters(
    model: object,
) -> dict[str, object]:
    classifier = model.named_steps[
        "classifier"
    ]

    raw = classifier.get_params(
        deep=False
    )

    result: dict[str, object] = {}

    for key, value in raw.items():
        if isinstance(
            value,
            (
                str,
                int,
                float,
                bool,
                type(None),
            ),
        ):
            result[
                f"classifier__{key}"
            ] = value

    return result


def run_tracked_experiments(
    dataframe: pd.DataFrame,
    *,
    tracker: MLflowTracker,
    config: TrainingConfig | None = None,
    model_names: tuple[str, ...] | None = None,
) -> TrackedExperimentResult:
    effective_config = (
        config
        if config is not None
        else TrainingConfig()
    )

    validated = validate_raw_dataset(
        dataframe
    )

    fingerprint = dataset_fingerprint(
        validated
    )

    selected_models = (
        model_names
        if model_names is not None
        else tuple(MODEL_BUILDERS)
    )

    unknown = set(
        selected_models
    ).difference(
        MODEL_BUILDERS
    )

    if unknown:
        raise ValueError(
            "Unknown model names: "
            f"{sorted(unknown)}"
        )

    X = validated[
        FEATURE_COLUMNS
    ]

    y = validated[
        TARGET_COLUMN
    ]

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

    tracked_runs: list[
        TrackedRun
    ] = []

    parent_tags = {
        "sprint": "8",
        "day": "4",
        "artifact": "MLflow Tracking System",
        "purpose": "model-comparison",
    }

    with tracker.parent_run(
        run_name=(
            "sprint08-day04-comparison"
        ),
        tags=parent_tags,
    ) as parent:
        parent_run_id = (
            parent.info.run_id
        )

        for model_name in selected_models:
            builder = (
                MODEL_BUILDERS[
                    model_name
                ]
            )

            model = builder(
                random_seed=(
                    effective_config.random_seed
                )
            )

            model.fit(
                X_train,
                y_train,
            )

            probabilities = (
                model.predict_proba(
                    X_test
                )[:, 1]
            )

            evaluation = (
                evaluate_probabilities(
                    y_true=y_test,
                    probabilities=probabilities,
                    threshold=0.5,
                )
            )

            parameters = {
                "model_type": model_name,
                "random_seed": (
                    effective_config.random_seed
                ),
                "test_size": (
                    effective_config.test_size
                ),
                "dataset_fingerprint": (
                    fingerprint
                ),
                "feature_transformer": (
                    "FraudFeatureTransformer"
                ),
                "numeric_imputer": "median",
                "numeric_scaler": (
                    "StandardScaler"
                ),
                "categorical_imputer": (
                    "most_frequent"
                ),
                "categorical_encoder": (
                    "OneHotEncoder"
                ),
                "threshold": 0.5,
                **_classifier_parameters(
                    model
                ),
            }

            metrics = {
                "accuracy": (
                    evaluation.accuracy
                ),
                "precision": (
                    evaluation.precision
                ),
                "recall": (
                    evaluation.recall
                ),
                "f1": evaluation.f1,
                "roc_auc": (
                    evaluation.roc_auc
                ),
                "average_precision": (
                    evaluation.average_precision
                ),
            }

            tags = {
                "sprint": "8",
                "day": "4",
                "artifact": (
                    "MLflow Tracking System"
                ),
                "dataset_type": (
                    "synthetic-banking-fraud"
                ),
                "model_type": model_name,
            }

            reproducibility = {
                "dataset_fingerprint": (
                    fingerprint
                ),
                "random_seed": (
                    effective_config.random_seed
                ),
                "test_size": (
                    effective_config.test_size
                ),
                "train_rows": len(
                    X_train
                ),
                "test_rows": len(
                    X_test
                ),
                "fraud_rate": float(
                    y.mean()
                ),
                "model_type": model_name,
                "threshold": 0.5,
            }

            tracked = (
                tracker.log_model_run(
                    run_name=model_name,
                    model_name=model_name,
                    model=model,
                    parameters=parameters,
                    metrics=metrics,
                    tags=tags,
                    confusion_matrix=(
                        evaluation.confusion_matrix
                    ),
                    reproducibility_metadata=(
                        reproducibility
                    ),
                    input_example=(
                        X_train.head(5)
                    ),
                )
            )

            tracked_runs.append(
                tracked
            )

        comparable_runs = (
            tracker.search_child_runs(
                parent_run_id=(
                    parent_run_id
                )
            )
        )

    if not comparable_runs:
        raise RuntimeError(
            "No tracked child runs found"
        )

    best = comparable_runs[0]

    return TrackedExperimentResult(
        dataset_fingerprint=(
            fingerprint
        ),
        parent_run_id=(
            parent_run_id
        ),
        runs=tuple(
            tracked_runs
        ),
        best_run_id=(
            best.info.run_id
        ),
        best_model_name=(
            best.data.params[
                "model_type"
            ]
        ),
    )