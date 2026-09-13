from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from ml.validation.contracts import (
    ValidationCheck,
    ValidationResult,
)


@dataclass(frozen=True)
class ModelValidationPolicy:
    min_accuracy: float = 0.50
    min_precision: float = 0.08
    min_recall: float = 0.25
    min_f1: float = 0.12
    min_roc_auc: float = 0.60
    min_average_precision: float = 0.12

    # Candidate may be slightly lower because sampling
    # variation is normal, but large regressions fail.
    max_average_precision_regression: float = 0.02


class FraudModelValidator:
    def __init__(
        self,
        policy: ModelValidationPolicy | None = None,
    ) -> None:
        self.policy = (
            policy
            if policy is not None
            else ModelValidationPolicy()
        )

    def validate(
        self,
        *,
        model: object,
        X: pd.DataFrame,
        y: pd.Series,
        baseline_metrics: (
            dict[str, float] | None
        ) = None,
        threshold: float = 0.5,
    ) -> ValidationResult:
        checks: list[
            ValidationCheck
        ] = []

        probabilities = (
            self._predict_probabilities(
                model=model,
                X=X,
                checks=checks,
            )
        )

        if probabilities is None:
            return (
                ValidationResult
                .from_checks(checks)
            )

        predictions = (
            probabilities
            >= threshold
        ).astype(int)

        self._validate_prediction_shape(
            predictions=predictions,
            expected_rows=len(X),
            checks=checks,
        )

        self._validate_prediction_domain(
            predictions=predictions,
            checks=checks,
        )

        metrics = self._calculate_metrics(
            y=y,
            predictions=predictions,
            probabilities=probabilities,
        )

        self._validate_finite_metrics(
            metrics=metrics,
            checks=checks,
        )

        self._validate_thresholds(
            metrics=metrics,
            checks=checks,
        )

        if baseline_metrics is not None:
            self._validate_against_baseline(
                candidate_metrics=metrics,
                baseline_metrics=(
                    baseline_metrics
                ),
                checks=checks,
            )

        return ValidationResult.from_checks(
            checks,
            metrics=metrics,
        )

    def _predict_probabilities(
        self,
        *,
        model: object,
        X: pd.DataFrame,
        checks: list[ValidationCheck],
    ) -> np.ndarray | None:
        if not hasattr(
            model,
            "predict",
        ):
            checks.append(
                ValidationCheck(
                    name="model_can_predict",
                    passed=False,
                    message=(
                        "Model has no predict method"
                    ),
                    observed=None,
                    expected="predict()",
                )
            )

            return None

        if not hasattr(
            model,
            "predict_proba",
        ):
            checks.append(
                ValidationCheck(
                    name=(
                        "model_has_probabilities"
                    ),
                    passed=False,
                    message=(
                        "Model has no "
                        "predict_proba method"
                    ),
                    observed=None,
                    expected="predict_proba()",
                )
            )

            return None

        try:
            probabilities = (
                model.predict_proba(
                    X
                )[:, 1]
            )
        except Exception as exc:
            checks.append(
                ValidationCheck(
                    name="model_can_predict",
                    passed=False,
                    message=(
                        "Model prediction failed: "
                        f"{exc}"
                    ),
                    observed=(
                        type(exc).__name__
                    ),
                    expected=(
                        "successful prediction"
                    ),
                )
            )

            return None

        checks.append(
            ValidationCheck(
                name="model_can_predict",
                passed=True,
                message=(
                    "Model generated predictions"
                ),
                observed=len(
                    probabilities
                ),
                expected=len(X),
            )
        )

        return np.asarray(
            probabilities,
            dtype=float,
        )

    def _validate_prediction_shape(
        self,
        *,
        predictions: np.ndarray,
        expected_rows: int,
        checks: list[ValidationCheck],
    ) -> None:
        checks.append(
            ValidationCheck(
                name="prediction_shape",
                passed=(
                    predictions.shape
                    == (expected_rows,)
                ),
                message=(
                    "Prediction shape is valid"
                    if predictions.shape
                    == (expected_rows,)
                    else (
                        "Prediction shape is "
                        "invalid"
                    )
                ),
                observed=(
                    predictions.shape
                ),
                expected=(
                    expected_rows,
                ),
            )
        )

    def _validate_prediction_domain(
        self,
        *,
        predictions: np.ndarray,
        checks: list[ValidationCheck],
    ) -> None:
        values = set(
            np.unique(
                predictions
            ).tolist()
        )

        valid = values.issubset(
            {0, 1}
        )

        checks.append(
            ValidationCheck(
                name="prediction_domain",
                passed=valid,
                message=(
                    "Predictions are binary"
                    if valid
                    else (
                        "Predictions contain "
                        "invalid classes"
                    )
                ),
                observed=sorted(values),
                expected=[0, 1],
            )
        )

    def _calculate_metrics(
        self,
        *,
        y: pd.Series,
        predictions: np.ndarray,
        probabilities: np.ndarray,
    ) -> dict[str, float]:
        return {
            "accuracy": float(
                accuracy_score(
                    y,
                    predictions,
                )
            ),
            "precision": float(
                precision_score(
                    y,
                    predictions,
                    zero_division=0,
                )
            ),
            "recall": float(
                recall_score(
                    y,
                    predictions,
                    zero_division=0,
                )
            ),
            "f1": float(
                f1_score(
                    y,
                    predictions,
                    zero_division=0,
                )
            ),
            "roc_auc": float(
                roc_auc_score(
                    y,
                    probabilities,
                )
            ),
            "average_precision": float(
                average_precision_score(
                    y,
                    probabilities,
                )
            ),
        }

    def _validate_finite_metrics(
        self,
        *,
        metrics: dict[str, float],
        checks: list[ValidationCheck],
    ) -> None:
        finite = all(
            np.isfinite(value)
            for value in metrics.values()
        )

        checks.append(
            ValidationCheck(
                name="metrics_are_finite",
                passed=finite,
                message=(
                    "All model metrics are finite"
                    if finite
                    else (
                        "One or more metrics are "
                        "NaN or infinite"
                    )
                ),
                observed=metrics,
                expected=(
                    "all metrics finite"
                ),
            )
        )

    def _validate_thresholds(
        self,
        *,
        metrics: dict[str, float],
        checks: list[ValidationCheck],
    ) -> None:
        thresholds = {
            "accuracy": (
                self.policy.min_accuracy
            ),
            "precision": (
                self.policy.min_precision
            ),
            "recall": (
                self.policy.min_recall
            ),
            "f1": self.policy.min_f1,
            "roc_auc": (
                self.policy.min_roc_auc
            ),
            "average_precision": (
                self.policy
                .min_average_precision
            ),
        }

        for name, minimum in (
            thresholds.items()
        ):
            value = metrics[name]

            checks.append(
                ValidationCheck(
                    name=(
                        f"minimum_{name}"
                    ),
                    passed=(
                        value >= minimum
                    ),
                    message=(
                        f"{name} meets policy"
                        if value >= minimum
                        else (
                            f"{name} is below "
                            "minimum policy"
                        )
                    ),
                    observed=value,
                    expected=(
                        f">= {minimum}"
                    ),
                )
            )

    def _validate_against_baseline(
        self,
        *,
        candidate_metrics: dict[str, float],
        baseline_metrics: dict[str, float],
        checks: list[ValidationCheck],
    ) -> None:
        baseline_ap = baseline_metrics.get(
            "average_precision"
        )

        if baseline_ap is None:
            checks.append(
                ValidationCheck(
                    name=(
                        "candidate_vs_baseline"
                    ),
                    passed=False,
                    message=(
                        "Baseline Average Precision "
                        "is missing"
                    ),
                    observed=baseline_metrics,
                    expected=(
                        "average_precision metric"
                    ),
                )
            )

            return

        candidate_ap = (
            candidate_metrics[
                "average_precision"
            ]
        )

        minimum_allowed = (
            baseline_ap
            - self.policy
            .max_average_precision_regression
        )

        passed = (
            candidate_ap
            >= minimum_allowed
        )

        checks.append(
            ValidationCheck(
                name=(
                    "candidate_vs_baseline"
                ),
                passed=passed,
                message=(
                    "Candidate does not materially "
                    "regress from baseline"
                    if passed
                    else (
                        "Candidate materially "
                        "regresses from baseline"
                    )
                ),
                observed=candidate_ap,
                expected=(
                    f">= {minimum_allowed:.6f}"
                    " Average Precision"
                ),
            )
        )