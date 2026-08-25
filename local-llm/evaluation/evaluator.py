import json

from benchmarks.benchmark_types import (
    BenchmarkCase,
    BenchmarkResult,
)


def evaluate(
    case: BenchmarkCase,
    result: BenchmarkResult,
) -> BenchmarkResult:
    output_lower = result.output.lower()

    if case.expected_keywords:
        matches = sum(
            keyword.lower() in output_lower
            for keyword in case.expected_keywords
        )

        result.keyword_score = (
            matches / len(case.expected_keywords)
        )

    if case.expects_json:
        try:
            json.loads(result.output)
            result.valid_json = True
        except json.JSONDecodeError:
            result.valid_json = False

    return result