import pytest

from local_llm.model_analysis.memory_estimator import (
    estimate_memory_from_parameters,
)


def test_estimate_fp32_memory():
    memory = estimate_memory_from_parameters(
        parameters_billion=1,
        bits_per_parameter=32,
    )

    assert memory == pytest.approx(3.725, rel=0.01)


def test_estimate_fp16_memory():
    memory = estimate_memory_from_parameters(
        parameters_billion=1,
        bits_per_parameter=16,
    )

    assert memory == pytest.approx(1.863, rel=0.01)


def test_estimate_q4_memory():
    memory = estimate_memory_from_parameters(
        parameters_billion=1,
        bits_per_parameter=4,
    )

    assert memory == pytest.approx(0.466, rel=0.01)