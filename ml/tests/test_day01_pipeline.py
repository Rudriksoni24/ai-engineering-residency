from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ml.data.synthetic import (
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    generate_synthetic_transactions,
)
from ml.training.pipeline import (
    TrainingConfig,
    run_training_pipeline,
    validate_raw_dataset,
)


def test_synthetic_dataset_is_deterministic() -> None:
    first = generate_synthetic_transactions(
        n_samples=500,
        random_seed=42,
    )

    second = generate_synthetic_transactions(
        n_samples=500,
        random_seed=42,
    )

    pd.testing.assert_frame_equal(
        first,
        second,
    )


def test_synthetic_dataset_has_expected_schema() -> None:
    dataframe = generate_synthetic_transactions(
        n_samples=500,
        random_seed=42,
    )

    assert list(dataframe.columns) == (
        FEATURE_COLUMNS + [TARGET_COLUMN]
    )

    assert len(dataframe) == 500


def test_dataset_is_imbalanced_but_contains_both_classes() -> None:
    dataframe = generate_synthetic_transactions(
        n_samples=3_000,
        random_seed=42,
    )

    fraud_rate = dataframe[TARGET_COLUMN].mean()

    assert 0.0 < fraud_rate < 0.20
    assert set(
        dataframe[TARGET_COLUMN].unique()
    ) == {0, 1}


def test_validation_rejects_empty_dataset() -> None:
    dataframe = pd.DataFrame()

    with pytest.raises(
        ValueError,
        match="Dataset cannot be empty",
    ):
        validate_raw_dataset(dataframe)


def test_validation_rejects_missing_required_column() -> None:
    dataframe = generate_synthetic_transactions(
        n_samples=500,
        random_seed=42,
    )

    dataframe = dataframe.drop(
        columns=["transaction_amount"]
    )

    with pytest.raises(
        ValueError,
        match="missing required columns",
    ):
        validate_raw_dataset(dataframe)


def test_validation_rejects_invalid_target() -> None:
    dataframe = generate_synthetic_transactions(
        n_samples=500,
        random_seed=42,
    )

    dataframe.loc[
        dataframe.index[0],
        TARGET_COLUMN,
    ] = 2

    with pytest.raises(
        ValueError,
        match="must contain only 0 or 1",
    ):
        validate_raw_dataset(dataframe)


def test_training_pipeline_produces_predictions() -> None:
    dataframe = generate_synthetic_transactions(
        n_samples=1_000,
        random_seed=42,
    )

    result = run_training_pipeline(
        dataframe,
        config=TrainingConfig(
            random_seed=42,
            test_size=0.20,
        ),
    )

    assert result.train_size == 800
    assert result.test_size == 200
    assert len(result.predictions) == 200

    assert set(
        np.unique(result.predictions)
    ).issubset({0, 1})


def test_metrics_are_valid_probabilities() -> None:
    dataframe = generate_synthetic_transactions(
        n_samples=1_000,
        random_seed=42,
    )

    result = run_training_pipeline(dataframe)

    metrics = result.metrics

    assert 0.0 <= metrics.accuracy <= 1.0
    assert 0.0 <= metrics.precision <= 1.0
    assert 0.0 <= metrics.recall <= 1.0
    assert 0.0 <= metrics.f1 <= 1.0


def test_confusion_matrix_accounts_for_all_test_rows() -> None:
    dataframe = generate_synthetic_transactions(
        n_samples=1_000,
        random_seed=42,
    )

    result = run_training_pipeline(dataframe)

    matrix = result.metrics.confusion_matrix

    total = sum(
        value
        for row in matrix
        for value in row
    )

    assert total == result.test_size


def test_full_training_run_is_reproducible() -> None:
    dataframe = generate_synthetic_transactions(
        n_samples=1_000,
        random_seed=42,
    )

    config = TrainingConfig(
        random_seed=42,
        test_size=0.20,
    )

    first = run_training_pipeline(
        dataframe,
        config=config,
    )

    second = run_training_pipeline(
        dataframe,
        config=config,
    )

    np.testing.assert_array_equal(
        first.predictions,
        second.predictions,
    )

    assert first.metrics == second.metrics


def test_unseen_category_can_be_predicted() -> None:
    dataframe = generate_synthetic_transactions(
        n_samples=1_000,
        random_seed=42,
    )

    result = run_training_pipeline(dataframe)

    example = dataframe[
        FEATURE_COLUMNS
    ].iloc[[0]].copy()

    example["merchant_category"] = (
        "previously_unseen_category"
    )

    prediction = result.model.predict(example)

    assert prediction.shape == (1,)
    assert prediction[0] in {0, 1}

    # uv run python -m ml.scripts.run_day01