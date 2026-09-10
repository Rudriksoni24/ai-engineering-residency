from pathlib import Path

import pytest
import torch
from peft import PeftModel
from transformers import (
    LlamaConfig,
    LlamaForCausalLM,
)

from finetuning.training.config import (
    LocalLoRAConfig,
)
from finetuning.training.peft_local import (
    apply_lora,
    build_lora_config,
    count_parameters,
    find_matching_modules,
    validate_target_modules,
)


def build_tiny_llama() -> LlamaForCausalLM:
    config = LlamaConfig(
        vocab_size=128,
        hidden_size=32,
        intermediate_size=64,
        num_hidden_layers=2,
        num_attention_heads=4,
        num_key_value_heads=2,
        max_position_embeddings=64,
    )

    return LlamaForCausalLM(config)


def test_training_config_is_valid() -> None:
    config = LocalLoRAConfig()

    config.validate()


def test_invalid_rank_is_rejected() -> None:
    config = LocalLoRAConfig(
        rank=0
    )

    with pytest.raises(
        ValueError,
        match="rank",
    ):
        config.validate()


def test_lora_config_uses_expected_targets() -> None:
    config = LocalLoRAConfig(
        rank=4,
        alpha=8,
        target_modules=(
            "q_proj",
            "v_proj",
        ),
    )

    lora_config = build_lora_config(
        config
    )

    assert lora_config.r == 4
    assert lora_config.lora_alpha == 8

    assert set(
        lora_config.target_modules
    ) == {
        "q_proj",
        "v_proj",
    }


def test_target_modules_exist_in_tiny_llama() -> None:
    model = build_tiny_llama()

    matches = find_matching_modules(
        model,
        (
            "q_proj",
            "v_proj",
        ),
    )

    assert matches["q_proj"]
    assert matches["v_proj"]


def test_missing_target_module_is_rejected() -> None:
    model = build_tiny_llama()

    with pytest.raises(
        ValueError,
        match="were not found",
    ):
        validate_target_modules(
            model,
            (
                "does_not_exist",
            ),
        )


def test_peft_reduces_trainable_parameter_fraction() -> None:
    model = build_tiny_llama()

    original = count_parameters(model)

    assert (
        original.trainable_parameters
        == original.total_parameters
    )

    config = LocalLoRAConfig(
        rank=2,
        alpha=4,
        target_modules=(
            "q_proj",
            "v_proj",
        ),
    )

    peft_model = apply_lora(
        model,
        config,
    )

    adapted = count_parameters(
        peft_model
    )

    assert (
        adapted.trainable_parameters
        < original.trainable_parameters
    )

    assert (
        adapted.trainable_percentage
        < 100.0
    )


def test_lora_parameters_are_trainable() -> None:
    model = build_tiny_llama()

    config = LocalLoRAConfig(
        rank=2,
        alpha=4,
    )

    peft_model = apply_lora(
        model,
        config,
    )

    trainable_names = [
        name
        for name, parameter
        in peft_model.named_parameters()
        if parameter.requires_grad
    ]

    assert trainable_names

    assert all(
        "lora_" in name
        for name in trainable_names
    )


def test_non_lora_base_parameters_are_frozen() -> None:
    model = build_tiny_llama()

    peft_model = apply_lora(
        model,
        LocalLoRAConfig(
            rank=2,
            alpha=4,
        ),
    )

    base_parameters = [
        parameter
        for name, parameter
        in peft_model.named_parameters()
        if "lora_" not in name
    ]

    assert base_parameters

    assert all(
        parameter.requires_grad is False
        for parameter in base_parameters
    )


def test_adapter_parameters_receive_gradients() -> None:
    torch.manual_seed(42)

    model = build_tiny_llama()

    peft_model = apply_lora(
        model,
        LocalLoRAConfig(
            rank=2,
            alpha=4,
        ),
    )

    input_ids = torch.randint(
        low=0,
        high=128,
        size=(1, 12),
    )

    outputs = peft_model(
        input_ids=input_ids,
        labels=input_ids,
    )

    assert outputs.loss is not None

    outputs.loss.backward()

    adapter_gradients = [
        parameter.grad
        for name, parameter
        in peft_model.named_parameters()
        if "lora_" in name
        and parameter.requires_grad
    ]

    assert adapter_gradients

    assert any(
        gradient is not None
        for gradient in adapter_gradients
    )


def test_adapter_can_be_saved_and_reloaded(
    tmp_path: Path,
) -> None:
    torch.manual_seed(42)

    base = build_tiny_llama()

    peft_model = apply_lora(
        base,
        LocalLoRAConfig(
            rank=2,
            alpha=4,
        ),
    )

    adapter_dir = (
        tmp_path / "adapter"
    )

    peft_model.save_pretrained(
        adapter_dir
    )

    assert (
        adapter_dir
        / "adapter_config.json"
    ).exists()

    fresh_base = build_tiny_llama()

    reloaded = PeftModel.from_pretrained(
        fresh_base,
        adapter_dir,
    )

    assert isinstance(
        reloaded,
        PeftModel,
    )