from rag.evaluation.contracts import EvaluationCase
from rag.evaluation.evaluator import RAGEvaluator


def test_evaluator_returns_metrics():
    case = EvaluationCase(
        query="How are mismatches handled?",
        expected_answer="Mismatches must be investigated.",
        retrieved_documents=[
            "All transaction mismatches must be investigated."
        ],
        generated_answer=(
            "Transaction mismatches must be investigated."
        ),
    )

    evaluator = RAGEvaluator()

    result = evaluator.evaluate(case)

    assert len(result.metrics) == 2

    metric_names = {
        metric.name
        for metric in result.metrics
    }

    assert "keyword_recall" in metric_names
    assert "context_coverage" in metric_names


def test_evaluator_calculates_average_score():
    case = EvaluationCase(
        query="Question",
        expected_answer="Expected answer",
        retrieved_documents=[
            "Expected answer"
        ],
        generated_answer="Expected answer",
    )

    evaluator = RAGEvaluator()

    result = evaluator.evaluate(case)

    assert result.average_score == 1.0