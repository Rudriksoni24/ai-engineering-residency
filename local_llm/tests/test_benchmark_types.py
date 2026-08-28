from local_llm.benchmarks.benchmark_types import BenchmarkCase


def test_benchmark_case_defaults():
    case = BenchmarkCase(
        name="test",
        prompt="hello",
    )

    assert case.expected_keywords == ()
    assert case.expects_json is False