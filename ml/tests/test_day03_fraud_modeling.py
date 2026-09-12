from __future__ import annotations

import numpy as np
import pytest

from ml.data.synthetic import (
    generate_synthetic_transactions,
)
from ml.models.fraud_models import (
    MODEL_BUILDERS,
)
from ml.training.fraud_modeling import (
    evaluate_probabilities,
    predictions_from_threshold,
    run_fraud_modeling,
    select_candidate_model,
    select_threshold_for_recall,
)
from ml.training.pipeline import (
    TrainingConfig,
)


def test_day03_has_multiple_models() -> None:
    assert {
        "logistic_regression",
        "random_forest",
        "hist_gradient_boosting",
    }.issubset(
        MODEL_BUILDERS.keys()
    )


def test_threshold_predictions_are_binary() -> None:
    probabilities = np.array(
        [
            0.10,
            0.49,
            0.50,
            0.90,
        ]
    )

    predictions = predictions_from_threshold(
        probabilities,
        threshold=0.50,
    )

    np.testing.assert_array_equal(
        predictions,
        np.array(
            [
                0,
                0,
                1,
                1,
            ]
        ),
    )


def test_invalid_threshold_rejected() -> None:
    probabilities = np.array(
        [
            0.1,
            0.9,
        ]
    )

    with pytest.raises(
        ValueError,
        match="threshold must be between 0 and 1",
    ):
        predictions_from_threshold(
            probabilities,
            threshold=1.5,
        )


def test_lower_threshold_increases_or_preserves_recall() -> None:
    y_true = np.array(
        [
            0,
            0,
            1,
            1,
            1,
        ]
    )

    probabilities = np.array(
        [
            0.10,
            0.40,
            0.45,
            0.60,
            0.90,
        ]
    )

    high = evaluate_probabilities(
        y_true=y_true,
        probabilities=probabilities,
        threshold=0.70,
    )

    low = evaluate_probabilities(
        y_true=y_true,
        probabilities=probabilities,
        threshold=0.40,
    )

    assert low.recall >= high.recall


def test_probability_metrics_are_valid() -> None:
    y_true = np.array(
        [
            0,
            0,
            0,
            1,
            1,
        ]
    )

    probabilities = np.array(
        [
            0.05,
            0.15,
            0.20,
            0.75,
            0.90,
        ]
    )

    result = evaluate_probabilities(
        y_true=y_true,
        probabilities=probabilities,
    )

    assert 0.0 <= result.accuracy <= 1.0
    assert 0.0 <= result.precision <= 1.0
    assert 0.0 <= result.recall <= 1.0
    assert 0.0 <= result.f1 <= 1.0
    assert 0.0 <= result.roc_auc <= 1.0
    assert (
        0.0
        <= result.average_precision
        <= 1.0
    )


def test_good_ranking_has_high_roc_auc() -> None:
    y_true = np.array(
        [
            0,
            0,
            0,
            1,
            1,
            1,
        ]
    )

    probabilities = np.array(
        [
            0.05,
            0.10,
            0.20,
            0.75,
            0.85,
            0.95,
        ]
    )

    result = evaluate_probabilities(
        y_true=y_true,
        probabilities=probabilities,
    )

    assert result.roc_auc > 0.9
    assert result.average_precision > 0.9


def test_threshold_selector_meets_recall_floor() -> None:
    y_true = np.array(
        [
            0,
            0,
            0,
            1,
            1,
            1,
            1,
        ]
    )

    probabilities = np.array(
        [
            0.05,
            0.10,
            0.30,
            0.35,
            0.55,
            0.75,
            0.95,
        ]
    )

    threshold = (
        select_threshold_for_recall(
            y_true=y_true,
            probabilities=probabilities,
            minimum_recall=0.75,
        )
    )

    metrics = evaluate_probabilities(
        y_true=y_true,
        probabilities=probabilities,
        threshold=threshold,
    )

    assert metrics.recall >= 0.75


def test_full_modeling_returns_all_models() -> None:
    dataframe = generate_synthetic_transactions(
        n_samples=2_000,
        random_seed=42,
    )

    result = run_fraud_modeling(
        dataframe,
        config=TrainingConfig(
            random_seed=42,
            test_size=0.20,
        ),
        minimum_recall=0.70,
    )

    assert set(
        result.evaluations
    ) == set(
        MODEL_BUILDERS
    )


def test_each_model_produces_probability_metrics() -> None:
    dataframe = generate_synthetic_transactions(
        n_samples=2_000,
        random_seed=42,
    )

    result = run_fraud_modeling(
        dataframe,
        config=TrainingConfig(
            random_seed=42,
            test_size=0.20,
        ),
        minimum_recall=0.70,
    )

    for evaluation in (
        result.evaluations.values()
    ):
        metrics = evaluation.metrics

        assert (
            0.0
            <= metrics.roc_auc
            <= 1.0
        )

        assert (
            0.0
            <= metrics.average_precision
            <= 1.0
        )

        assert len(
            evaluation.probabilities
        ) == result.test_size


def test_selected_candidate_exists() -> None:
    dataframe = generate_synthetic_transactions(
        n_samples=2_000,
        random_seed=42,
    )

    result = run_fraud_modeling(
        dataframe,
        config=TrainingConfig(
            random_seed=42,
        ),
        minimum_recall=0.70,
    )

    assert (
        result.selected_model_name
        in result.evaluations
    )


def test_modeling_is_reproducible() -> None:
    dataframe = generate_synthetic_transactions(
        n_samples=2_000,
        random_seed=42,
    )

    config = TrainingConfig(
        random_seed=42,
        test_size=0.20,
    )

    first = run_fraud_modeling(
        dataframe,
        config=config,
        minimum_recall=0.70,
    )

    second = run_fraud_modeling(
        dataframe,
        config=config,
        minimum_recall=0.70,
    )

    assert (
        first.selected_model_name
        == second.selected_model_name
    )

    assert (
        first.selected_threshold
        == second.selected_threshold
    )

    for name in first.evaluations:
        assert (
            first.evaluations[name].metrics
            == second.evaluations[name].metrics
        )


def test_invalid_recall_floor_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="minimum_recall",
    ):
        select_threshold_for_recall(
            y_true=np.array([0, 1]),
            probabilities=np.array(
                [
                    0.1,
                    0.9,
                ]
            ),
            minimum_recall=0.0,
        )