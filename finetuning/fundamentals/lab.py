from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import Tensor, nn


@dataclass(frozen=True)
class ParameterSummary:
    total_parameters: int
    trainable_parameters: int
    frozen_parameters: int

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
class MemoryEstimate:
    model_weight_bytes: int
    gradient_bytes: int
    optimizer_state_bytes: int

    @property
    def estimated_training_state_bytes(self) -> int:
        return (
            self.model_weight_bytes
            + self.gradient_bytes
            + self.optimizer_state_bytes
        )


@dataclass(frozen=True)
class ParameterState:
    name: str
    parameter_count: int
    trainable: bool


@dataclass(frozen=True)
class TrainingStepResult:
    loss_before_update: float
    trainable_parameters_changed: bool
    frozen_parameters_changed: bool


class TinyClassifier(nn.Module):
    """
    Small neural network used only to demonstrate fine-tuning mechanics.

    This model is intentionally tiny. It is a concept demonstration,
    not an approximation of production LLM fine-tuning workloads.
    """

    def __init__(
        self,
        input_size: int = 4,
        hidden_size: int = 8,
        number_of_classes: int = 2,
    ) -> None:
        super().__init__()

        self.feature_layer = nn.Linear(
            input_size,
            hidden_size,
        )

        self.activation = nn.ReLU()

        self.output_layer = nn.Linear(
            hidden_size,
            number_of_classes,
        )

    def forward(self, inputs: Tensor) -> Tensor:
        hidden = self.feature_layer(inputs)
        activated = self.activation(hidden)
        return self.output_layer(activated)


def count_parameters(model: nn.Module) -> ParameterSummary:
    total_parameters = sum(
        parameter.numel()
        for parameter in model.parameters()
    )

    trainable_parameters = sum(
        parameter.numel()
        for parameter in model.parameters()
        if parameter.requires_grad
    )

    return ParameterSummary(
        total_parameters=total_parameters,
        trainable_parameters=trainable_parameters,
        frozen_parameters=(
            total_parameters - trainable_parameters
        ),
    )


def inspect_parameter_states(
    model: nn.Module,
) -> list[ParameterState]:
    return [
        ParameterState(
            name=name,
            parameter_count=parameter.numel(),
            trainable=parameter.requires_grad,
        )
        for name, parameter in model.named_parameters()
    ]


def freeze_module(module: nn.Module) -> None:
    for parameter in module.parameters():
        parameter.requires_grad = False


def unfreeze_module(module: nn.Module) -> None:
    for parameter in module.parameters():
        parameter.requires_grad = True


def estimate_training_memory(
    model: nn.Module,
    bytes_per_parameter: int = 4,
    optimizer_state_tensors: int = 2,
) -> MemoryEstimate:
    """
    Estimate core parameter-related training memory.

    The calculation intentionally excludes activation memory because
    activations depend on batch size, input shape, network structure,
    sequence length, and implementation details.

    Assumptions for the default estimate:

    - FP32 weights: 4 bytes per parameter
    - FP32 gradient per trainable parameter
    - Adam-like optimizer with two parameter-sized state tensors

    This is an educational approximation, not a runtime memory profiler.
    """

    if bytes_per_parameter <= 0:
        raise ValueError(
            "bytes_per_parameter must be greater than zero"
        )

    if optimizer_state_tensors < 0:
        raise ValueError(
            "optimizer_state_tensors cannot be negative"
        )

    summary = count_parameters(model)

    model_weight_bytes = (
        summary.total_parameters
        * bytes_per_parameter
    )

    gradient_bytes = (
        summary.trainable_parameters
        * bytes_per_parameter
    )

    optimizer_state_bytes = (
        summary.trainable_parameters
        * bytes_per_parameter
        * optimizer_state_tensors
    )

    return MemoryEstimate(
        model_weight_bytes=model_weight_bytes,
        gradient_bytes=gradient_bytes,
        optimizer_state_bytes=optimizer_state_bytes,
    )


def clone_named_parameters(
    model: nn.Module,
) -> dict[str, Tensor]:
    return {
        name: parameter.detach().clone()
        for name, parameter in model.named_parameters()
    }


def parameters_changed(
    before: dict[str, Tensor],
    model: nn.Module,
    *,
    trainable: bool,
) -> bool:
    relevant_parameters = [
        (name, parameter)
        for name, parameter in model.named_parameters()
        if parameter.requires_grad is trainable
    ]

    if not relevant_parameters:
        return False

    return any(
        not torch.equal(
            before[name],
            parameter.detach(),
        )
        for name, parameter in relevant_parameters
    )


def run_single_supervised_step(
    model: nn.Module,
    inputs: Tensor,
    targets: Tensor,
    learning_rate: float = 0.05,
) -> TrainingStepResult:
    """
    Perform exactly one supervised optimization step.

    The function is deliberately explicit so the mechanics of
    fine-tuning remain visible.
    """

    if learning_rate <= 0:
        raise ValueError(
            "learning_rate must be greater than zero"
        )

    trainable_parameters = [
        parameter
        for parameter in model.parameters()
        if parameter.requires_grad
    ]

    if not trainable_parameters:
        raise ValueError(
            "model has no trainable parameters"
        )

    model.train()

    optimizer = torch.optim.SGD(
        trainable_parameters,
        lr=learning_rate,
    )

    loss_function = nn.CrossEntropyLoss()

    parameters_before = clone_named_parameters(model)

    # 1. Clear previous gradients.
    optimizer.zero_grad()

    # 2. Forward pass.
    logits = model(inputs)

    # 3. Calculate supervised loss.
    loss = loss_function(
        logits,
        targets,
    )

    # 4. Backpropagation computes gradients.
    loss.backward()

    # 5. Optimizer modifies trainable parameters.
    optimizer.step()

    trainable_changed = parameters_changed(
        parameters_before,
        model,
        trainable=True,
    )

    frozen_changed = parameters_changed(
        parameters_before,
        model,
        trainable=False,
    )

    return TrainingStepResult(
        loss_before_update=float(loss.detach().item()),
        trainable_parameters_changed=trainable_changed,
        frozen_parameters_changed=frozen_changed,
    )


def bytes_to_kib(number_of_bytes: int) -> float:
    return number_of_bytes / 1024


def bytes_to_mib(number_of_bytes: int) -> float:
    return number_of_bytes / (1024**2)