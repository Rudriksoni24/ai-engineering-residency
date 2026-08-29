from graphrag.comparison.contracts import (
    ComparisonCase,
    ComparisonResult,
    RetrievalSystem,
    SystemEvaluation,
)
from graphrag.comparison.metrics import (
    keyword_coverage,
)


class RetrievalComparator:

    def __init__(
        self,
        vector_system: RetrievalSystem,
        graph_system: RetrievalSystem,
    ) -> None:

        self.vector_system = (
            vector_system
        )

        self.graph_system = (
            graph_system
        )

    def compare(
        self,
        case: ComparisonCase,
    ) -> ComparisonResult:

        vector_output = (
            self.vector_system.answer(
                case.query
            )
        )

        graph_output = (
            self.graph_system.answer(
                case.query
            )
        )

        vector_evaluation = (
            self._evaluate(
                case,
                vector_output,
            )
        )

        graph_evaluation = (
            self._evaluate(
                case,
                graph_output,
            )
        )

        return ComparisonResult(
            case=case,
            vector=vector_evaluation,
            graph=graph_evaluation,
        )

    def compare_many(
        self,
        cases: list[
            ComparisonCase
        ],
    ) -> list[ComparisonResult]:

        return [
            self.compare(case)
            for case in cases
        ]

    @staticmethod
    def _evaluate(
        case,
        output,
    ) -> SystemEvaluation:

        coverage = keyword_coverage(
            expected_answer=(
                case.expected_answer
            ),
            actual_answer=(
                output.answer
            ),
        )

        return SystemEvaluation(
            output=output,
            keyword_coverage=coverage,
            retrieval_success=(
                output
                .retrieved_evidence_count
                > 0
            ),
        )