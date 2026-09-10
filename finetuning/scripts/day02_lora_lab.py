from __future__ import annotations

import torch
from torch.nn import functional as F

from finetuning.lora.linear import LoRALinear


def main() -> None:
    torch.manual_seed(42)

    print("=" * 72)
    print("Sprint 7 — Day 2: LoRA Mathematics and Architecture")
    print("Artifact: LoRA Implementation")
    print("=" * 72)

    layer = LoRALinear(
        in_features=16,
        out_features=16,
        rank=2,
        alpha=4.0,
        bias=False,
    )

    print("\n1. Architecture")

    print(
        f"Base weight shape: {tuple(layer.base.weight.shape)}"
    )

    print(
        f"LoRA A shape:      {tuple(layer.lora_A.shape)}"
    )

    print(
        f"LoRA B shape:      {tuple(layer.lora_B.shape)}"
    )

    print(
        f"Rank:              {layer.rank}"
    )

    print(
        f"Alpha:             {layer.alpha}"
    )

    print(
        f"Scaling:           {layer.scaling}"
    )

    print("\n2. Mathematical model")

    print(
        "W' = W + ΔW"
    )

    print(
        "ΔW = scaling × BA"
    )

    print("\n3. Parameter summary")

    summary = layer.parameter_summary()

    print(
        f"Base parameters:       "
        f"{summary.base_parameters:,}"
    )

    print(
        f"Adapter parameters:    "
        f"{summary.adapter_parameters:,}"
    )

    print(
        f"Trainable parameters:  "
        f"{summary.trainable_parameters:,}"
    )

    print(
        f"Total parameters:      "
        f"{summary.total_parameters:,}"
    )

    print(
        f"Trainable percentage:  "
        f"{summary.trainable_percentage:.2f}%"
    )

    print(
        f"Adapter/base ratio:    "
        f"{summary.adapter_vs_base_percentage:.2f}%"
    )

    print("\n4. Parameter states")

    for name, parameter in layer.named_parameters():
        state = (
            "TRAINABLE"
            if parameter.requires_grad
            else "FROZEN"
        )

        print(
            f"{name:<25} "
            f"{parameter.numel():>6} "
            f"{state}"
        )

    inputs = torch.randn(
        8,
        16,
    )

    targets = torch.randn(
        8,
        16,
    )

    print("\n5. Initial behavior")

    base_output = layer.base(inputs).detach()

    adapted_output = layer(inputs).detach()

    initial_difference = (
        adapted_output
        - base_output
    ).abs().max().item()

    print(
        "Maximum base-vs-LoRA difference "
        f"at initialization: {initial_difference:.8f}"
    )

    print(
        "Expected: 0 because B starts at zero."
    )

    delta_before = layer.delta_weight().detach()

    print(
        "Initial ΔW norm: "
        f"{delta_before.norm().item():.8f}"
    )

    base_weight_before = (
        layer.base.weight
        .detach()
        .clone()
    )

    optimizer = torch.optim.SGD(
        [
            layer.lora_A,
            layer.lora_B,
        ],
        lr=0.1,
    )

    print("\n6. Train only LoRA parameters")

    for step in range(1, 11):
        optimizer.zero_grad()

        predictions = layer(inputs)

        loss = F.mse_loss(
            predictions,
            targets,
        )

        loss.backward()

        optimizer.step()

        print(
            f"Step {step:02d} "
            f"loss={loss.item():.6f}"
        )

    print("\n7. Validate parameter behavior")

    base_changed = not torch.equal(
        base_weight_before,
        layer.base.weight.detach(),
    )

    delta_after = layer.delta_weight().detach()

    print(
        f"Base weight changed: "
        f"{base_changed}"
    )

    print(
        f"ΔW norm after training: "
        f"{delta_after.norm().item():.8f}"
    )

    output_after = layer(inputs).detach()

    output_difference = (
        output_after
        - base_output
    ).abs().max().item()

    print(
        "Maximum base-vs-adapted difference "
        f"after training: {output_difference:.8f}"
    )

    print("\n8. Merge validation")

    unmerged_output = layer(inputs).detach()

    merged_output = (
        layer
        .merged_forward(inputs)
        .detach()
    )

    merge_difference = (
        unmerged_output
        - merged_output
    ).abs().max().item()

    print(
        "Maximum merged-vs-unmerged difference: "
        f"{merge_difference:.8f}"
    )

    print("\n9. Interpretation")

    print(
        "The original W remained frozen."
    )

    print(
        "Training modified only A and B."
    )

    print(
        "BA created a low-rank update ΔW."
    )

    print(
        "The effective layer behaves as W + ΔW."
    )

    print(
        "The adapter can also be mathematically "
        "merged into W for inference."
    )

    print("\nDay 2 lab complete.")


if __name__ == "__main__":
    main()