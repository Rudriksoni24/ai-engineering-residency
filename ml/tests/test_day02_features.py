from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ml.data.synthetic import (
    FEATURE_COLUMNS,
    generate_synthetic_transactions,
)
from ml.features.fraud_features import (
    ENGINEERED_COLUMNS,
    FraudFeatureTransformer,
)
from ml.models.engineered import (
    build_engineered_classifier,
)
from ml.training.comparison import (
    compare_feature_pipelines,
)
from ml.training.pipeline import (
    TrainingConfig,
)


def test_feature_transform_is_deterministic() -> None:
    dataframe = generate_synthetic_transactions(
        n_samples=500,
        random_seed=42,
    )

    X = dataframe[FEATURE_COLUMNS]

    transformer = FraudFeatureTransformer()

    first = transformer.fit_transform(X)
    second = transformer.transform(X)

    pd.testing.assert_frame_equal(
        first,
        second,
    )


def test_engineered_feature_schema_is_stable() -> None:
    dataframe = generate_synthetic_transactions(
        n_samples=500,
        random_seed=42,
    )

    transformed = FraudFeatureTransformer().fit_transform(
        dataframe[FEATURE_COLUMNS]
    )

    assert list(transformed.columns) == (
        ENGINEERED_COLUMNS
    )


def test_amount_log_is_created() -> None:
    dataframe = generate_synthetic_transactions(
        n_samples=500,
        random_seed=42,
    )

    transformed = FraudFeatureTransformer().fit_transform(
        dataframe[FEATURE_COLUMNS]
    )

    assert "amount_log" in transformed.columns

    assert transformed["amount_log"].notna().all()


def test_night_transaction_flag_is_binary() -> None:
    dataframe = generate_synthetic_transactions(
        n_samples=500,
        random_seed=42,
    )

    transformed = FraudFeatureTransformer().fit_transform(
        dataframe[FEATURE_COLUMNS]
    )

    values = set(
        transformed[
            "is_night_transaction"
        ].unique()
    )

    assert values.issubset({0.0, 1.0})


def test_amount_to_balance_ratio_handles_zero_balance() -> None:
    dataframe = generate_synthetic_transactions(
        n_samples=500,
        random_seed=42,
    )

    X = dataframe[
        FEATURE_COLUMNS
    ].copy()

    X.loc[
        X.index[0],
        "account_balance",
    ] = 0.0

    transformed = FraudFeatureTransformer().fit_transform(
        X
    )

    assert np.isnan(
        transformed.loc[
            X.index[0],
            "amount_to_balance_ratio",
        ]
    )


def test_account_age_bucket_is_created() -> None:
    dataframe = generate_synthetic_transactions(
        n_samples=500,
        random_seed=42,
    )

    transformed = FraudFeatureTransformer().fit_transform(
        dataframe[FEATURE_COLUMNS]
    )

    expected = {
        "new",
        "young",
        "established",
        "mature",
    }

    actual = set(
        transformed[
            "account_age_bucket"
        ].dropna()
    )

    assert actual.issubset(expected)


def test_feature_transformer_rejects_missing_columns() -> None:
    dataframe = generate_synthetic_transactions(
        n_samples=500,
        random_seed=42,
    )

    X = dataframe[
        FEATURE_COLUMNS
    ].drop(
        columns=[
            "transaction_amount",
        ]
    )

    transformer = FraudFeatureTransformer()

    with pytest.raises(
        ValueError,
        match="missing required columns",
    ):
        transformer.fit_transform(X)


def test_engineered_pipeline_handles_missing_numeric_value() -> None:
    dataframe = generate_synthetic_transactions(
        n_samples=1_000,
        random_seed=42,
    )

    X = dataframe[
        FEATURE_COLUMNS
    ].copy()

    y = dataframe[
        "fraud_label"
    ]

    X.loc[
        X.index[0],
        "transaction_amount",
    ] = np.nan

    model = build_engineered_classifier(
        random_seed=42
    )

    model.fit(
        X,
        y,
    )

    predictions = model.predict(
        X.iloc[:10]
    )

    assert len(predictions) == 10


def test_engineered_pipeline_handles_missing_categorical_value() -> None:
    dataframe = generate_synthetic_transactions(
        n_samples=1_000,
        random_seed=42,
    )

    X = dataframe[
        FEATURE_COLUMNS
    ].copy()

    y = dataframe[
        "fraud_label"
    ]

    X.loc[
        X.index[0],
        "merchant_category",
    ] = None

    model = build_engineered_classifier(
        random_seed=42
    )

    model.fit(
        X,
        y,
    )

    prediction = model.predict(
        X.iloc[[0]]
    )

    assert prediction.shape == (1,)


def test_engineered_pipeline_handles_unseen_category() -> None:
    dataframe = generate_synthetic_transactions(
        n_samples=1_000,
        random_seed=42,
    )

    X = dataframe[
        FEATURE_COLUMNS
    ]

    y = dataframe[
        "fraud_label"
    ]

    model = build_engineered_classifier(
        random_seed=42
    )

    model.fit(
        X,
        y,
    )

    unseen = X.iloc[[0]].copy()

    unseen["transaction_type"] = (
        "brand_new_transaction_type"
    )

    prediction = model.predict(
        unseen
    )

    assert prediction.shape == (1,)


def test_numeric_scaler_is_not_refit_during_predict() -> None:
    dataframe = generate_synthetic_transactions(
        n_samples=1_000,
        random_seed=42,
    )

    X = dataframe[
        FEATURE_COLUMNS
    ]

    y = dataframe[
        "fraud_label"
    ]

    model = build_engineered_classifier(
        random_seed=42
    )

    model.fit(
        X.iloc[:800],
        y.iloc[:800],
    )

    preprocessing = model.named_steps[
        "preprocessing"
    ]

    numeric_pipeline = (
        preprocessing.named_transformers_[
            "numeric"
        ]
    )

    scaler = numeric_pipeline.named_steps[
        "scaler"
    ]

    mean_before = scaler.mean_.copy()

    extreme_test = X.iloc[
        800:
    ].copy()

    extreme_test[
        "transaction_amount"
    ] = 999_999_999.0

    model.predict(
        extreme_test
    )

    mean_after = scaler.mean_

    np.testing.assert_array_equal(
        mean_before,
        mean_after,
    )


def test_model_comparison_is_deterministic() -> None:
    dataframe = generate_synthetic_transactions(
        n_samples=1_000,
        random_seed=42,
    )

    config = TrainingConfig(
        random_seed=42,
        test_size=0.20,
    )

    first = compare_feature_pipelines(
        dataframe,
        config=config,
    )

    second = compare_feature_pipelines(
        dataframe,
        config=config,
    )

    assert (
        first.baseline_metrics
        == second.baseline_metrics
    )

    assert (
        first.engineered_metrics
        == second.engineered_metrics
    )


def test_comparison_uses_same_split_sizes() -> None:
    dataframe = generate_synthetic_transactions(
        n_samples=1_000,
        random_seed=42,
    )

    result = compare_feature_pipelines(
        dataframe,
        config=TrainingConfig(
            random_seed=42,
            test_size=0.20,
        ),
    )

    assert result.train_size == 800
    assert result.test_size == 200