import time
from benchmarks.benchmark_types import (
    BenchmarkCase,
    BenchmarkResult,
)
from runtime.runtime_types import GenerationRequest


class BenchmarkRunner:

    def __init__(
        self,
        runtime,
        runtime_name: str,
    ):
        self.runtime = runtime
        self.runtime_name = runtime_name

    def run(
        self,
        case: BenchmarkCase,
        model: str,
    ) -> BenchmarkResult:
        # Construct the strongly-typed GenerationRequest contract required by the runtime
        request = GenerationRequest(
            prompt=case.prompt,
            model=model,
            max_tokens=getattr(case, "max_tokens", 512),
            temperature=getattr(case, "temperature", 0.7),
            top_p=getattr(case, "top_p", None),
            seed=getattr(case, "seed", None),
        )

        start = time.perf_counter()
        
        # Execute using the unified runtime contract
        response = self.runtime.generate(request)
        
        end = time.perf_counter()

        return BenchmarkResult(
            case_name=case.name,
            model=model,
            runtime=self.runtime_name,
            latency_seconds=end - start,
            output=response.text,
        )
