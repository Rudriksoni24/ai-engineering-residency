import pytest

from agents.evaluation.contracts import (
    AgentEvaluationResult,
)
from agents.evaluation.metrics import (
    summarize_results,
)


def test_empty_summary():
    summary = summarize_results(
        []
    )

    assert summary.total_cases == 0
    assert summary.passed_cases == 0
    assert summary.failed_cases == 0
    assert summary.pass_rate == 0.0
    assert summary.average_steps == 0.0


def test_summary_calculates_metrics():
    results = [
        AgentEvaluationResult(
            case_id="case-1",
            passed=True,
            answer="one",
            actual_tools=(
                "get_account",
            ),
            step_count=1,
            error=None,
            checks=(
                (
                    "expected_success",
                    True,
                ),
            ),
        ),
        AgentEvaluationResult(
            case_id="case-2",
            passed=False,
            answer="two",
            actual_tools=(
                "get_transaction",
                "get_account",
                "get_account",
            ),
            step_count=3,
            error=None,
            checks=(
                (
                    "expected_success",
                    True,
                ),
                (
                    "max_steps",
                    False,
                ),
            ),
        ),
    ]

    summary = summarize_results(
        results
    )

    assert summary.total_cases == 2
    assert summary.passed_cases == 1
    assert summary.failed_cases == 1

    assert summary.pass_rate == pytest.approx(
        0.5
    )

    assert (
        summary.average_steps
        == pytest.approx(2.0)
    )