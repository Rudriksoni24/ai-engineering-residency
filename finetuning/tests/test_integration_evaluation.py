import pytest

from finetuning.data.pipeline import (
    InstructionExample,
    format_instruction_prompt,
)
from finetuning.evaluation.comparison import (
    EvaluationCase,
    EvaluationResult,
    summarize_results,
)


def test_evaluation_case_accepts_valid_data() -> None:
    case = EvaluationCase(
        case_id="txn-001",
        prompt="Classify TXN-001.",
        expected_response="DECLINED",
    )

    case.validate()


def test_empty_evaluation_prompt_is_rejected() -> None:
    case = EvaluationCase(
        case_id="txn-001",
        prompt=" ",
        expected_response="DECLINED",
    )

    with pytest.raises(
        ValueError,
        match="prompt",
    ):
        case.validate()


def test_empty_expected_response_is_rejected() -> None:
    case = EvaluationCase(
        case_id="txn-001",
        prompt="Classify.",
        expected_response=" ",
    )

    with pytest.raises(
        ValueError,
        match="expected_response",
    ):
        case.validate()


def test_instruction_prompt_excludes_response() -> None:
    example = InstructionExample(
        instruction=(
            "Classify transaction status."
        ),
        input_text=(
            "Transaction TXN-1001 "
            "was declined."
        ),
        response=(
            '{"status":"DECLINED"}'
        ),
    )

    prompt = format_instruction_prompt(
        example,
        system_prompt=(
            "You are a banking assistant."
        ),
    )

    assert "### System" in prompt
    assert "### Instruction" in prompt
    assert "### Input" in prompt
    assert "### Response" in prompt

    assert (
        '{"status":"DECLINED"}'
        not in prompt
    )


def test_loss_delta_is_negative_when_adapted_improves() -> None:
    result = EvaluationResult(
        case_id="case-1",
        base_loss=3.0,
        adapted_loss=2.0,
    )

    assert (
        result.loss_delta
        == pytest.approx(-1.0)
    )

    assert result.improved is True


def test_summary_detects_overall_improvement() -> None:
    results = [
        EvaluationResult(
            case_id="a",
            base_loss=3.0,
            adapted_loss=2.0,
        ),
        EvaluationResult(
            case_id="b",
            base_loss=4.0,
            adapted_loss=3.5,
        ),
    ]

    summary = summarize_results(
        results
    )

    assert summary.case_count == 2
    assert summary.improved_cases == 2
    assert summary.regressed_cases == 0
    assert summary.unchanged_cases == 0

    assert (
        summary.average_base_loss
        == pytest.approx(3.5)
    )

    assert (
        summary.average_adapted_loss
        == pytest.approx(2.75)
    )

    assert (
        summary.average_loss_delta
        == pytest.approx(-0.75)
    )

    assert (
        summary.improved_overall
        is True
    )


def test_summary_can_report_mixed_results() -> None:
    results = [
        EvaluationResult(
            case_id="better",
            base_loss=3.0,
            adapted_loss=2.0,
        ),
        EvaluationResult(
            case_id="worse",
            base_loss=2.0,
            adapted_loss=3.0,
        ),
        EvaluationResult(
            case_id="same",
            base_loss=1.0,
            adapted_loss=1.0,
        ),
    ]

    summary = summarize_results(
        results
    )

    assert summary.improved_cases == 1
    assert summary.regressed_cases == 1
    assert summary.unchanged_cases == 1


def test_empty_evaluation_results_are_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="results cannot be empty",
    ):
        summarize_results(
            []
        )