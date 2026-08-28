from rag.evaluation.contracts import (
    EvaluationCase,
    EvaluationResult,
    MetricResult,
)


def test_evaluation_result_average_score():
    case = EvaluationCase(
        query="How are mismatches handled?",
        expected_answer="Mismatches must be investigated.",
        retrieved_documents=[
            "All transaction mismatches must be investigated."
        ],
        generated_answer="Mismatches must be investigated.",
    )

    result = EvaluationResult(
        case=case,
        metrics=[
            MetricResult(
                name="metric_one",
                score=0.8,
            ),
            MetricResult(
                name="metric_two",
                score=1.0,
            ),
        ],
    )

    assert result.average_score == 0.9


def test_empty_metrics_have_zero_average():
    case = EvaluationCase(
        query="Question",
        expected_answer="Expected",
        retrieved_documents=[],
        generated_answer="Generated",
    )

    result = EvaluationResult(
        case=case,
        metrics=[],
    )

    assert result.average_score == 0.0