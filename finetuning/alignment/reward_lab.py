from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class PreferencePair:
    prompt: str
    chosen: str
    rejected: str

    def validate(self) -> None:
        if not self.prompt.strip():
            raise ValueError(
                "prompt cannot be empty"
            )

        if not self.chosen.strip():
            raise ValueError(
                "chosen response cannot be empty"
            )

        if not self.rejected.strip():
            raise ValueError(
                "rejected response cannot be empty"
            )

        if (
            self.chosen.strip()
            == self.rejected.strip()
        ):
            raise ValueError(
                "chosen and rejected responses "
                "must differ"
            )


@dataclass(frozen=True)
class RewardComparison:
    chosen_reward: float
    rejected_reward: float
    margin: float
    ranking_loss: float
    preferred_correctly: bool


class DeterministicRewardModel:
    """
    Educational deterministic reward scorer.

    This is not a learned neural reward model.

    It exposes reward-model behavior using transparent heuristics so
    ranking, margins, and preference losses can be studied without
    hiding the concept behind a large transformer.
    """

    def __init__(
        self,
        *,
        unsupported_claim_penalty: float = 2.0,
        uncertainty_reward: float = 1.0,
        actionability_reward: float = 1.0,
        excessive_length_penalty: float = 0.5,
    ) -> None:
        self.unsupported_claim_penalty = (
            unsupported_claim_penalty
        )

        self.uncertainty_reward = (
            uncertainty_reward
        )

        self.actionability_reward = (
            actionability_reward
        )

        self.excessive_length_penalty = (
            excessive_length_penalty
        )

    def score(
        self,
        prompt: str,
        response: str,
    ) -> float:
        if not prompt.strip():
            raise ValueError(
                "prompt cannot be empty"
            )

        if not response.strip():
            raise ValueError(
                "response cannot be empty"
            )

        normalized = response.lower()

        reward = 0.0

        unsupported_claim_phrases = (
            "definitely",
            "certainly",
            "the exact reason is",
            "must have failed because",
        )

        uncertainty_phrases = (
            "cannot know",
            "can't know",
            "without more information",
            "without transaction details",
            "check the",
            "verify the",
        )

        actionability_phrases = (
            "check",
            "verify",
            "review",
            "contact",
            "inspect",
        )

        if any(
            phrase in normalized
            for phrase in unsupported_claim_phrases
        ):
            reward -= (
                self.unsupported_claim_penalty
            )

        if any(
            phrase in normalized
            for phrase in uncertainty_phrases
        ):
            reward += (
                self.uncertainty_reward
            )

        if any(
            phrase in normalized
            for phrase in actionability_phrases
        ):
            reward += (
                self.actionability_reward
            )

        word_count = len(
            response.split()
        )

        if word_count > 80:
            reward -= (
                self.excessive_length_penalty
            )

        return reward

    def compare(
        self,
        pair: PreferencePair,
    ) -> RewardComparison:
        pair.validate()

        chosen_reward = self.score(
            pair.prompt,
            pair.chosen,
        )

        rejected_reward = self.score(
            pair.prompt,
            pair.rejected,
        )

        margin = (
            chosen_reward
            - rejected_reward
        )

        loss = pairwise_logistic_loss(
            chosen_reward=chosen_reward,
            rejected_reward=rejected_reward,
        )

        return RewardComparison(
            chosen_reward=chosen_reward,
            rejected_reward=rejected_reward,
            margin=margin,
            ranking_loss=loss,
            preferred_correctly=(
                chosen_reward
                > rejected_reward
            ),
        )


def pairwise_logistic_loss(
    *,
    chosen_reward: float,
    rejected_reward: float,
) -> float:
    """
    Stable implementation of:

        -log(sigmoid(chosen - rejected))

    Equivalent to:

        softplus(-(chosen - rejected))
    """

    margin = (
        chosen_reward
        - rejected_reward
    )

    value = -margin

    if value > 0:
        return (
            value
            + math.log1p(
                math.exp(-value)
            )
        )

    return math.log1p(
        math.exp(value)
    )


def kl_regularized_objective(
    *,
    reward: float,
    kl_divergence: float,
    beta: float,
) -> float:
    """
    Simplified educational alignment objective:

        reward - beta * KL

    This is not a complete PPO objective.
    """

    if kl_divergence < 0:
        raise ValueError(
            "kl_divergence cannot be negative"
        )

    if beta < 0:
        raise ValueError(
            "beta cannot be negative"
        )

    return (
        reward
        - beta * kl_divergence
    )