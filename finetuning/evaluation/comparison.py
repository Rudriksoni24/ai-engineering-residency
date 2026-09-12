from __future__ import annotations

from dataclasses import dataclass
from statistics import mean

import torch
from torch import Tensor, nn
from transformers import PreTrainedTokenizerBase


@dataclass(frozen=True)
class EvaluationCase:
    case_id: str
    prompt: str
    expected_response: str

    def validate(self) -> None:
        if not self.case_id.strip():
            raise ValueError(
                "case_id cannot be empty"
            )

        if not self.prompt.strip():
            raise ValueError(
                "prompt cannot be empty"
            )

        if not self.expected_response.strip():
            raise ValueError(
                "expected_response cannot be empty"
            )


@dataclass(frozen=True)
class EvaluationResult:
    case_id: str
    base_loss: float
    adapted_loss: float

    @property
    def loss_delta(self) -> float:
        return (
            self.adapted_loss
            - self.base_loss
        )

    @property
    def improved(self) -> bool:
        return (
            self.adapted_loss
            < self.base_loss
        )


@dataclass(frozen=True)
class EvaluationSummary:
    case_count: int
    improved_cases: int
    regressed_cases: int
    unchanged_cases: int
    average_base_loss: float
    average_adapted_loss: float

    @property
    def average_loss_delta(self) -> float:
        return (
            self.average_adapted_loss
            - self.average_base_loss
        )

    @property
    def improved_overall(self) -> bool:
        return (
            self.average_adapted_loss
            < self.average_base_loss
        )


def build_completion_batch(
    *,
    tokenizer: PreTrainedTokenizerBase,
    prompt: str,
    expected_response: str,
    max_length: int,
    device: torch.device,
) -> dict[str, Tensor]:
    if not prompt:
        raise ValueError(
            "prompt cannot be empty"
        )

    if not expected_response:
        raise ValueError(
            "expected_response cannot be empty"
        )

    if max_length <= 0:
        raise ValueError(
            "max_length must be greater than zero"
        )

    prompt_encoding = tokenizer(
        prompt,
        add_special_tokens=True,
        truncation=False,
    )

    response_encoding = tokenizer(
        expected_response,
        add_special_tokens=False,
        truncation=False,
    )

    prompt_ids = list(
        prompt_encoding["input_ids"]
    )

    response_ids = list(
        response_encoding["input_ids"]
    )

    if not response_ids:
        raise ValueError(
            "expected response produced no tokens"
        )

    combined_ids = (
        prompt_ids
        + response_ids
    )

    if len(combined_ids) > max_length:
        raise ValueError(
            "evaluation example exceeds max_length; "
            "do not silently truncate expected response"
        )

    labels = (
        [-100] * len(prompt_ids)
        + response_ids
    )

    input_ids = torch.tensor(
        [combined_ids],
        dtype=torch.long,
        device=device,
    )

    attention_mask = torch.ones_like(
        input_ids
    )

    label_tensor = torch.tensor(
        [labels],
        dtype=torch.long,
        device=device,
    )

    return {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "labels": label_tensor,
    }


@torch.inference_mode()
def completion_loss(
    *,
    model: nn.Module,
    tokenizer: PreTrainedTokenizerBase,
    prompt: str,
    expected_response: str,
    max_length: int,
    device: torch.device,
) -> float:
    model.eval()

    batch = build_completion_batch(
        tokenizer=tokenizer,
        prompt=prompt,
        expected_response=expected_response,
        max_length=max_length,
        device=device,
    )

    outputs = model(
        **batch
    )

    if outputs.loss is None:
        raise RuntimeError(
            "model returned no evaluation loss"
        )

    loss = float(
        outputs.loss
        .detach()
        .cpu()
        .item()
    )

    if not torch.isfinite(
        torch.tensor(loss)
    ):
        raise RuntimeError(
            "evaluation loss is not finite"
        )

    return loss


def make_result(
    *,
    case_id: str,
    base_loss: float,
    adapted_loss: float,
) -> EvaluationResult:
    if not case_id.strip():
        raise ValueError(
            "case_id cannot be empty"
        )

    return EvaluationResult(
        case_id=case_id,
        base_loss=base_loss,
        adapted_loss=adapted_loss,
    )


def summarize_results(
    results: list[EvaluationResult],
    *,
    tolerance: float = 1e-8,
) -> EvaluationSummary:
    if not results:
        raise ValueError(
            "results cannot be empty"
        )

    if tolerance < 0:
        raise ValueError(
            "tolerance cannot be negative"
        )

    improved = 0
    regressed = 0
    unchanged = 0

    for result in results:
        delta = result.loss_delta

        if abs(delta) <= tolerance:
            unchanged += 1
        elif delta < 0:
            improved += 1
        else:
            regressed += 1

    return EvaluationSummary(
        case_count=len(results),
        improved_cases=improved,
        regressed_cases=regressed,
        unchanged_cases=unchanged,
        average_base_loss=mean(
            result.base_loss
            for result in results
        ),
        average_adapted_loss=mean(
            result.adapted_loss
            for result in results
        ),
    )