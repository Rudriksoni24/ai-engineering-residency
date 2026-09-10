from __future__ import annotations

import math
from dataclasses import dataclass

import torch
from torch import Tensor, nn
from torch.nn import functional as F


@dataclass(frozen=True)
class LoRAParameterSummary:
    base_parameters: int
    adapter_parameters: int
    trainable_parameters: int
    total_parameters: int

    @property
    def trainable_percentage(self) -> float:
        if self.total_parameters == 0:
            return 0.0

        return (
            self.trainable_parameters
            / self.total_parameters
            * 100.0
        )

    @property
    def adapter_vs_base_percentage(self) -> float:
        if self.base_parameters == 0:
            return 0.0

        return (
            self.adapter_parameters
            / self.base_parameters
            * 100.0
        )


class LoRALinear(nn.Module):
    """
    First-principles LoRA wrapper around a linear layer.

    Base computation:

        y = Wx + b

    LoRA computation:

        y = Wx + b + scaling * BAx

    where:

        A shape = [rank, in_features]
        B shape = [out_features, rank]

    The base linear parameters remain frozen.
    """

    def __init__(
        self,
        in_features: int,
        out_features: int,
        rank: int,
        alpha: float = 1.0,
        bias: bool = True,
    ) -> None:
        super().__init__()

        if in_features <= 0:
            raise ValueError(
                "in_features must be greater than zero"
            )

        if out_features <= 0:
            raise ValueError(
                "out_features must be greater than zero"
            )

        if rank <= 0:
            raise ValueError(
                "rank must be greater than zero"
            )

        if rank > min(in_features, out_features):
            raise ValueError(
                "rank should not exceed the smaller layer dimension"
            )

        if alpha <= 0:
            raise ValueError(
                "alpha must be greater than zero"
            )

        self.in_features = in_features
        self.out_features = out_features
        self.rank = rank
        self.alpha = alpha

        self.scaling = alpha / rank

        self.base = nn.Linear(
            in_features,
            out_features,
            bias=bias,
        )

        self.lora_A = nn.Parameter(
            torch.empty(
                rank,
                in_features,
            )
        )

        self.lora_B = nn.Parameter(
            torch.zeros(
                out_features,
                rank,
            )
        )

        self.reset_lora_parameters()
        self.freeze_base_parameters()

    def reset_lora_parameters(self) -> None:
        """
        Initialize A randomly and B to zero.

        Since B starts at zero:

            BA = 0

        so the adapter initially contributes exactly zero.
        """

        nn.init.kaiming_uniform_(
            self.lora_A,
            a=math.sqrt(5),
        )

        nn.init.zeros_(self.lora_B)

    def freeze_base_parameters(self) -> None:
        for parameter in self.base.parameters():
            parameter.requires_grad = False

    def adapter_output(self, inputs: Tensor) -> Tensor:
        """
        Compute:

            BAx

        using two low-rank linear transformations.
        """

        low_rank = F.linear(
            inputs,
            self.lora_A,
        )

        return F.linear(
            low_rank,
            self.lora_B,
        )

    def forward(self, inputs: Tensor) -> Tensor:
        base_output = self.base(inputs)

        lora_output = self.adapter_output(inputs)

        return (
            base_output
            + self.scaling * lora_output
        )

    def delta_weight(self) -> Tensor:
        """
        Materialize the effective LoRA weight update:

            ΔW = scaling * BA
        """

        return (
            self.scaling
            * torch.matmul(
                self.lora_B,
                self.lora_A,
            )
        )

    def merged_weight(self) -> Tensor:
        """
        Return:

            W' = W + ΔW

        without modifying the stored base weight.
        """

        return (
            self.base.weight.detach()
            + self.delta_weight().detach()
        )

    def parameter_summary(
        self,
    ) -> LoRAParameterSummary:
        base_parameters = sum(
            parameter.numel()
            for parameter in self.base.parameters()
        )

        adapter_parameters = (
            self.lora_A.numel()
            + self.lora_B.numel()
        )

        total_parameters = sum(
            parameter.numel()
            for parameter in self.parameters()
        )

        trainable_parameters = sum(
            parameter.numel()
            for parameter in self.parameters()
            if parameter.requires_grad
        )

        return LoRAParameterSummary(
            base_parameters=base_parameters,
            adapter_parameters=adapter_parameters,
            trainable_parameters=trainable_parameters,
            total_parameters=total_parameters,
        )

    def merged_forward(
        self,
        inputs: Tensor,
    ) -> Tensor:
        """
        Compute inference using the mathematically merged weight.

        This does not permanently mutate the base model.
        """

        return F.linear(
            inputs,
            self.merged_weight(),
            self.base.bias,
        )