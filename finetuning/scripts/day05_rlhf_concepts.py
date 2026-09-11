from __future__ import annotations

from finetuning.alignment.reward_lab import (
    DeterministicRewardModel,
    PreferencePair,
    kl_regularized_objective,
)

PREFERENCE_PAIRS = [
    PreferencePair(
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
    ),
    PreferencePair(
        prompt=(
            "What should I do when account "
            "verification is pending?"
        ),
        chosen=(
            "Review the verification status "
            "and check whether additional "
            "documents are required."
        ),
        rejected=(
            "It definitely means the account "
            "has been rejected."
        ),
    ),
]


def main() -> None:
    print("=" * 72)
    print(
        "Sprint 7 — Day 5: RLHF Concepts"
    )
    print(
        "Artifact: Alignment Architecture Notes"
    )
    print("=" * 72)

    print("\n1. Canonical RLHF architecture")

    print(
        """
Base Model
   ↓
Supervised Fine-Tuning
   ↓
Preference Data
   ↓
Reward Model
   ↓
RL Optimization
   ↓
Aligned Policy
"""
    )

    print("2. Reward-model concept lab")

    reward_model = (
        DeterministicRewardModel()
    )

    for index, pair in enumerate(
        PREFERENCE_PAIRS,
        start=1,
    ):
        comparison = (
            reward_model.compare(pair)
        )

        print(
            f"\nPair {index}"
        )

        print(
            f"Prompt: {pair.prompt}"
        )

        print(
            "Chosen reward:   "
            f"{comparison.chosen_reward:.3f}"
        )

        print(
            "Rejected reward: "
            f"{comparison.rejected_reward:.3f}"
        )

        print(
            "Margin:          "
            f"{comparison.margin:.3f}"
        )

        print(
            "Ranking loss:    "
            f"{comparison.ranking_loss:.6f}"
        )

        print(
            "Preferred correctly: "
            f"{comparison.preferred_correctly}"
        )

    print(
        "\n3. KL-control concept"
    )

    reward = 5.0
    kl = 2.0

    for beta in (
        0.0,
        0.1,
        0.5,
        1.0,
    ):
        objective = (
            kl_regularized_objective(
                reward=reward,
                kl_divergence=kl,
                beta=beta,
            )
        )

        print(
            f"reward={reward:.1f} "
            f"KL={kl:.1f} "
            f"beta={beta:.1f} "
            f"objective={objective:.3f}"
        )

    print(
        "\n4. Policy/reference architecture"
    )

    print(
        """
Prompt
  ↓
Policy Model
  ↓
Response
  ├──────────────→ Reward Model → reward
  │
  └──────────────→ Reference comparison → KL
                                   │
                      reward - beta × KL
                                   │
                                   ↓
                            policy update
"""
    )

    print(
        "5. Reward hacking example"
    )

    print(
        """
Suppose the reward model accidentally learns:

    longer response → higher reward

The policy may discover:

    repeat explanations
    add unnecessary details
    avoid concise answers

Reward can increase while real usefulness decreases.
"""
    )

    print(
        "6. Offline vs online feedback"
    )

    print(
        """
Offline:
- fixed preference dataset
- reproducible
- auditable
- potentially stale

Online:
- fresh deployment feedback
- new failure modes exposed
- noisier
- vulnerable to feedback loops/manipulation
"""
    )

    print(
        "7. Day 5 boundary"
    )

    print(
        "No PPO training was run."
    )

    print(
        "No production reward model "
        "was trained."
    )

    print(
        "No DPO implementation "
        "was introduced."
    )

    print(
        "\nDay 5 RLHF concepts complete."
    )


if __name__ == "__main__":
    main()

    #uv run python -m finetuning.scripts.day05_rlhf_concepts