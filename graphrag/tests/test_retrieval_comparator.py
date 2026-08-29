from graphrag.comparison.comparator import (
    RetrievalComparator,
)
from graphrag.comparison.contracts import (
    ComparisonCase,
    RetrievalOutput,
)


class FakeSystem:

    def __init__(
        self,
        name: str,
        answer_text: str,
        evidence_count: int,
        relationship_count: int = 0,
    ) -> None:

        self._name = name
        self.answer_text = (
            answer_text
        )
        self.evidence_count = (
            evidence_count
        )
        self.relationship_count = (
            relationship_count
        )

    @property
    def system_name(
        self,
    ) -> str:
        return self._name

    def answer(
        self,
        query: str,
    ) -> RetrievalOutput:

        return RetrievalOutput(
            system_name=self._name,
            answer=self.answer_text,
            retrieved_evidence_count=(
                self.evidence_count
            ),
            relationship_count=(
                self.relationship_count
            ),
            latency_ms=1.0,
        )


def test_compares_two_systems():

    vector = FakeSystem(
        name="vector_rag",
        answer_text=(
            "ACC001 initiated "
            "TXN9001."
        ),
        evidence_count=2,
    )

    graph = FakeSystem(
        name="graph_rag",
        answer_text=(
            "ACC001 initiated "
            "TXN9001."
        ),
        evidence_count=3,
        relationship_count=2,
    )

    comparator = RetrievalComparator(
        vector_system=vector,
        graph_system=graph,
    )

    result = comparator.compare(
        ComparisonCase(
            case_id="case-001",
            query=(
                "What transaction "
                "did ACC001 initiate?"
            ),
            expected_answer=(
                "ACC001 initiated "
                "TXN9001."
            ),
            query_type=(
                "relationship"
            ),
        )
    )

    assert (
        result.vector
        .keyword_coverage
        == 1.0
    )

    assert (
        result.graph
        .keyword_coverage
        == 1.0
    )

    assert (
        result.vector
        .retrieval_success
    )

    assert (
        result.graph
        .retrieval_success
    )


def test_failed_retrieval_is_detected():

    vector = FakeSystem(
        name="vector_rag",
        answer_text=(
            "I don't know."
        ),
        evidence_count=0,
    )

    graph = FakeSystem(
        name="graph_rag",
        answer_text=(
            "ACC001 initiated "
            "TXN9001."
        ),
        evidence_count=3,
        relationship_count=2,
    )

    comparator = RetrievalComparator(
        vector_system=vector,
        graph_system=graph,
    )

    result = comparator.compare(
        ComparisonCase(
            case_id="case-002",
            query=(
                "What transaction "
                "did ACC001 initiate?"
            ),
            expected_answer=(
                "ACC001 initiated "
                "TXN9001."
            ),
            query_type=(
                "relationship"
            ),
        )
    )

    assert not (
        result.vector
        .retrieval_success
    )

    assert (
        result.graph
        .retrieval_success
    )