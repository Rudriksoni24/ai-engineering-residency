from __future__ import annotations

from finetuning.alignment.dpo_lab import (
    DPOLogProbabilities,
    DPOPreferencePair,
    compare_dpo,
    sequence_log_probability,
)


def main() -> None:
    print("=" * 72)
    print(
        "Sprint 7 — Day 6: "
        "Direct Preference Optimization"
    )
    print(
        "Artifact: Preference Optimization Lab"
    )
    print("=" * 72)

    pair = DPOPreferencePair(
        prompt=(
            "Why was payment PAY-1001 declined?"
        ),
        chosen=(
            "I cannot determine the exact reason "
            "without the issuer decline code. "
            "Check the transaction response."
        ),
        rejected=(
            "It definitely failed because "
            "the customer had insufficient funds."
        ),
    )

    pair.validate()

    print("\n1. Preference pair")

    print(
        f"Prompt:\n{pair.prompt}"
    )

    print(
        f"\nChosen:\n{pair.chosen}"
    )

    print(
        f"\nRejected:\n{pair.rejected}"
    )

    print(
        "\n2. Token log-probability example"
    )

    chosen_tokens = [
        -0.3,
        -0.7,
        -0.4,
        -0.5,
    ]

    rejected_tokens = [
        -0.8,
        -1.2,
        -0.9,
        -0.6,
    ]

    chosen_sequence_logp = (
        sequence_log_probability(
            chosen_tokens
        )
    )

    rejected_sequence_logp = (
        sequence_log_probability(
            rejected_tokens
        )
    )

    print(
        "Chosen sequence log probability: "
        f"{chosen_sequence_logp:.3f}"
    )

    print(
        "Rejected sequence log probability: "
        f"{rejected_sequence_logp:.3f}"
    )

    print(
        "\n3. Policy / reference example"
    )

    probabilities = DPOLogProbabilities(
        policy_chosen=-4.0,
        policy_rejected=-8.0,
        reference_chosen=-6.0,
        reference_rejected=-7.0,
    )

    print(
        "Policy chosen:     "
        f"{probabilities.policy_chosen:.3f}"
    )

    print(
        "Policy rejected:   "
        f"{probabilities.policy_rejected:.3f}"
    )

    print(
        "Reference chosen:  "
        f"{probabilities.reference_chosen:.3f}"
    )

    print(
        "Reference rejected:"
        f" {probabilities.reference_rejected:.3f}"
    )

    print(
        "\n4. Preference margins"
    )

    print(
        "Policy margin: "
        f"{probabilities.policy_margin:.3f}"
    )

    print(
        "Reference margin: "
        f"{probabilities.reference_margin:.3f}"
    )

    print(
        "Relative preference margin: "
        f"{probabilities.relative_preference_margin:.3f}"
    )

    print(
        "\n5. Beta comparison"
    )

    for beta in (
        0.1,
        0.5,
        1.0,
    ):
        comparison = compare_dpo(
            probabilities=probabilities,
            beta=beta,
        )

        print(
            f"beta={beta:.1f} "
            f"logit={comparison.logit:.3f} "
            f"loss={comparison.loss:.6f}"
        )

    print(
        "\n6. Good vs bad policy preference"
    )

    good_policy = DPOLogProbabilities(
        policy_chosen=-2.0,
        policy_rejected=-6.0,
        reference_chosen=-4.0,
        reference_rejected=-4.0,
    )

    bad_policy = DPOLogProbabilities(
        policy_chosen=-6.0,
        policy_rejected=-2.0,
        reference_chosen=-4.0,
        reference_rejected=-4.0,
    )

    good = compare_dpo(
        probabilities=good_policy,
        beta=0.5,
    )

    bad = compare_dpo(
        probabilities=bad_policy,
        beta=0.5,
    )

    print(
        f"Good policy loss: "
        f"{good.loss:.6f}"
    )

    print(
        f"Bad policy loss:  "
        f"{bad.loss:.6f}"
    )

    print(
        "\n7. RLHF vs DPO"
    )

    print(
        """
Traditional RLHF:

Preference Data
      ↓
Reward Model
      ↓
PPO
      ↓
Policy


DPO:

Preference Data
      ↓
Chosen / Rejected Log Probabilities
      ↓
Direct Preference Loss
      ↓
Policy
"""
    )

    print(
        "8. Interpretation"
    )

    print(
        "DPO directly compares preference "
        "behavior between policy and reference."
    )

    print(
        "No explicit learned reward model "
        "was required for this lab."
    )

    print(
        "No PPO rollout loop was required."
    )

    print(
        "The reference model relationship "
        "still matters."
    )

    print(
        "This is an educational loss lab, "
        "not a production DPO training run."
    )

    print(
        "\nDay 6 DPO lab complete."
    )


if __name__ == "__main__":
    main()

    #uv run python -m finetuning.scripts.day06_dpo_lab