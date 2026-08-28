from rag.evaluation.benchmark import (
    RAGBenchmark,
)
from rag.evaluation.dataset import (
    EvaluationDataset,
)
from rag.evaluation.contracts import (
    EvaluationCase,
)
from rag.evaluation.evaluator import (
    RAGEvaluator,
)


class FakePipeline:
    def answer(
        self,
        query: str,
    ) -> str:
        if query == "Question one":
            return "Answer one"

        return "Answer two"


def test_benchmark_runs_all_cases():
    dataset = EvaluationDataset(
        cases=[
            EvaluationCase(
                query="Question one",
                expected_answer="Answer one",
                retrieved_documents=[],
                generated_answer="",
            ),
            EvaluationCase(
                query="Question two",
                expected_answer="Answer two",
                retrieved_documents=[],
                generated_answer="",
            ),
        ]
    )

    benchmark = RAGBenchmark(
        pipeline=FakePipeline(),
        evaluator=RAGEvaluator(),
    )

    result = benchmark.run(dataset)

    assert len(result.results) == 2


def test_benchmark_calculates_average():
    dataset = EvaluationDataset(
        cases=[
            EvaluationCase(
                query="Question one",
                expected_answer="Answer one",
                retrieved_documents=[],
                generated_answer="",
            ),
        ]
    )

    benchmark = RAGBenchmark(
        pipeline=FakePipeline(),
        evaluator=RAGEvaluator(),
    )

    result = benchmark.run(dataset)

    assert result.average_score > 0.0