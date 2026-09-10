from __future__ import annotations

import torch

from finetuning.fundamentals.lab import (
    TinyClassifier,
    bytes_to_kib,
    count_parameters,
    estimate_training_memory,
    freeze_module,
    inspect_parameter_states,
    run_single_supervised_step,
)


def main() -> None:
    torch.manual_seed(42)

    print("=" * 70)
    print("Sprint 7 — Day 1: Fine-Tuning Fundamentals")
    print("Artifact: Fine-Tuning Study Lab")
    print("=" * 70)

    model = TinyClassifier()

    print("\n1. Initial model")
    print(model)

    full_summary = count_parameters(model)

    print("\n2. Full fine-tuning parameter summary")
    print(
        f"Total parameters:     "
        f"{full_summary.total_parameters:,}"
    )
    print(
        f"Trainable parameters: "
        f"{full_summary.trainable_parameters:,}"
    )
    print(
        f"Frozen parameters:    "
        f"{full_summary.frozen_parameters:,}"
    )
    print(
        f"Trainable percentage: "
        f"{full_summary.trainable_percentage:.2f}%"
    )

    full_memory = estimate_training_memory(model)

    print("\n3. Simplified FP32 full-training memory estimate")
    print(
        "Model weights:       "
        f"{bytes_to_kib(full_memory.model_weight_bytes):.2f} KiB"
    )
    print(
        "Gradients:           "
        f"{bytes_to_kib(full_memory.gradient_bytes):.2f} KiB"
    )
    print(
        "Optimizer states:    "
        f"{bytes_to_kib(full_memory.optimizer_state_bytes):.2f} KiB"
    )
    print(
        "Core training state: "
        f"{bytes_to_kib(full_memory.estimated_training_state_bytes):.2f} KiB"
    )
    print(
        "Activation memory:   "
        "not included because it depends on the runtime workload"
    )

    print("\n4. Freeze the feature layer")
    freeze_module(model.feature_layer)

    partial_summary = count_parameters(model)

    print(
        f"Total parameters:     "
        f"{partial_summary.total_parameters:,}"
    )
    print(
        f"Trainable parameters: "
        f"{partial_summary.trainable_parameters:,}"
    )
    print(
        f"Frozen parameters:    "
        f"{partial_summary.frozen_parameters:,}"
    )
    print(
        f"Trainable percentage: "
        f"{partial_summary.trainable_percentage:.2f}%"
    )

    print("\n5. Parameter states")

    for parameter_state in inspect_parameter_states(model):
        state = (
            "TRAINABLE"
            if parameter_state.trainable
            else "FROZEN"
        )

        print(
            f"{parameter_state.name:<30} "
            f"{parameter_state.parameter_count:>5} "
            f"{state}"
        )

    partial_memory = estimate_training_memory(model)

    print("\n6. Memory estimate after freezing feature layer")
    print(
        "Model weights:       "
        f"{bytes_to_kib(partial_memory.model_weight_bytes):.2f} KiB"
    )
    print(
        "Gradients:           "
        f"{bytes_to_kib(partial_memory.gradient_bytes):.2f} KiB"
    )
    print(
        "Optimizer states:    "
        f"{bytes_to_kib(partial_memory.optimizer_state_bytes):.2f} KiB"
    )
    print(
        "Core training state: "
        f"{bytes_to_kib(partial_memory.estimated_training_state_bytes):.2f} KiB"
    )

    inputs = torch.tensor(
        [
            [1.0, 0.0, 0.0, 1.0],
            [0.0, 1.0, 1.0, 0.0],
            [1.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 1.0],
        ],
        dtype=torch.float32,
    )

    targets = torch.tensor(
        [0, 1, 0, 1],
        dtype=torch.long,
    )

    print("\n7. Run one supervised fine-tuning step")

    result = run_single_supervised_step(
        model=model,
        inputs=inputs,
        targets=targets,
        learning_rate=0.05,
    )

    print(
        f"Loss before update: "
        f"{result.loss_before_update:.6f}"
    )
    print(
        "Trainable parameters changed: "
        f"{result.trainable_parameters_changed}"
    )
    print(
        "Frozen parameters changed:    "
        f"{result.frozen_parameters_changed}"
    )

    print("\n8. Interpretation")
    print(
        "The forward pass produced predictions."
    )
    print(
        "The loss measured prediction error."
    )
    print(
        "backward() produced gradients."
    )
    print(
        "optimizer.step() updated trainable parameters."
    )
    print(
        "Frozen parameters participated in the forward pass "
        "but were not updated."
    )

    print("\nDay 1 lab complete.")


if __name__ == "__main__":
    main()