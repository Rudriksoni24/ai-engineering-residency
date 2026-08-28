from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class EvaluationCase:
    query: str
    expected_answer: str
    retrieved_documents: Sequence[str]
    generated_answer: str


@dataclass(frozen=True)
class MetricResult:
    name: str
    score: float
    details: str = ""


@dataclass(frozen=True)
class EvaluationResult:
    case: EvaluationCase
    metrics: Sequence[MetricResult]

    @property
    def average_score(self) -> float:
        if not self.metrics:
            return 0.0

        return sum(metric.score for metric in self.metrics) / len(
            self.metrics
        )