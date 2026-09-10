import pytest
import torch

from finetuning.fundamentals.lab import (
    TinyClassifier,
    count_parameters,
    estimate_training_memory,
    freeze_module,
    inspect_parameter_states,
    run_single_supervised_step,
)


def test_all_parameters_are_trainable_initially() -> None:
    model = TinyClassifier()

    summary = count_parameters(model)

    assert summary.total_parameters > 0
    assert summary.trainable_parameters == summary.total_parameters
    assert summary.frozen_parameters == 0
    assert summary.trainable_percentage == pytest.approx(100.0)


def test_freezing_layer_reduces_trainable_parameter_count() -> None:
    model = TinyClassifier()

    before = count_parameters(model)

    freeze_module(model.feature_layer)

    after = count_parameters(model)

    assert after.total_parameters == before.total_parameters
    assert after.trainable_parameters < before.trainable_parameters
    assert after.frozen_parameters > 0


def test_parameter_state_identifies_trainable_and_frozen_parameters() -> None:
    model = TinyClassifier()

    freeze_module(model.feature_layer)

    states = {
        state.name: state
        for state in inspect_parameter_states(model)
    }

    assert states["feature_layer.weight"].trainable is False
    assert states["feature_layer.bias"].trainable is False

    assert states["output_layer.weight"].trainable is True
    assert states["output_layer.bias"].trainable is True


def test_memory_estimate_accounts_for_weights_gradients_and_optimizer() -> None:
    model = TinyClassifier()

    summary = count_parameters(model)

    estimate = estimate_training_memory(
        model,
        bytes_per_parameter=4,
        optimizer_state_tensors=2,
    )

    assert estimate.model_weight_bytes == (
        summary.total_parameters * 4
    )

    assert estimate.gradient_bytes == (
        summary.trainable_parameters * 4
    )

    assert estimate.optimizer_state_bytes == (
        summary.trainable_parameters * 4 * 2
    )

    assert estimate.estimated_training_state_bytes == (
        estimate.model_weight_bytes
        + estimate.gradient_bytes
        + estimate.optimizer_state_bytes
    )


def test_freezing_parameters_reduces_training_memory_estimate() -> None:
    model = TinyClassifier()

    full_estimate = estimate_training_memory(model)

    freeze_module(model.feature_layer)

    frozen_estimate = estimate_training_memory(model)

    assert (
        frozen_estimate.model_weight_bytes
        == full_estimate.model_weight_bytes
    )

    assert (
        frozen_estimate.gradient_bytes
        < full_estimate.gradient_bytes
    )

    assert (
        frozen_estimate.optimizer_state_bytes
        < full_estimate.optimizer_state_bytes
    )

    assert (
        frozen_estimate.estimated_training_state_bytes
        < full_estimate.estimated_training_state_bytes
    )


def test_one_supervised_step_changes_trainable_parameters() -> None:
    torch.manual_seed(42)

    model = TinyClassifier()

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

    result = run_single_supervised_step(
        model=model,
        inputs=inputs,
        targets=targets,
    )

    assert result.loss_before_update > 0
    assert result.trainable_parameters_changed is True
    assert result.frozen_parameters_changed is False


def test_frozen_parameters_do_not_change_during_training_step() -> None:
    torch.manual_seed(42)

    model = TinyClassifier()

    freeze_module(model.feature_layer)

    feature_weight_before = (
        model.feature_layer.weight
        .detach()
        .clone()
    )

    feature_bias_before = (
        model.feature_layer.bias
        .detach()
        .clone()
    )

    output_weight_before = (
        model.output_layer.weight
        .detach()
        .clone()
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

    result = run_single_supervised_step(
        model=model,
        inputs=inputs,
        targets=targets,
    )

    assert torch.equal(
        feature_weight_before,
        model.feature_layer.weight.detach(),
    )

    assert torch.equal(
        feature_bias_before,
        model.feature_layer.bias.detach(),
    )

    assert not torch.equal(
        output_weight_before,
        model.output_layer.weight.detach(),
    )

    assert result.trainable_parameters_changed is True
    assert result.frozen_parameters_changed is False


def test_training_step_fails_when_no_parameters_are_trainable() -> None:
    model = TinyClassifier()

    freeze_module(model)

    inputs = torch.randn(4, 4)
    targets = torch.tensor([0, 1, 0, 1])

    with pytest.raises(
        ValueError,
        match="model has no trainable parameters",
    ):
        run_single_supervised_step(
            model=model,
            inputs=inputs,
            targets=targets,
        )


def test_memory_estimator_rejects_invalid_precision() -> None:
    model = TinyClassifier()

    with pytest.raises(
        ValueError,
        match="bytes_per_parameter",
    ):
        estimate_training_memory(
            model,
            bytes_per_parameter=0,
        )