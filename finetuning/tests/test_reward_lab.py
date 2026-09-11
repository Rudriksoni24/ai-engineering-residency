import math

import pytest

from finetuning.alignment.reward_lab import (
    DeterministicRewardModel,
    PreferencePair,
    kl_regularized_objective,
    pairwise_logistic_loss,
)


def test_valid_preference_pair() -> None:
    pair = PreferencePair(
        prompt="Why did the payment fail?",
        chosen=(
            "I cannot know the exact reason "
            "without transaction details."
        ),
        rejected=(
            "It definitely failed because "
            "the account was closed."
        ),
    )

    pair.validate()


def test_empty_prompt_is_rejected() -> None:
    pair = PreferencePair(
        prompt=" ",
        chosen="Good answer.",
        rejected="Bad answer.",
    )

    with pytest.raises(
        ValueError,
        match="prompt",
    ):
        pair.validate()


def test_empty_chosen_response_is_rejected() -> None:
    pair = PreferencePair(
        prompt="Question",
        chosen=" ",
        rejected="Response",
    )

    with pytest.raises(
        ValueError,
        match="chosen",
    ):
        pair.validate()


def test_identical_responses_are_rejected() -> None:
    pair = PreferencePair(
        prompt="Question",
        chosen="Same",
        rejected="Same",
    )

    with pytest.raises(
        ValueError,
        match="must differ",
    ):
        pair.validate()


def test_reward_model_prefers_cautious_actionable_response() -> None:
    model = DeterministicRewardModel()

    pair = PreferencePair(
        prompt=(
            "Why was payment PAY-1001 declined?"
        ),
        chosen=(
            "I cannot know the exact reason "
            "without transaction details. "
            "Check the issuer decline code."
        ),
        rejected=(
            "The exact reason is that the "
            "customer has insufficient funds."
        ),
    )

    comparison = model.compare(
        pair
    )

    assert (
        comparison.chosen_reward
        > comparison.rejected_reward
    )

    assert comparison.margin > 0

    assert (
        comparison.preferred_correctly
        is True
    )


def test_correct_ranking_has_lower_loss_than_reversed_ranking() -> None:
    correct_loss = pairwise_logistic_loss(
        chosen_reward=3.0,
        rejected_reward=1.0,
    )

    reversed_loss = pairwise_logistic_loss(
        chosen_reward=1.0,
        rejected_reward=3.0,
    )

    assert (
        correct_loss
        < reversed_loss
    )


def test_larger_positive_margin_reduces_ranking_loss() -> None:
    small_margin = pairwise_logistic_loss(
        chosen_reward=2.0,
        rejected_reward=1.0,
    )

    large_margin = pairwise_logistic_loss(
        chosen_reward=5.0,
        rejected_reward=1.0,
    )

    assert (
        large_margin
        < small_margin
    )


def test_pairwise_loss_is_finite() -> None:
    loss = pairwise_logistic_loss(
        chosen_reward=100.0,
        rejected_reward=-100.0,
    )

    assert math.isfinite(
        loss
    )


def test_kl_penalty_reduces_objective() -> None:
    no_penalty = kl_regularized_objective(
        reward=5.0,
        kl_divergence=0.0,
        beta=0.5,
    )

    penalized = kl_regularized_objective(
        reward=5.0,
        kl_divergence=2.0,
        beta=0.5,
    )

    assert penalized < no_penalty


def test_higher_beta_penalizes_same_kl_more() -> None:
    weak_control = kl_regularized_objective(
        reward=5.0,
        kl_divergence=2.0,
        beta=0.1,
    )

    strong_control = kl_regularized_objective(
        reward=5.0,
        kl_divergence=2.0,
        beta=1.0,
    )

    assert (
        strong_control
        < weak_control
    )


def test_negative_kl_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="kl_divergence",
    ):
        kl_regularized_objective(
            reward=1.0,
            kl_divergence=-1.0,
            beta=0.1,
        )