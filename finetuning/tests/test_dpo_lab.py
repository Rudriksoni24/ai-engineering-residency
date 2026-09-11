import math

import pytest

from finetuning.alignment.dpo_lab import (
    DPOLogProbabilities,
    DPOPreferencePair,
    compare_dpo,
    dpo_loss,
    sequence_log_probability,
)


def test_valid_preference_pair() -> None:
    pair = DPOPreferencePair(
        prompt="Why was payment declined?",
        chosen=(
            "Check the issuer decline code."
        ),
        rejected=(
            "It definitely failed because "
            "the account is empty."
        ),
    )

    pair.validate()


def test_empty_prompt_is_rejected() -> None:
    pair = DPOPreferencePair(
        prompt=" ",
        chosen="Good response",
        rejected="Bad response",
    )

    with pytest.raises(
        ValueError,
        match="prompt",
    ):
        pair.validate()


def test_empty_chosen_is_rejected() -> None:
    pair = DPOPreferencePair(
        prompt="Question",
        chosen=" ",
        rejected="Rejected",
    )

    with pytest.raises(
        ValueError,
        match="chosen",
    ):
        pair.validate()


def test_empty_rejected_is_rejected() -> None:
    pair = DPOPreferencePair(
        prompt="Question",
        chosen="Chosen",
        rejected=" ",
    )

    with pytest.raises(
        ValueError,
        match="rejected",
    ):
        pair.validate()


def test_identical_responses_are_rejected() -> None:
    pair = DPOPreferencePair(
        prompt="Question",
        chosen="Same",
        rejected="Same",
    )

    with pytest.raises(
        ValueError,
        match="must differ",
    ):
        pair.validate()


def test_sequence_log_probability_is_sum() -> None:
    result = sequence_log_probability(
        [
            -0.5,
            -1.0,
            -0.25,
        ]
    )

    assert result == pytest.approx(
        -1.75
    )


def test_policy_margin_prefers_chosen_when_larger() -> None:
    probabilities = DPOLogProbabilities(
        policy_chosen=-2.0,
        policy_rejected=-5.0,
        reference_chosen=-3.0,
        reference_rejected=-3.0,
    )

    assert (
        probabilities.policy_margin
        == pytest.approx(3.0)
    )


def test_relative_margin_accounts_for_reference() -> None:
    probabilities = DPOLogProbabilities(
        policy_chosen=-2.0,
        policy_rejected=-4.0,
        reference_chosen=-1.0,
        reference_rejected=-2.0,
    )

    assert (
        probabilities.policy_margin
        == pytest.approx(2.0)
    )

    assert (
        probabilities.reference_margin
        == pytest.approx(1.0)
    )

    assert (
        probabilities.relative_preference_margin
        == pytest.approx(1.0)
    )


def test_dpo_loss_is_finite() -> None:
    probabilities = DPOLogProbabilities(
        policy_chosen=-2.0,
        policy_rejected=-4.0,
        reference_chosen=-3.0,
        reference_rejected=-3.5,
    )

    loss = dpo_loss(
        probabilities=probabilities,
        beta=0.1,
    )

    assert math.isfinite(
        loss
    )


def test_better_chosen_preference_reduces_loss() -> None:
    weak = DPOLogProbabilities(
        policy_chosen=-4.0,
        policy_rejected=-4.0,
        reference_chosen=-4.0,
        reference_rejected=-4.0,
    )

    strong = DPOLogProbabilities(
        policy_chosen=-2.0,
        policy_rejected=-6.0,
        reference_chosen=-4.0,
        reference_rejected=-4.0,
    )

    weak_loss = dpo_loss(
        probabilities=weak,
        beta=0.5,
    )

    strong_loss = dpo_loss(
        probabilities=strong,
        beta=0.5,
    )

    assert (
        strong_loss
        < weak_loss
    )


def test_rejected_preference_increases_loss() -> None:
    good = DPOLogProbabilities(
        policy_chosen=-2.0,
        policy_rejected=-5.0,
        reference_chosen=-3.0,
        reference_rejected=-3.0,
    )

    bad = DPOLogProbabilities(
        policy_chosen=-5.0,
        policy_rejected=-2.0,
        reference_chosen=-3.0,
        reference_rejected=-3.0,
    )

    assert (
        dpo_loss(
            probabilities=good,
            beta=0.5,
        )
        <
        dpo_loss(
            probabilities=bad,
            beta=0.5,
        )
    )


def test_beta_changes_loss_behavior() -> None:
    probabilities = DPOLogProbabilities(
        policy_chosen=-2.0,
        policy_rejected=-5.0,
        reference_chosen=-3.0,
        reference_rejected=-3.0,
    )

    small_beta = dpo_loss(
        probabilities=probabilities,
        beta=0.1,
    )

    large_beta = dpo_loss(
        probabilities=probabilities,
        beta=1.0,
    )

    assert (
        large_beta
        < small_beta
    )


def test_beta_must_be_positive() -> None:
    probabilities = DPOLogProbabilities(
        policy_chosen=-2.0,
        policy_rejected=-3.0,
        reference_chosen=-2.0,
        reference_rejected=-3.0,
    )

    with pytest.raises(
        ValueError,
        match="beta",
    ):
        dpo_loss(
            probabilities=probabilities,
            beta=0.0,
        )


def test_comparison_contains_expected_values() -> None:
    probabilities = DPOLogProbabilities(
        policy_chosen=-2.0,
        policy_rejected=-5.0,
        reference_chosen=-3.0,
        reference_rejected=-4.0,
    )

    comparison = compare_dpo(
        probabilities=probabilities,
        beta=0.5,
    )

    assert (
        comparison.policy_margin
        == pytest.approx(3.0)
    )

    assert (
        comparison.reference_margin
        == pytest.approx(1.0)
    )

    assert (
        comparison.relative_preference_margin
        == pytest.approx(2.0)
    )

    assert (
        comparison.logit
        == pytest.approx(1.0)
    )

    assert comparison.loss > 0