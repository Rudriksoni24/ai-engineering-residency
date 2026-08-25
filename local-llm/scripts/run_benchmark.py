from benchmarks.benchmark_runner import BenchmarkRunner
from evaluation.evaluator import evaluate
from evaluation.test_cases import BENCHMARK_CASES

from runtime.ollama_runtime import OllamaRuntime


MODEL = "qwen2.5:3b"


def main():
    runtime = OllamaRuntime()

    runner = BenchmarkRunner(
        runtime=runtime,
        runtime_name="ollama",
    )

    for case in BENCHMARK_CASES:
        result = runner.run(
            case=case,
            model=MODEL,
        )

        result = evaluate(
            case=case,
            result=result,
        )

        print("\n" + "=" * 60)
        print(f"CASE: {result.case_name}")
        print(f"LATENCY: {result.latency_seconds:.2f}s")
        print(f"KEYWORD SCORE: {result.keyword_score}")
        print(f"VALID JSON: {result.valid_json}")
        print("OUTPUT:")
        print(result.output)


if __name__ == "__main__":
    main()