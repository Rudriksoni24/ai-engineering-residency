from local_llm.benchmarks.benchmark_types import (
    BenchmarkCase,
    BenchmarkResult,
)
from local_llm.evaluation.evaluator import evaluate


def test_keyword_evaluation():
    case = BenchmarkCase(
        name="test",
        prompt="test",
        expected_keywords=(
            "query",
            "key",
        ),
    )

    result = BenchmarkResult(
        case_name="test",
        model="test-model",
        runtime="fake",
        latency_seconds=1.0,
        output="A query interacts with a key.",
    )

    evaluated = evaluate(case, result)

    assert evaluated.keyword_score == 1.0


def test_json_evaluation():
    case = BenchmarkCase(
        name="json",
        prompt="test",
        expects_json=True,
    )

    result = BenchmarkResult(
        case_name="json",
        model="test-model",
        runtime="fake",
        latency_seconds=1.0,
        output='{"status": "ok"}',
    )

    evaluated = evaluate(case, result)

    assert evaluated.valid_json is True