from __future__ import annotations

import numpy as np
import pandas as pd

from ml.data.synthetic import (
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    generate_synthetic_transactions,
)
from ml.models.fraud_models import (
    build_logistic_regression,
)
from ml.validation.data import (
    DataValidationPolicy,
    FraudDataValidator,
)
from ml.validation.model import (
    FraudModelValidator,
    ModelValidationPolicy,
)


def test_valid_dataset_passes() -> None:
    dataframe = (
        generate_synthetic_transactions(
            n_samples=1_000,
            random_seed=42,
        )
    )

    result = (
        FraudDataValidator()
        .validate(dataframe)
    )

    assert result.passed
    assert not result.failures


def test_empty_dataset_fails() -> None:
    result = (
        FraudDataValidator()
        .validate(
            pd.DataFrame()
        )
    )

    assert not result.passed

    assert any(
        failure.name
        == "dataset_not_empty"
        for failure in result.failures
    )


def test_missing_required_column_fails() -> None:
    dataframe = (
        generate_synthetic_transactions(
            n_samples=1_000,
            random_seed=42,
        )
    )

    dataframe = dataframe.drop(
        columns=[
            "transaction_amount",
        ]
    )

    result = (
        FraudDataValidator()
        .validate(dataframe)
    )

    assert not result.passed

    assert any(
        failure.name
        == "required_columns"
        for failure in result.failures
    )


def test_invalid_hour_fails() -> None:
    dataframe = (
        generate_synthetic_transactions(
            n_samples=1_000,
            random_seed=42,
        )
    )

    dataframe.loc[
        dataframe.index[0],
        "transaction_hour",
    ] = 27

    result = (
        FraudDataValidator()
        .validate(dataframe)
    )

    assert not result.passed

    assert any(
        failure.name
        == "transaction_hour_range"
        for failure in result.failures
    )


def test_negative_amount_fails() -> None:
    dataframe = (
        generate_synthetic_transactions(
            n_samples=1_000,
            random_seed=42,
        )
    )

    dataframe.loc[
        dataframe.index[0],
        "transaction_amount",
    ] = -10

    result = (
        FraudDataValidator()
        .validate(dataframe)
    )

    assert not result.passed


def test_invalid_label_fails() -> None:
    dataframe = (
        generate_synthetic_transactions(
            n_samples=1_000,
            random_seed=42,
        )
    )

    dataframe.loc[
        dataframe.index[0],
        TARGET_COLUMN,
    ] = 2

    result = (
        FraudDataValidator()
        .validate(dataframe)
    )

    assert not result.passed

    assert any(
        failure.name
        == "label_domain"
        for failure in result.failures
    )


def test_single_class_dataset_fails() -> None:
    dataframe = (
        generate_synthetic_transactions(
            n_samples=1_000,
            random_seed=42,
        )
    )

    dataframe[
        TARGET_COLUMN
    ] = 0

    result = (
        FraudDataValidator()
        .validate(dataframe)
    )

    assert not result.passed

    assert any(
        failure.name
        == "both_classes_present"
        for failure in result.failures
    )


def test_invalid_category_fails() -> None:
    dataframe = (
        generate_synthetic_transactions(
            n_samples=1_000,
            random_seed=42,
        )
    )

    dataframe.loc[
        dataframe.index[0],
        "transaction_type",
    ] = "crypto_transfer"

    result = (
        FraudDataValidator()
        .validate(dataframe)
    )

    assert not result.passed


def test_excessive_duplicates_fail() -> None:
    dataframe = (
        generate_synthetic_transactions(
            n_samples=1_000,
            random_seed=42,
        )
    )

    duplicates = dataframe.iloc[
        :100
    ].copy()

    corrupted = pd.concat(
        [
            dataframe,
            duplicates,
        ],
        ignore_index=True,
    )

    validator = FraudDataValidator(
        DataValidationPolicy(
            max_duplicate_fraction=0.01,
        )
    )

    result = validator.validate(
        corrupted
    )

    assert not result.passed

    assert any(
        failure.name
        == "duplicate_fraction"
        for failure in result.failures
    )


def test_excessive_missing_values_fail() -> None:
    dataframe = (
        generate_synthetic_transactions(
            n_samples=1_000,
            random_seed=42,
        )
    )

    dataframe.loc[
        dataframe.index[:200],
        "account_balance",
    ] = np.nan

    result = (
        FraudDataValidator()
        .validate(dataframe)
    )

    assert not result.passed

    assert any(
        failure.name
        == "feature_missing_fraction"
        for failure in result.failures
    )


def test_small_dataset_fails() -> None:
    dataframe = (
        generate_synthetic_transactions(
            n_samples=100,
            random_seed=42,
        )
    )

    result = (
        FraudDataValidator()
        .validate(dataframe)
    )

    assert not result.passed

    assert any(
        failure.name
        == "minimum_dataset_size"
        for failure in result.failures
    )


def fitted_candidate():
    dataframe = (
        generate_synthetic_transactions(
            n_samples=1_500,
            random_seed=42,
        )
    )

    X = dataframe[
        FEATURE_COLUMNS
    ]

    y = dataframe[
        TARGET_COLUMN
    ]

    model = build_logistic_regression(
        random_seed=42
    )

    model.fit(
        X.iloc[:1_200],
        y.iloc[:1_200],
    )

    return (
        model,
        X.iloc[1_200:],
        y.iloc[1_200:],
    )


def test_candidate_meeting_requirements_passes() -> None:
    model, X, y = (
        fitted_candidate()
    )

    validator = FraudModelValidator(
        ModelValidationPolicy(
            min_accuracy=0.0,
            min_precision=0.0,
            min_recall=0.0,
            min_f1=0.0,
            min_roc_auc=0.0,
            min_average_precision=0.0,
        )
    )

    result = validator.validate(
        model=model,
        X=X,
        y=y,
    )

    assert result.passed


def test_candidate_below_threshold_fails() -> None:
    model, X, y = (
        fitted_candidate()
    )

    validator = FraudModelValidator(
        ModelValidationPolicy(
            min_accuracy=0.0,
            min_precision=0.0,
            min_recall=0.0,
            min_f1=0.0,
            min_roc_auc=0.99,
            min_average_precision=0.99,
        )
    )

    result = validator.validate(
        model=model,
        X=X,
        y=y,
    )

    assert not result.passed

    assert any(
        failure.name
        in {
            "minimum_roc_auc",
            "minimum_average_precision",
        }
        for failure in result.failures
    )


def test_prediction_metrics_are_finite() -> None:
    model, X, y = (
        fitted_candidate()
    )

    result = (
        FraudModelValidator(
            ModelValidationPolicy(
                min_accuracy=0.0,
                min_precision=0.0,
                min_recall=0.0,
                min_f1=0.0,
                min_roc_auc=0.0,
                min_average_precision=0.0,
            )
        )
        .validate(
            model=model,
            X=X,
            y=y,
        )
    )

    assert all(
        np.isfinite(value)
        for value
        in result.metrics.values()
    )


def test_candidate_vs_baseline_passes_within_tolerance() -> None:
    model, X, y = (
        fitted_candidate()
    )

    validator = FraudModelValidator(
        ModelValidationPolicy(
            min_accuracy=0.0,
            min_precision=0.0,
            min_recall=0.0,
            min_f1=0.0,
            min_roc_auc=0.0,
            min_average_precision=0.0,
            max_average_precision_regression=0.05,
        )
    )

    first = validator.validate(
        model=model,
        X=X,
        y=y,
    )

    baseline = {
        "average_precision": (
            first.metrics[
                "average_precision"
            ]
            + 0.02
        )
    }

    result = validator.validate(
        model=model,
        X=X,
        y=y,
        baseline_metrics=baseline,
    )

    assert result.passed


def test_candidate_vs_baseline_fails_on_large_regression() -> None:
    model, X, y = (
        fitted_candidate()
    )

    validator = FraudModelValidator(
        ModelValidationPolicy(
            min_accuracy=0.0,
            min_precision=0.0,
            min_recall=0.0,
            min_f1=0.0,
            min_roc_auc=0.0,
            min_average_precision=0.0,
            max_average_precision_regression=0.01,
        )
    )

    result = validator.validate(
        model=model,
        X=X,
        y=y,
        baseline_metrics={
            "average_precision": 1.0,
        },
    )

    assert not result.passed

    assert any(
        failure.name
        == "candidate_vs_baseline"
        for failure in result.failures
    )