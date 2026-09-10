from __future__ import annotations

import random
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

import torch
from peft import (
    LoraConfig,
    PeftModel,
    TaskType,
    get_peft_model,
)
from torch import Tensor, nn
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    PreTrainedTokenizerBase,
)

from finetuning.training.config import LocalLoRAConfig


@dataclass(frozen=True)
class ParameterSummary:
    total_parameters: int
    trainable_parameters: int

    @property
    def frozen_parameters(self) -> int:
        return (
            self.total_parameters
            - self.trainable_parameters
        )

    @property
    def trainable_percentage(self) -> float:
        if self.total_parameters == 0:
            return 0.0

        return (
            self.trainable_parameters
            / self.total_parameters
            * 100.0
        )


@dataclass(frozen=True)
class TrainingMetrics:
    first_loss: float
    final_loss: float
    steps: int


def set_seed(seed: int) -> None:
    random.seed(seed)
    torch.manual_seed(seed)

    if torch.backends.mps.is_available():
        torch.mps.manual_seed(seed)


def select_device() -> torch.device:
    if torch.backends.mps.is_available():
        return torch.device("mps")

    return torch.device("cpu")


def count_parameters(
    model: nn.Module,
) -> ParameterSummary:
    total = sum(
        parameter.numel()
        for parameter in model.parameters()
    )

    trainable = sum(
        parameter.numel()
        for parameter in model.parameters()
        if parameter.requires_grad
    )

    return ParameterSummary(
        total_parameters=total,
        trainable_parameters=trainable,
    )


def build_lora_config(
    config: LocalLoRAConfig,
) -> LoraConfig:
    config.validate()

    return LoraConfig(
        r=config.rank,
        lora_alpha=config.alpha,
        lora_dropout=config.dropout,
        target_modules=list(
            config.target_modules
        ),
        bias="none",
        task_type=TaskType.CAUSAL_LM,
    )


def find_matching_modules(
    model: nn.Module,
    target_modules: Iterable[str],
) -> dict[str, list[str]]:
    names = [
        name
        for name, _ in model.named_modules()
    ]

    result: dict[str, list[str]] = {}

    for target in target_modules:
        matches = [
            name
            for name in names
            if name.endswith(target)
        ]

        result[target] = matches

    return result


def validate_target_modules(
    model: nn.Module,
    target_modules: Iterable[str],
) -> dict[str, list[str]]:
    matches = find_matching_modules(
        model,
        target_modules,
    )

    missing = [
        name
        for name, found in matches.items()
        if not found
    ]

    if missing:
        raise ValueError(
            "LoRA target modules were not found: "
            + ", ".join(missing)
        )

    return matches


def load_tokenizer(
    model_name: str,
) -> PreTrainedTokenizerBase:
    tokenizer = AutoTokenizer.from_pretrained(
        model_name
    )

    if tokenizer.pad_token_id is None:
        if tokenizer.eos_token_id is None:
            raise ValueError(
                "tokenizer has neither pad_token "
                "nor eos_token"
            )

        tokenizer.pad_token = (
            tokenizer.eos_token
        )

    return tokenizer


def load_base_model(
    model_name: str,
) -> nn.Module:
    return AutoModelForCausalLM.from_pretrained(
        model_name
    )


def apply_lora(
    model: nn.Module,
    config: LocalLoRAConfig,
) -> PeftModel:
    validate_target_modules(
        model,
        config.target_modules,
    )

    lora_config = build_lora_config(config)

    return get_peft_model(
        model,
        lora_config,
    )


def encode_training_text(
    tokenizer: PreTrainedTokenizerBase,
    text: str,
    max_length: int,
    device: torch.device,
) -> dict[str, Tensor]:
    encoded = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=max_length,
    )

    input_ids = encoded["input_ids"].to(
        device
    )

    attention_mask = encoded[
        "attention_mask"
    ].to(device)

    labels = input_ids.clone()

    return {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "labels": labels,
    }


def train_adapter(
    model: PeftModel,
    tokenizer: PreTrainedTokenizerBase,
    training_texts: list[str],
    config: LocalLoRAConfig,
    device: torch.device,
) -> TrainingMetrics:
    if not training_texts:
        raise ValueError(
            "training_texts cannot be empty"
        )

    model.train()

    trainable_parameters = [
        parameter
        for parameter in model.parameters()
        if parameter.requires_grad
    ]

    if not trainable_parameters:
        raise ValueError(
            "PEFT model has no trainable parameters"
        )

    optimizer = torch.optim.AdamW(
        trainable_parameters,
        lr=config.learning_rate,
    )

    first_loss: float | None = None
    final_loss = 0.0

    for step in range(
        config.training_steps
    ):
        text = training_texts[
            step % len(training_texts)
        ]

        batch = encode_training_text(
            tokenizer=tokenizer,
            text=text,
            max_length=config.max_length,
            device=device,
        )

        optimizer.zero_grad()

        outputs = model(**batch)

        loss = outputs.loss

        if loss is None:
            raise RuntimeError(
                "causal LM returned no loss"
            )

        if not torch.isfinite(loss):
            raise RuntimeError(
                f"non-finite loss at step {step + 1}"
            )

        loss.backward()

        optimizer.step()

        loss_value = float(
            loss.detach().cpu().item()
        )

        if first_loss is None:
            first_loss = loss_value

        final_loss = loss_value

        print(
            f"step={step + 1:02d}/"
            f"{config.training_steps:02d} "
            f"loss={loss_value:.6f}"
        )

    if first_loss is None:
        raise RuntimeError(
            "training produced no steps"
        )

    return TrainingMetrics(
        first_loss=first_loss,
        final_loss=final_loss,
        steps=config.training_steps,
    )


@torch.inference_mode()
def generate_text(
    model: nn.Module,
    tokenizer: PreTrainedTokenizerBase,
    prompt: str,
    device: torch.device,
    *,
    max_new_tokens: int = 40,
) -> str:
    model.eval()

    encoded = tokenizer(
        prompt,
        return_tensors="pt",
    )

    input_ids = encoded["input_ids"].to(
        device
    )

    attention_mask = encoded[
        "attention_mask"
    ].to(device)

    generated = model.generate(
        input_ids=input_ids,
        attention_mask=attention_mask,
        max_new_tokens=max_new_tokens,
        do_sample=False,
        pad_token_id=tokenizer.pad_token_id,
    )

    return tokenizer.decode(
        generated[0],
        skip_special_tokens=True,
    )


def save_adapter(
    model: PeftModel,
    output_dir: Path,
) -> None:
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    model.save_pretrained(
        output_dir
    )


def load_saved_adapter(
    *,
    model_name: str,
    adapter_dir: Path,
    device: torch.device,
) -> PeftModel:
    base_model = load_base_model(
        model_name
    )

    model = PeftModel.from_pretrained(
        base_model,
        adapter_dir,
    )

    model.to(device)

    return model