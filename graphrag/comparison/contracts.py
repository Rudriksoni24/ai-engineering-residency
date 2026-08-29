from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ComparisonCase:
    case_id: str
    query: str
    expected_answer: str
    query_type: str


@dataclass(frozen=True)
class RetrievalOutput:
    system_name: str
    answer: str
    retrieved_evidence_count: int
    relationship_count: int
    latency_ms: float


@dataclass(frozen=True)
class SystemEvaluation:
    output: RetrievalOutput
    keyword_coverage: float
    retrieval_success: bool


@dataclass(frozen=True)
class ComparisonResult:
    case: ComparisonCase
    vector: SystemEvaluation
    graph: SystemEvaluation


class RetrievalSystem(Protocol):

    @property
    def system_name(
        self,
    ) -> str:
        ...

    def answer(
        self,
        query: str,
    ) -> RetrievalOutput:
        ...