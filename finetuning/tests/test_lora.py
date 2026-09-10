import torch
from torch.nn import functional as F

from finetuning.lora.linear import LoRALinear


def test_base_parameters_are_frozen() -> None:
    layer = LoRALinear(
        in_features=4,
        out_features=3,
        rank=2,
    )

    assert layer.base.weight.requires_grad is False

    assert layer.base.bias is not None
    assert layer.base.bias.requires_grad is False


def test_lora_parameters_are_trainable() -> None:
    layer = LoRALinear(
        in_features=4,
        out_features=3,
        rank=2,
    )

    assert layer.lora_A.requires_grad is True
    assert layer.lora_B.requires_grad is True


def test_lora_parameter_shapes_are_correct() -> None:
    layer = LoRALinear(
        in_features=8,
        out_features=6,
        rank=2,
    )

    assert layer.lora_A.shape == (2, 8)
    assert layer.lora_B.shape == (6, 2)

    assert layer.delta_weight().shape == (6, 8)


def test_output_shape_matches_linear_layer() -> None:
    layer = LoRALinear(
        in_features=4,
        out_features=3,
        rank=2,
    )

    inputs = torch.randn(5, 4)

    output = layer(inputs)

    assert output.shape == (5, 3)


def test_zero_initialized_adapter_preserves_base_output() -> None:
    torch.manual_seed(42)

    layer = LoRALinear(
        in_features=4,
        out_features=3,
        rank=2,
        alpha=2.0,
    )

    inputs = torch.randn(5, 4)

    base_output = layer.base(inputs)

    lora_output = layer(inputs)

    assert torch.equal(
        base_output,
        lora_output,
    )


def test_delta_weight_is_zero_at_initialization() -> None:
    layer = LoRALinear(
        in_features=4,
        out_features=3,
        rank=2,
    )

    delta = layer.delta_weight()

    assert torch.equal(
        delta,
        torch.zeros_like(delta),
    )


def test_trainable_parameter_count_is_smaller_than_full_weight() -> None:
    layer = LoRALinear(
        in_features=128,
        out_features=128,
        rank=4,
        bias=False,
    )

    summary = layer.parameter_summary()

    full_fine_tuning_parameters = (
        layer.in_features
        * layer.out_features
    )

    assert (
        summary.trainable_parameters
        == summary.adapter_parameters
    )

    assert (
        summary.adapter_parameters
        < full_fine_tuning_parameters
    )


def test_only_adapter_parameters_receive_gradients() -> None:
    torch.manual_seed(42)

    layer = LoRALinear(
        in_features=4,
        out_features=3,
        rank=2,
    )

    inputs = torch.randn(5, 4)

    output = layer(inputs)

    loss = output.pow(2).mean()

    loss.backward()

    assert layer.base.weight.grad is None

    assert layer.base.bias is not None
    assert layer.base.bias.grad is None

    assert layer.lora_B.grad is not None

    # Because B starts at zero, the first gradient reaching A
    # is expected to be zero.
    assert layer.lora_A.grad is not None
    assert torch.equal(
        layer.lora_A.grad,
        torch.zeros_like(layer.lora_A.grad),
    )


def test_adapter_update_changes_model_output() -> None:
    torch.manual_seed(42)

    layer = LoRALinear(
        in_features=4,
        out_features=3,
        rank=2,
        alpha=2.0,
    )

    optimizer = torch.optim.SGD(
        [
            layer.lora_A,
            layer.lora_B,
        ],
        lr=0.1,
    )

    inputs = torch.randn(8, 4)

    targets = torch.randn(8, 3)

    output_before = layer(inputs).detach().clone()

    for _ in range(5):
        optimizer.zero_grad()

        output = layer(inputs)

        loss = F.mse_loss(
            output,
            targets,
        )

        loss.backward()

        optimizer.step()

    output_after = layer(inputs).detach()

    assert not torch.equal(
        output_before,
        output_after,
    )


def test_base_weights_do_not_change_after_adapter_training() -> None:
    torch.manual_seed(42)

    layer = LoRALinear(
        in_features=4,
        out_features=3,
        rank=2,
        alpha=2.0,
    )

    base_weight_before = (
        layer.base.weight
        .detach()
        .clone()
    )

    base_bias_before = (
        layer.base.bias
        .detach()
        .clone()
        if layer.base.bias is not None
        else None
    )

    optimizer = torch.optim.SGD(
        [
            layer.lora_A,
            layer.lora_B,
        ],
        lr=0.1,
    )

    inputs = torch.randn(8, 4)
    targets = torch.randn(8, 3)

    for _ in range(5):
        optimizer.zero_grad()

        output = layer(inputs)

        loss = F.mse_loss(
            output,
            targets,
        )

        loss.backward()

        optimizer.step()

    assert torch.equal(
        base_weight_before,
        layer.base.weight.detach(),
    )

    if base_bias_before is not None:
        assert layer.base.bias is not None

        assert torch.equal(
            base_bias_before,
            layer.base.bias.detach(),
        )


def test_merged_and_unmerged_forward_are_equivalent() -> None:
    torch.manual_seed(42)

    layer = LoRALinear(
        in_features=4,
        out_features=3,
        rank=2,
        alpha=2.0,
    )

    with torch.no_grad():
        layer.lora_B.normal_()

    inputs = torch.randn(5, 4)

    unmerged_output = layer(inputs)

    merged_output = layer.merged_forward(inputs)

    assert torch.allclose(
        unmerged_output,
        merged_output,
        atol=1e-6,
    )


def test_scaling_is_alpha_divided_by_rank() -> None:
    layer = LoRALinear(
        in_features=8,
        out_features=8,
        rank=4,
        alpha=16.0,
    )

    assert layer.scaling == 4.0