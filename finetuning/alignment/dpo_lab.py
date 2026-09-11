from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class DPOPreferencePair:
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
class DPOLogProbabilities:
    policy_chosen: float
    policy_rejected: float
    reference_chosen: float
    reference_rejected: float

    @property
    def policy_margin(self) -> float:
        return (
            self.policy_chosen
            - self.policy_rejected
        )

    @property
    def reference_margin(self) -> float:
        return (
            self.reference_chosen
            - self.reference_rejected
        )

    @property
    def relative_preference_margin(
        self,
    ) -> float:
        return (
            self.policy_margin
            - self.reference_margin
        )


@dataclass(frozen=True)
class DPOComparison:
    policy_margin: float
    reference_margin: float
    relative_preference_margin: float
    beta: float
    logit: float
    loss: float


def softplus(value: float) -> float:
    """
    Numerically stable softplus:

        log(1 + exp(value))
    """

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


def dpo_logit(
    *,
    probabilities: DPOLogProbabilities,
    beta: float,
) -> float:
    if beta <= 0:
        raise ValueError(
            "beta must be greater than zero"
        )

    return (
        beta
        * probabilities.relative_preference_margin
    )


def dpo_loss(
    *,
    probabilities: DPOLogProbabilities,
    beta: float,
) -> float:
    """
    Educational DPO preference loss.

    loss =
        -log sigmoid(
            beta * (
                policy_margin
                - reference_margin
            )
        )

    Using:

        -log sigmoid(x)
        =
        softplus(-x)
    """

    logit = dpo_logit(
        probabilities=probabilities,
        beta=beta,
    )

    return softplus(
        -logit
    )


def compare_dpo(
    *,
    probabilities: DPOLogProbabilities,
    beta: float,
) -> DPOComparison:
    logit = dpo_logit(
        probabilities=probabilities,
        beta=beta,
    )

    loss = dpo_loss(
        probabilities=probabilities,
        beta=beta,
    )

    return DPOComparison(
        policy_margin=(
            probabilities.policy_margin
        ),
        reference_margin=(
            probabilities.reference_margin
        ),
        relative_preference_margin=(
            probabilities.relative_preference_margin
        ),
        beta=beta,
        logit=logit,
        loss=loss,
    )


def sequence_log_probability(
    token_log_probabilities: list[float],
) -> float:
    if not token_log_probabilities:
        raise ValueError(
            "token_log_probabilities "
            "cannot be empty"
        )

    if not all(
        math.isfinite(value)
        for value in token_log_probabilities
    ):
        raise ValueError(
            "token log probabilities "
            "must be finite"
        )

    return sum(
        token_log_probabilities
    )