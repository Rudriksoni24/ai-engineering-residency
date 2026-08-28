from dataclasses import dataclass
from typing import Any, Protocol

from rag.evaluation.contracts import (
    EvaluationCase,
    EvaluationResult,
)
from rag.evaluation.dataset import EvaluationDataset
from rag.evaluation.evaluator import RAGEvaluator


class AnsweringPipeline(Protocol):
    def answer(
        self,
        query: str,
    ) -> Any:
        ...


@dataclass(frozen=True)
class BenchmarkResult:
    results: list[EvaluationResult]

    @property
    def average_score(self) -> float:
        if not self.results:
            return 0.0

        return sum(
            result.average_score
            for result in self.results
        ) / len(self.results)


class RAGBenchmark:
    def __init__(
        self,
        pipeline: AnsweringPipeline,
        evaluator: RAGEvaluator,
    ) -> None:
        self.pipeline = pipeline
        self.evaluator = evaluator

    def run(
        self,
        dataset: EvaluationDataset,
    ) -> BenchmarkResult:
        results = []

        for dataset_case in dataset.cases:
            pipeline_response = self.pipeline.answer(
                dataset_case.query
            )

            generated_answer = getattr(
                pipeline_response,
                "answer",
                pipeline_response,
            )

            retrieved_documents = getattr(
                pipeline_response,
                "retrieved_documents",
                [],
            )

            case = EvaluationCase(
                query=dataset_case.query,
                expected_answer=dataset_case.expected_answer,
                retrieved_documents=retrieved_documents,
                generated_answer=generated_answer,
            )

            results.append(
                self.evaluator.evaluate(case)
            )

        return BenchmarkResult(
            results=results
        )