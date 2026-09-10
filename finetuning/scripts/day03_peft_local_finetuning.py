from __future__ import annotations

import gc

import torch

from finetuning.training.config import (
    LocalLoRAConfig,
)
from finetuning.training.peft_local import (
    apply_lora,
    count_parameters,
    generate_text,
    load_base_model,
    load_saved_adapter,
    load_tokenizer,
    save_adapter,
    select_device,
    set_seed,
    train_adapter,
    validate_target_modules,
)

TRAINING_TEXTS = [
    (
        "User: Classify transaction TXN-001. "
        "Amount: INR 2500. Status: declined.\n"
        "Assistant: "
        '{"transaction_id":"TXN-001",'
        '"status":"DECLINED"}'
    ),
    (
        "User: Classify transaction TXN-002. "
        "Amount: INR 9100. Status: approved.\n"
        "Assistant: "
        '{"transaction_id":"TXN-002",'
        '"status":"APPROVED"}'
    ),
    (
        "User: Classify transaction TXN-003. "
        "Amount: INR 430. Status: pending.\n"
        "Assistant: "
        '{"transaction_id":"TXN-003",'
        '"status":"PENDING"}'
    ),
    (
        "User: Classify transaction TXN-004. "
        "Amount: INR 18000. Status: declined.\n"
        "Assistant: "
        '{"transaction_id":"TXN-004",'
        '"status":"DECLINED"}'
    ),
]


EVALUATION_PROMPT = (
    "User: Classify transaction TXN-900. "
    "Amount: INR 3500. Status: declined.\n"
    "Assistant:"
)


def release_model(
    model: object,
) -> None:
    del model

    gc.collect()

    if torch.backends.mps.is_available():
        torch.mps.empty_cache()


def main() -> None:
    config = LocalLoRAConfig()

    config.validate()

    set_seed(config.seed)

    device = select_device()

    print("=" * 72)
    print(
        "Sprint 7 — Day 3: "
        "PEFT and Local Fine-Tuning"
    )
    print(
        "Artifact: Adapted Local Model"
    )
    print("=" * 72)

    print("\n1. Training configuration")

    print(
        f"Model:          {config.model_name}"
    )
    print(
        f"Device:         {device}"
    )
    print(
        f"Rank:           {config.rank}"
    )
    print(
        f"Alpha:          {config.alpha}"
    )
    print(
        f"Dropout:        {config.dropout}"
    )
    print(
        "Targets:        "
        f"{config.target_modules}"
    )
    print(
        f"Learning rate:  "
        f"{config.learning_rate}"
    )
    print(
        f"Training steps: "
        f"{config.training_steps}"
    )
    print(
        f"Max length:     "
        f"{config.max_length}"
    )
    print(
        f"Seed:           {config.seed}"
    )
    print(
        f"Artifact:       {config.output_dir}"
    )

    print("\n2. Workload classification")
    print(
        "Model class: small pretrained causal LM"
    )
    print(
        "Training class: real local PEFT adaptation"
    )
    print(
        "Scale: short educational run"
    )
    print(
        "Production-scale training: NO"
    )

    tokenizer = load_tokenizer(
        config.model_name
    )

    print("\n3. Load base model")

    base_model = load_base_model(
        config.model_name
    )

    base_summary = count_parameters(
        base_model
    )

    print(
        "Base total parameters: "
        f"{base_summary.total_parameters:,}"
    )

    base_model.to(device)

    print("\n4. Baseline inference")

    baseline = generate_text(
        model=base_model,
        tokenizer=tokenizer,
        prompt=EVALUATION_PROMPT,
        device=device,
    )

    print(baseline)

    print("\n5. Validate target modules")

    matches = validate_target_modules(
        base_model,
        config.target_modules,
    )

    for target, module_names in matches.items():
        print(
            f"{target}: "
            f"{len(module_names)} module(s)"
        )

        for module_name in module_names[:3]:
            print(
                f"  - {module_name}"
            )

        if len(module_names) > 3:
            print("  - ...")

    print("\n6. Inject PEFT LoRA")

    model = apply_lora(
        base_model,
        config,
    )

    model.to(device)

    peft_summary = count_parameters(
        model
    )

    print(
        "Total parameters:     "
        f"{peft_summary.total_parameters:,}"
    )

    print(
        "Trainable parameters: "
        f"{peft_summary.trainable_parameters:,}"
    )

    print(
        "Frozen parameters:    "
        f"{peft_summary.frozen_parameters:,}"
    )

    print(
        "Trainable percentage: "
        f"{peft_summary.trainable_percentage:.4f}%"
    )

    print("\nPEFT summary:")
    model.print_trainable_parameters()

    print("\n7. Train adapters")

    metrics = train_adapter(
        model=model,
        tokenizer=tokenizer,
        training_texts=TRAINING_TEXTS,
        config=config,
        device=device,
    )

    print(
        f"First loss: {metrics.first_loss:.6f}"
    )

    print(
        f"Final loss: {metrics.final_loss:.6f}"
    )

    print(
        "Loss decreased: "
        f"{metrics.final_loss < metrics.first_loss}"
    )

    print("\n8. Adapted inference")

    adapted_before_save = generate_text(
        model=model,
        tokenizer=tokenizer,
        prompt=EVALUATION_PROMPT,
        device=device,
    )

    print(adapted_before_save)

    print("\n9. Save adapter")

    save_adapter(
        model,
        config.output_dir,
    )

    print(
        f"Adapter saved to: "
        f"{config.output_dir}"
    )

    print("\n10. Release trained model")

    del model
    del base_model

    gc.collect()

    if torch.backends.mps.is_available():
        torch.mps.empty_cache()

    print("\n11. Reload base + saved adapter")

    reloaded_model = load_saved_adapter(
        model_name=config.model_name,
        adapter_dir=config.output_dir,
        device=device,
    )

    reloaded_summary = count_parameters(
        reloaded_model
    )

    print(
        "Reloaded total parameters: "
        f"{reloaded_summary.total_parameters:,}"
    )

    print("\n12. Reloaded-adapter inference")

    adapted_after_reload = generate_text(
        model=reloaded_model,
        tokenizer=tokenizer,
        prompt=EVALUATION_PROMPT,
        device=device,
    )

    print(adapted_after_reload)

    print("\n13. Before vs after")

    print("\nBASELINE:")
    print(baseline)

    print("\nADAPTED:")
    print(adapted_after_reload)

    print(
        "\nOutputs differ: "
        f"{baseline != adapted_after_reload}"
    )

    print("\n14. Interpretation")

    print(
        "The pretrained base model was reused."
    )

    print(
        "PEFT injected LoRA into selected "
        "attention projections."
    )

    print(
        "Only a small subset of parameters "
        "was optimized."
    )

    print(
        "The adapter was saved independently "
        "of the base model."
    )

    print(
        "A fresh base model instance successfully "
        "loaded the saved adapter."
    )

    print(
        "Any claimed behavioral improvement "
        "must be supported by evaluation, "
        "not merely by a lower training loss."
    )

    print("\nDay 3 local adaptation complete.")


if __name__ == "__main__":
    main()

    # uv run python -m finetuning.scripts.day03_peft_local_finetuning